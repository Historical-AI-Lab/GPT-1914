"""substantive/drawbank.py — load, verify, and assemble the three draw banks.

Producers own their own draws (plan §2: no standalone refit scripts here).
This module never fits anything -- it loads what
fit_beta_regression_nocontext.py and bt_context_scoring.py calibrate/score
already wrote, checks their metadata agrees on every shared key, and hands
substantive.estimator plain numpy arrays.

Bank artifact schema (npz, written by the respective producer):
  beta draws   (substantive.artifacts.beta_draws_path)
    arrays: b0 (D,), b_len (D,), u_frame (D, K)
    meta:   frame_types (list[str], length K), standardization
            {mu_loglen, sd_loglen}, sigma_u, sigma_u_diagnostics, + base_meta
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
import math
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from . import artifacts
from .routing import Routing, route_questions

# frame_type inference mirrors fit_beta_regression_nocontext.py's
# _REASONING_TO_FRAME / _infer_frame_type: kept as a small local copy
# rather than importing that CLI script, since the mapping is stable and
# importing a top-level script module for three lines of logic is the
# more fragile coupling.
_REASONING_TO_FRAME = {
    "knowledge": "world_context", "refusal": "world_context", "inference": "world_context",
    "character_modeling": "book_context", "constrained_generation": "book_context",
    "topic_sentence": "book_context",
    "phrase_cloze": "passage_context", "sentence_cloze": "passage_context",
}


def _frame_type_of(rec: dict) -> str:
    return rec.get("frame_type") or _REASONING_TO_FRAME.get(rec.get("reasoning_type", ""), "")


def _gt_len(rec: dict) -> int:
    strings = rec.get("answer_strings") or []
    return max(len(strings[0]), 1) if strings else 1


class ArtifactMismatch(RuntimeError):
    """A shared meta key disagrees across draw banks being combined."""


# frame_types order is the silent killer (plan §4): u_frame is a bare
# (D, K) array, so a reordering mislabels every question's beta while
# everything still runs -- no override flag is offered for that reason.
COMPATIBILITY_KEYS = [
    "benchmark_version", "routing_basis", "prompt_mode", "prior_dist",
    "prior_df", "prior_scale", "judge_effort", "frame_types",
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
    both carry the key must agree. No override flag -- spec §8.9's whole
    point is that these fail loudly.
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
    """The pilot-pooling cluster-collision trap (plan §4): a bare qid like
    "3" means a different question in a different benchmark version, so
    clustering on it silently correlates two unrelated questions. Only
    fires when a meta carries `cluster_ids`: a list of [qid, benchmark_version]
    pairs, one per LOO record contributing to the calibration set (a plain
    {qid: version} dict cannot represent the collision itself, since pilot
    qid "3" and production qid "3" would overwrite one another as keys)."""
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
    qnums_pf: list          # binary-channel qnums, sorted, aligned to the arrays below
    v_hat: np.ndarray
    n_v: np.ndarray
    k_alpha: np.ndarray
    n_alpha: np.ndarray
    frame_idx: np.ndarray
    z_loglen: np.ndarray
    coef_b0: np.ndarray
    coef_b_len: np.ndarray
    coef_u_frame: np.ndarray
    sigma_u: float
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


def assemble(*, scored_file, benchmark_path, reliability_path,
            beta_draws_path, calib_draws_path, delta_draws_path,
            compatibility_keys: list[str] = COMPATIBILITY_KEYS) -> Bank:
    """Load every producer's output and hand back plain numpy arrays.

    Raises ArtifactMismatch (via verify_compatible) rather than silently
    combining artifacts fit under different instruments, and raises
    KeyError/ValueError on any routed question missing from a required
    input -- a scored-but-unrouted or routed-but-unscored question is a
    pipeline bug, not something to paper over (spec §8.9).
    """
    routing = route_questions(benchmark_path)

    scored = json.loads(Path(scored_file).read_text(encoding="utf-8"))
    question_fit = scored.get("question_fit", {})

    reliability = json.loads(Path(reliability_path).read_text(encoding="utf-8"))
    per_question_alpha = reliability.get("per_question", {})

    beta_arrays, beta_meta = artifacts.load_npz(beta_draws_path)
    calib_arrays, calib_meta = artifacts.load_npz(calib_draws_path)
    delta_arrays, delta_meta = artifacts.load_npz(delta_draws_path)

    verify_compatible(
        {"beta_draws": beta_meta, "calib_draws": calib_meta, "delta_draws": delta_meta},
        keys=compatibility_keys,
    )

    frame_types = list(beta_meta["frame_types"])
    frame_index = {f: i for i, f in enumerate(frame_types)}
    mu_loglen = beta_meta["standardization"]["mu_loglen"]
    sd_loglen = beta_meta["standardization"]["sd_loglen"]

    qnums_pf = sorted(routing.pass_fail, key=int)
    v_hat, n_v, k_alpha, n_alpha, frame_idx, z_loglen = [], [], [], [], [], []
    auto_pf = []
    for qnum in qnums_pf:
        if qnum not in question_fit:
            raise KeyError(f"pass/fail question {qnum} routed but not present in {scored_file}")
        if qnum not in per_question_alpha:
            raise KeyError(f"pass/fail question {qnum} routed but missing alpha reliability "
                           f"in {reliability_path}")
        scores = question_fit[qnum]["scores"]
        v_hat.append(float(np.mean(scores)))
        n_v.append(len(scores))
        # An automatic verdict is a certainty, not a noisy judge reading, so it
        # bypasses Rogan-Gladen downstream rather than being corrected by it.
        _auto = question_fit[qnum].get("auto_verdict")
        auto_pf.append(1.0 if _auto == "gt_identity"
                       else 0.0 if _auto == "distractor_identity"
                       else np.nan)
        alpha_rec = per_question_alpha[qnum]
        # alpha's k is the ERROR count, not the correct count: the Beta
        # posterior models P(judge wrongly passes a distractor), and the
        # reliability file's question_correct measures the opposite event
        # (correct rejections). See spec Sec8.5: k=0 (a perfect judge, zero
        # errors) gives the low Jeffreys mean 0.125 at n=6, not a high one.
        n_total = alpha_rec["question_total"]
        n_correct = alpha_rec["question_correct"]
        k_alpha.append(n_total - n_correct)
        n_alpha.append(n_total)
        rec = routing.pass_fail[qnum]
        frame = _frame_type_of(rec)
        if frame not in frame_index:
            raise ValueError(f"question {qnum}: frame_type {frame!r} not in beta bank's "
                             f"frame_types {frame_types}")
        frame_idx.append(frame_index[frame])
        z_loglen.append((math.log(_gt_len(rec)) - mu_loglen) / sd_loglen)

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
        routing=routing, qnums_pf=qnums_pf,
        v_hat=np.array(v_hat, dtype=float), n_v=np.array(n_v, dtype=float),
        k_alpha=np.array(k_alpha, dtype=float), n_alpha=np.array(n_alpha, dtype=float),
        frame_idx=np.array(frame_idx, dtype=int), z_loglen=np.array(z_loglen, dtype=float),
        coef_b0=beta_arrays["b0"], coef_b_len=beta_arrays["b_len"],
        coef_u_frame=beta_arrays["u_frame"], sigma_u=float(beta_meta["sigma_u"]),
        qnums_pc=qnums_pc, delta_draws=delta_draws,
        cal_a=calib_arrays["cal_a"], cal_b=calib_arrays["cal_b"],
        auto_pf=np.array(auto_pf, dtype=float), auto_pc=np.array(auto_pc, dtype=float),
        metas={"beta_draws": beta_meta, "calib_draws": calib_meta, "delta_draws": delta_meta},
    )


def provenance(bank: Bank) -> dict:
    """Merged source_artifacts across every bank that produced this Bank."""
    merged: dict = {}
    for role, meta in bank.metas.items():
        merged[role] = {k: meta.get(k) for k in
                        ("produced_by", "produced_at", "git_head", "source_artifacts") if k in meta}
    return merged


def freeze(bank: Bank, path) -> None:
    """Write one self-describing archival npz: every draw set, alpha
    counts, verdicts, and merged provenance, so a published number
    reproduces bit-for-bit after the producing artifacts move (plan §4).

    reasoning_pf / reasoning_pc carry each question's reasoning_type,
    positionally aligned to qnums_pf / qnums_pc, so the reasoning-type
    breakdown (substantive/groups.py) still works when scoring is redone
    from a frozen bank -- without them load_frozen's stub records would
    have nothing for groups.group_of to read.
    """
    arrays = {
        "v_hat": bank.v_hat, "n_v": bank.n_v, "k_alpha": bank.k_alpha, "n_alpha": bank.n_alpha,
        "frame_idx": bank.frame_idx, "z_loglen": bank.z_loglen,
        "coef_b0": bank.coef_b0, "coef_b_len": bank.coef_b_len, "coef_u_frame": bank.coef_u_frame,
        "delta_draws": bank.delta_draws, "cal_a": bank.cal_a, "cal_b": bank.cal_b,
        "auto_pf": bank.auto_pf, "auto_pc": bank.auto_pc,
    }
    reasoning_pf = [bank.routing.pass_fail[q].get("reasoning_type") for q in bank.qnums_pf]
    reasoning_pc = [bank.routing.partial[q].get("reasoning_type") for q in bank.qnums_pc]
    meta = artifacts.base_meta(
        produced_by="substantive.drawbank.freeze",
        routing_basis=bank.routing.basis, sigma_u=bank.sigma_u,
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
        routing=routing, qnums_pf=list(meta["qnums_pf"]),
        v_hat=arrays["v_hat"], n_v=arrays["n_v"],
        k_alpha=arrays["k_alpha"], n_alpha=arrays["n_alpha"],
        frame_idx=arrays["frame_idx"], z_loglen=arrays["z_loglen"],
        coef_b0=arrays["coef_b0"], coef_b_len=arrays["coef_b_len"],
        coef_u_frame=arrays["coef_u_frame"], sigma_u=float(meta["sigma_u"]),
        qnums_pc=list(meta["qnums_pc"]), delta_draws=arrays["delta_draws"],
        cal_a=arrays["cal_a"], cal_b=arrays["cal_b"],
        # Banks frozen before automatic verdicts existed carry neither array;
        # all-NaN is exactly "nothing was short-circuited", so they reproduce.
        auto_pf=arrays["auto_pf"] if "auto_pf" in arrays
                else np.full(len(meta["qnums_pf"]), np.nan),
        auto_pc=arrays["auto_pc"] if "auto_pc" in arrays
                else np.full(len(meta["qnums_pc"]), np.nan),
        metas=meta.get("source_metas", {}),
    )
