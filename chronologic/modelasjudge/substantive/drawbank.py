"""substantive/drawbank.py — load, verify, and assemble the two draw banks.

Producers own their own draws (plan §2: no standalone refit scripts here).
This module never fits anything -- it loads what
bt_context_scoring.py calibrate/score already wrote, checks their metadata
agrees on every shared key, and hands substantive.estimator plain numpy
arrays.

Only two banks feed a candidate's score now (direct-binary-scoring-spec.md
§1-§4): the binary channel is the raw judge verdict, computed straight from
the scored-answers file with no correction and no reliability/beta
artifacts as a dependency. The alpha-reliability JSON and beta draw bank
are judge-validation inputs -- see substantive/judge_validation.py and
judge_validation_report.py -- and are never loaded here.

Bank artifact schema (npz, written by the respective producer):
  calibration draws (substantive.artifacts.calib_draws_path)
    arrays: cal_a (C,), cal_b (C,)
    meta:   bt_tag, prior_scale, prior_dist, prior_df, prompt_mode,
            reference_policy, cluster_ids ({qid: benchmark_version}), + base_meta
  Delta draws  (substantive.artifacts.delta_draws_path)
    arrays: delta__{qid} (n_delta_draws,) per BT-routed question, all the
            same length; c_len__{qid} scalar (candidate answer length, for
            the optional length covariate)
    meta:   bt_tag, candidate_label, candidate_effort, reference_policy, + base_meta
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from . import artifacts
from .routing import Routing, route_questions


class ArtifactMismatch(RuntimeError):
    """A shared meta key disagrees across draw banks being combined."""


COMPATIBILITY_KEYS = [
    "benchmark_version", "routing_basis", "prompt_mode", "prior_dist",
    "prior_df", "prior_scale", "judge_effort",
    # The calibration design. Delta draws are pre-calibration, but cmd_score
    # stamps the design it scored against onto them, so a scored file built on
    # the anchored curve cannot be combined with draws fit under a free
    # intercept -- the two put ground-truth parity at 0.90 and 0.345.
    "pin_p", "class_balance",
]


def verify_compatible(metas: dict[str, dict], keys: list[str] = COMPATIBILITY_KEYS) -> None:
    """Raise ArtifactMismatch if any of `keys` disagrees across `metas`.

    metas: {role: meta_dict}. A key absent from a given meta is ignored for
    that role (older artifacts may predate a field); any two roles that
    both carry the key must agree. No override flag -- these fail loudly.
    """
    for key in keys:
        seen = {role: meta[key] for role, meta in metas.items() if key in meta}
        values = list(seen.values())
        if len(values) > 1 and any(v != values[0] for v in values):
            raise ArtifactMismatch(
                f"{key!r} disagrees across artifacts: "
                + ", ".join(f"{role}={val!r}" for role, val in seen.items())
            )
    _assert_cluster_ids_single_version(metas)


def _assert_cluster_ids_single_version(metas: dict[str, dict]) -> None:
    """The pilot-pooling cluster-collision trap: a bare qid like "3" means a
    different question in a different benchmark version, so clustering on
    it silently correlates two unrelated questions. Only fires when a meta
    carries `cluster_ids`: a list of [qid, benchmark_version] pairs, one per
    LOO record contributing to the calibration set (a plain {qid: version}
    dict cannot represent the collision itself, since pilot qid "3" and
    production qid "3" would overwrite one another as keys)."""
    for role, meta in metas.items():
        cluster_ids = meta.get("cluster_ids")
        if not cluster_ids:
            continue
        by_qid: dict[str, set] = {}
        for qid, version in cluster_ids:
            by_qid.setdefault(qid, set()).add(version)
        bad = {q: sorted(v) for q, v in by_qid.items() if len(v) > 1}
        if bad:
            raise ArtifactMismatch(
                f"{role}: cluster id(s) resolve to more than one benchmark version: {bad}"
            )


@dataclass
class Bank:
    routing: Routing
    qnums_pf: list          # binary-channel qnums, sorted, aligned to v_hat
    v_hat: np.ndarray
    qnums_pc: list          # BT-channel qnums, sorted, aligned to delta_draws rows
    delta_draws: np.ndarray
    cal_a: np.ndarray
    cal_b: np.ndarray
    # Automatic verdicts: 1.0 or 0.0 where a candidate answer was verbatim
    # identical to a ground truth or to a probability-0 distractor, NaN where
    # the question was actually judged. Aligned to qnums_pf / qnums_pc. All-NaN
    # for any artifact written before automatic verdicts existed, which is what
    # makes those artifacts reproduce their old numbers exactly.
    auto_pf: np.ndarray = field(default_factory=lambda: np.zeros(0))
    auto_pc: np.ndarray = field(default_factory=lambda: np.zeros(0))
    metas: dict = field(default_factory=dict)   # role -> meta dict
    benchmark_version: str = ""


def assemble(*, scored_file, benchmark_path, calib_draws_path, delta_draws_path,
            benchmark_version, compatibility_keys: list[str] = COMPATIBILITY_KEYS) -> Bank:
    """Load every producer's output and hand back plain numpy arrays.

    Raises ArtifactMismatch (via verify_compatible) rather than silently
    combining artifacts fit under different instruments, and raises
    KeyError/ValueError on any routed question missing from a required
    input -- a scored-but-unrouted or routed-but-unscored question is a
    pipeline bug, not something to paper over.
    """
    routing = route_questions(benchmark_path)

    scored = json.loads(Path(scored_file).read_text(encoding="utf-8"))
    question_fit = scored.get("question_fit", {})

    calib_arrays, calib_meta = artifacts.load_npz(calib_draws_path)
    delta_arrays, delta_meta = artifacts.load_npz(delta_draws_path)

    verify_compatible(
        {"calib_draws": calib_meta, "delta_draws": delta_meta},
        keys=compatibility_keys,
    )

    qnums_pf = sorted(routing.pass_fail, key=int)
    v_hat, auto_pf = [], []
    for qnum in qnums_pf:
        if qnum not in question_fit:
            raise KeyError(f"pass/fail question {qnum} routed but not present in {scored_file}")
        scores = question_fit[qnum]["scores"]
        v_hat.append(float(np.mean(scores)))
        # An automatic verdict is a certainty, not a noisy judge reading, so it
        # overrides the observed v_q rather than being folded into it -- though
        # v_q already equals the override today (judge_scoring_nocontext.py
        # writes scores=[1]/[0] for these questions), so this is a documented
        # no-op on this channel.
        _auto = question_fit[qnum].get("auto_verdict")
        auto_pf.append(1.0 if _auto == "gt_identity"
                       else 0.0 if _auto == "distractor_identity"
                       else np.nan)

    qnums_pc = sorted(routing.partial, key=int)
    delta_rows = []
    auto_pc = []
    n_delta_draws = None
    for qnum in qnums_pc:
        key = f"delta__{qnum}"
        if key not in delta_arrays:
            raise KeyError(f"BT question {qnum} routed but missing {key!r} in {delta_draws_path}")
        row = delta_arrays[key]
        auto_pc.append(float(delta_arrays[f"auto__{qnum}"])
                       if f"auto__{qnum}" in delta_arrays else np.nan)
        if n_delta_draws is None:
            n_delta_draws = row.shape[0]
        elif row.shape[0] != n_delta_draws:
            raise ValueError(f"question {qnum}: {row.shape[0]} Delta draws, "
                             f"expected {n_delta_draws} (all questions must match)")
        delta_rows.append(row)
    delta_draws = (np.stack(delta_rows) if delta_rows
                  else np.zeros((0, n_delta_draws or 0), dtype=float))

    return Bank(
        routing=routing, qnums_pf=qnums_pf, v_hat=np.array(v_hat, dtype=float),
        qnums_pc=qnums_pc, delta_draws=delta_draws,
        cal_a=calib_arrays["cal_a"], cal_b=calib_arrays["cal_b"],
        auto_pf=np.array(auto_pf, dtype=float), auto_pc=np.array(auto_pc, dtype=float),
        metas={"calib_draws": calib_meta, "delta_draws": delta_meta},
        benchmark_version=benchmark_version,
    )


def provenance(bank: Bank) -> dict:
    """Merged source_artifacts across every bank that produced this Bank."""
    merged: dict = {}
    for role, meta in bank.metas.items():
        merged[role] = {k: meta.get(k) for k in
                        ("produced_by", "produced_at", "git_head", "source_artifacts") if k in meta}
    return merged


def freeze(bank: Bank, path) -> None:
    """Write one self-describing archival npz: every draw set, verdicts,
    and merged provenance, so a published number reproduces bit-for-bit
    after the producing artifacts move.

    reasoning_pf / reasoning_pc carry each question's reasoning_type,
    positionally aligned to qnums_pf / qnums_pc, so the reasoning-type
    breakdown (substantive/groups.py) still works when scoring is redone
    from a frozen bank -- without them load_frozen's stub records would
    have nothing for groups.group_of to read.
    """
    arrays = {
        "v_hat": bank.v_hat, "delta_draws": bank.delta_draws,
        "cal_a": bank.cal_a, "cal_b": bank.cal_b,
        "auto_pf": bank.auto_pf, "auto_pc": bank.auto_pc,
    }
    reasoning_pf = [bank.routing.pass_fail[q].get("reasoning_type") for q in bank.qnums_pf]
    reasoning_pc = [bank.routing.partial[q].get("reasoning_type") for q in bank.qnums_pc]
    meta = artifacts.base_meta(
        produced_by="substantive.drawbank.freeze",
        scoring_version="direct_binary_v1",
        routing_basis=bank.routing.basis, benchmark_version=bank.benchmark_version,
        qnums_pf=bank.qnums_pf, qnums_pc=bank.qnums_pc,
        reasoning_pf=reasoning_pf, reasoning_pc=reasoning_pc,
        source_metas=bank.metas,
    )
    artifacts.save_npz(path, arrays, meta)


def load_frozen(path) -> Bank:
    arrays, meta = artifacts.load_npz(path)
    if "reasoning_pf" not in meta or "reasoning_pc" not in meta:
        raise KeyError(
            f"{path}: frozen bank predates the reasoning-type breakdown "
            "(no reasoning_pf/reasoning_pc in meta) -- re-run "
            "`score_substantive.py score --freeze-bank ...` against the "
            "producing artifacts to regenerate it."
        )
    pass_fail = {q: {"reasoning_type": rt}
                 for q, rt in zip(meta["qnums_pf"], meta["reasoning_pf"])}
    partial = {q: {"reasoning_type": rt}
              for q, rt in zip(meta["qnums_pc"], meta["reasoning_pc"])}
    routing = Routing(basis=meta["routing_basis"], pass_fail=pass_fail, partial=partial)
    return Bank(
        routing=routing, qnums_pf=list(meta["qnums_pf"]), v_hat=arrays["v_hat"],
        qnums_pc=list(meta["qnums_pc"]), delta_draws=arrays["delta_draws"],
        cal_a=arrays["cal_a"], cal_b=arrays["cal_b"],
        # Banks frozen before automatic verdicts existed carry neither array;
        # all-NaN is exactly "nothing was short-circuited", so they reproduce.
        auto_pf=arrays["auto_pf"] if "auto_pf" in arrays
                else np.full(len(meta["qnums_pf"]), np.nan),
        auto_pc=arrays["auto_pc"] if "auto_pc" in arrays
                else np.full(len(meta["qnums_pc"]), np.nan),
        # RG-era arrays (k_alpha, n_alpha, coef_*, sigma_u, ...) are silently
        # ignored if present -- this scorer no longer reads them.
        metas=meta.get("source_metas", {}),
        benchmark_version=meta.get("benchmark_version", ""),
    )
