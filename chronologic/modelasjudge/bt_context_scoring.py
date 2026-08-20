"""bt_context_scoring.py — CLI for the PARTIAL-CREDIT scoring path.

Thin argparse wrapper over the bt/ package. See bt-context-judge-plan.md
and bradley/bradley-terry-spec.md for the full design, and
estimator_and_calibration_explained.md for how p_fit is produced and what
its scale means.

This is the richer of ChronoLogic's two scoring paths. Where
judge_scoring_nocontext.py returns a binary verdict on instruction following
and factual accuracy, this path resolves a continuous score by running a
Bradley-Terry round robin over the question's own answer options -- so it
covers a superset of those criteria, adding fit to the historical context.
(The rubric in bt/prompts.py still *asks* only about context fit; the superset
holds because the anchor pool contains every distractor, including
instruction-following failures like negation and same_book.)

Automatic verdicts: a candidate verbatim-identical to a ground truth scores
exactly 1.0, and one identical to any probability-0 distractor scores 0.0,
both without a single judge call (substantive/verdicts.py). Every
probability-0 distractor counts here, unlike on the pass/fail path, because
this path does measure period fidelity.

Subcommands
-----------
  anchor-fit   Fit the per-question Bradley-Terry anchor model for every
               context-scored question in a benchmark.
  loo          Leave-one-out: score every answer option as if it were a
               candidate, reusing the anchor comparisons already collected.
  validate     Threshold sweep, AUC + question bootstrap, bias stats, QC
               flags. Pure post-processing of anchor-fit/loo artifacts.
  calibrate    Fit p_fit = sigma(intercept + slope * Delta_cg) from LOO deltas.
               By default the intercept is PINNED so ground-truth parity
               (Delta=0) scores 0.90, and ground truths are weighted to match
               the non-ground-truths in total; see bt/calibrate.py.
  score        Score one candidate's free-generated answers, filling the
               partial-credit results into a scored_answers file (under the
               historical key `context_fit`).
  simulate     Fully synthetic recovery tests / reports (no network ever).

Global flags (all networked subcommands)
-----------------------------------------
  --judge MODEL_ID       Judge model, OpenRouter id (default: anthropic/claude-sonnet-5)
  --judge-effort LEVEL   none|low|medium|high (default: medium)
  --seed INT             Master seed (default: 20260728)
  --benchmark PATH       Benchmark JSONL (default: naming.latest_benchmark(../booksample))
  --repeats N            Judge calls per ordered pair (default: 1)
  --prior-scale F        BT prior sigma (default: 1.0)
  --prompt-mode MODE     exemplars|rationales (default: rationales). "exemplars"
                         is deprecated; it is kept only to reproduce artifacts
                         fitted before the mode existed, and it alone carries no
                         __pm- tag suffix (a naming fact, not a preference). See
                         bt/prompts.py for what each mode shows the judge and for
                         where rationale masking happens (prompt-build time, per
                         comparison). The mode is part of the artifact tag, so a
                         mismatch between subcommands reads the wrong anchors
                         rather than corrupting anything.
  --questions Q1,Q2,...  Restrict to these question numbers
  --no-cache             Disable the prompt cache
  --dry-run              Print the planned call count + cost estimate; no network
  --debug                Print raw judge responses

Examples
--------
  python bt_context_scoring.py anchor-fit \\
      --benchmark ../booksample/manual/chronologic_manual_0.1.jsonl \\
      --judge anthropic/claude-sonnet-5 --judge-effort medium --repeats 1

  python bt_context_scoring.py loo --benchmark ../booksample/manual/chronologic_manual_0.1.jsonl

  python bt_context_scoring.py validate --benchmark ... --n-boot 2000

  python bt_context_scoring.py calibrate --benchmark ... [--extra-labels rows.jsonl]

  python bt_context_scoring.py score \\
      --scored-file scored_answers/judge_....json \\
      --free-gen generated_answers/free_gen_....json \\
      --benchmark ...

  python bt_context_scoring.py simulate --mode null --replicates 50 --seed 1
"""

from __future__ import annotations

import argparse
import json
import math
import random
import sys
from pathlib import Path

import numpy as np
from scipy.special import expit

MODELASJUDGE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(MODELASJUDGE_DIR))

from bt import artifacts
from bt.cache import PromptCache
from bt.calibrate import apply_calibration, fit_calibration
from bt.collect import merge_counts, run_comparisons
from bt.design import Item, build_anchor_design, build_candidate_design, items_from_question, select_reference_gt
from bt.fit import fit_anchor_model, load_anchor_fits, save_anchor_fits
from bt.prompts import build_bt_prompt, build_exemplar_block
from bt.tau import score_candidate
from bt.validate import (LooRecord, bias_stats, bootstrap_auc, dedupe_judgments,
                         restrict_counts, roc_from_loo)
from substantive.routing import is_legacy_context_scored, route_questions
from substantive import artifacts as substantive_artifacts
from substantive import verdicts

# Placeholder stored in delta_draws_by_qnum for a short-circuited question; the
# npz save loop replaces it with a NaN row of the run's common length.
_AUTO_DELTA_SENTINEL = object()

# Kept as an alias so any external caller of the old name keeps working.
is_context_scored = is_legacy_context_scored


def load_benchmark(path) -> dict[str, dict]:
    """qnum (str) -> record, for questions routed to the partial-credit (BT) channel.

    Delegates to substantive.routing.route_questions, which resolves the
    precedence partial_credit -> context_judged -> the legacy
    frame_type/reasoning_type rule (plan §0: both this loader and
    judge_scoring_nocontext's had silently diverged from `partial_credit`,
    the field the spec names, by falling back to the legacy rule whenever
    `context_judged` was absent -- as it is on every released
    chronologic_en_*.jsonl). Return type is unchanged (qnum -> record) so
    every existing caller and test keeps working; only the selection rule
    is now shared.
    """
    return route_questions(path).partial


def _frame(rec: dict) -> str:
    """Prefer the adjusted substantive frame over the original metadata_frame,
    mirroring judge_scoring_nocontext._load_benchmark_frames."""
    return rec.get("substantive_metadata_frame") or rec.get("metadata_frame", "")


def select_questions(records: dict[str, dict], questions_arg: str | None) -> dict[str, dict]:
    if not questions_arg:
        return records
    wanted = set(questions_arg.split(","))
    return {q: r for q, r in records.items() if q in wanted}


def _n_gt(rec: dict) -> int:
    return sum(1 for t in rec.get("answer_types", []) if t == "ground_truth")


def stratified_subsample(records: dict[str, dict], n: int, stratify_by: list[str],
                         seed: int) -> list[str]:
    """Stratified sample of `n` qnums from `records`, largest-remainder allocation.

    Why stratify on n_gt (plan §8): cmd_loo skips held-out ground truths
    when len(gt_ids) < 2, so only the two-GT questions can ever produce a
    label==1.0 LOO record. Proportional allocation alone would under-
    represent them if they are a minority of the population; stratifying
    on n_gt (alongside question_category, the default) keeps them
    represented in proportion to the *population*, not starved to zero by
    chance the way unstratified random sampling could.
    """
    def key(rec):
        parts = []
        for field in stratify_by:
            parts.append(str(_n_gt(rec)) if field == "n_gt" else str(rec.get(field, "")))
        return tuple(parts)

    strata: dict[tuple, list[str]] = {}
    for qnum, rec in records.items():
        strata.setdefault(key(rec), []).append(qnum)

    total = sum(len(v) for v in strata.values())
    if n >= total:
        return sorted(records, key=int)

    raw = {k: len(v) * n / total for k, v in strata.items()}
    floors = {k: int(v) for k, v in raw.items()}
    remainder = n - sum(floors.values())
    for k in sorted(strata, key=lambda k: -(raw[k] - floors[k]))[:remainder]:
        floors[k] += 1

    rng = random.Random(seed)
    selected: list[str] = []
    for k, count in floors.items():
        pool = strata[k]
        selected.extend(rng.sample(pool, min(count, len(pool))))
    return sorted(selected, key=int)


# How Delta relates a candidate to a question's ground truths. Recorded in
# the LOO and calibration artifacts because changing it changes every Delta:
# on the pilot the two GTs of a question differ by a median 0.71.
REFERENCE_POLICY = "mean-of-all-gts"


class PriorScaleMismatch(RuntimeError):
    """Artifacts on disk were produced under incompatible scoring settings."""


def check_prior_scale_consistency(anchor_meta: dict, calib: dict | None,
                                  candidate_prior_scale: float) -> None:
    """Refuse to score when the anchors, the calibration, and the candidate
    grid were not built on the same prior scale.

    theta scales close to linearly with prior_scale under the near-complete
    separation this judge produces -- measured on the pilot, Delta inflated
    2.81x when the prior went 1.0 -> 3.0.  Calibration silently undoes that:
    the slope fell 1.797 -> 0.647, a 2.78x compensation, leaving p_fit
    invariant to within a median 0.009 per item.  The cancellation is exact
    only when the slope is *applied* on the scale it was *fitted* on.

    Mixing them is therefore a silent, large error rather than a loud one:
    a ps=3 calibration applied to ps=1 deltas would inflate every reported
    p_fit by roughly that same 2.78x.  Nothing else in the pipeline would
    object, because prior_scale is not part of the artifact tag.
    """
    anchor_ps = anchor_meta.get("prior_scale")
    calib_ps = calib.get("prior_scale") if calib else None

    unstamped = []
    if anchor_ps is None:
        unstamped.append("anchors")
    if calib is not None and calib_ps is None:
        unstamped.append("calibration")
    if unstamped:
        print(f"  warning: no prior_scale recorded in {' and '.join(unstamped)}; "
              f"cannot verify consistency. Re-run the producing subcommand to "
              f"stamp it. Proceeding on the assumption that everything used "
              f"--prior-scale {candidate_prior_scale}.")

    calib_policy = calib.get("reference_policy") if calib else None
    if calib_policy is not None and calib_policy != REFERENCE_POLICY:
        raise PriorScaleMismatch(
            f"calibration was fitted under reference_policy={calib_policy!r} but this "
            f"build uses {REFERENCE_POLICY!r}. Delta means a different thing under each "
            f"(the pilot's two GTs differ by a median 0.71), so p_fit would be wrong. "
            f"Re-run `loo` and `calibrate`."
        )
    if calib is not None and calib_policy is None:
        print(f"  warning: calibration has no reference_policy recorded; assuming "
              f"{REFERENCE_POLICY!r}. Re-run `loo` and `calibrate` to stamp it.")

    seen = {"candidate grid": candidate_prior_scale}
    if anchor_ps is not None:
        seen["anchors"] = anchor_ps
    if calib_ps is not None:
        seen["calibration"] = calib_ps
    distinct = {round(float(v), 10) for v in seen.values()}
    if len(distinct) > 1:
        detail = ", ".join(f"{k}={v}" for k, v in seen.items())
        raise PriorScaleMismatch(
            f"prior_scale differs across artifacts: {detail}. p_fit would be "
            f"wrong by roughly the ratio between them. Re-run `loo` and "
            f"`calibrate` at --prior-scale {candidate_prior_scale}, or score "
            f"with the scale the calibration was fitted on."
        )


def make_judge_call_from_args(args):
    if args.dry_run:
        return None
    from bt.llm_judge import make_llm_judge_call
    return make_llm_judge_call(args.judge, args.judge_effort, debug=args.debug)


def cmd_anchor_fit(args):
    benchmark_records = select_questions(load_benchmark(args.benchmark), args.questions)
    tag = artifacts.bt_tag(args.judge, args.benchmark, args.judge_effort, args.prompt_mode,
                           args.prior_dist)
    cache = None if args.no_cache else PromptCache(artifacts.cache_dir())
    judge_call = make_judge_call_from_args(args)

    planned = 0
    designs = {}
    for qnum, rec in benchmark_records.items():
        items = items_from_question(rec)
        comps = build_anchor_design(qnum, items, args.repeats, args.seed)
        designs[qnum] = (items, comps, rec)
        planned += len(comps)

    print(f"{len(benchmark_records)} questions, {planned} planned judge calls.")
    if args.dry_run:
        print(f"Estimated cost class: {planned} calls at judge={args.judge} effort={args.judge_effort}")
        return

    fits = {}
    all_logs = []
    for qnum, (items, comps, rec) in designs.items():
        items_by_id = {it.item_id: it for it in items}

        def build(comp, _items_by_id=items_by_id, _rec=rec, _mode=args.prompt_mode):
            block = build_exemplar_block(list(_items_by_id.values()),
                                         {comp.first, comp.second}, set(), _mode)
            return build_bt_prompt(_frame(_rec), _rec.get("main_question", ""),
                                   block, _items_by_id[comp.first].text,
                                   _items_by_id[comp.second].text, _mode)

        def call(comp, system, user, _judge_call=judge_call):
            return _judge_call(comp, system, user)

        result = run_comparisons(comps, items_by_id, build, call, cache=cache,
                                 judge_model=args.judge, judge_effort=args.judge_effort)
        all_logs.extend(result.log_records)
        fit = fit_anchor_model([it.item_id for it in items], result.counts,
                               prior_scale=args.prior_scale, seed=args.seed,
                               prior_dist=args.prior_dist, prior_df=args.prior_df)
        fits[qnum] = fit
        print(f"  q{qnum}: {result.completed_calls}/{result.planned_calls} calls, "
              f"abstention {result.abstention_rate:.2f}")

    artifacts.ensure_dirs()
    anchors_file = artifacts.anchors_path(tag)
    # Merge rather than replace: `save_anchor_fits` rewrites the whole archive,
    # so a --questions run would otherwise discard every question it did not
    # refit. Refitting a subset should update those questions and leave the
    # rest of the fit standing.
    merged, prior_meta = {}, {}
    if anchors_file.exists():
        merged, prior_meta = load_anchor_fits(anchors_file)
        kept = [q for q in merged if q not in fits]
        if kept:
            print(f"  merging into {len(kept)} existing question fit(s) already on disk")
    merged.update(fits)
    meta = {**prior_meta,
            "judge": args.judge, "judge_effort": args.judge_effort,
            "benchmark": str(args.benchmark), "prior_scale": args.prior_scale,
            "seed": args.seed, "prompt_mode": args.prompt_mode,
            "prior_dist": args.prior_dist, "prior_df": args.prior_df}
    # repeats can differ per question once subsets are refit, so record it per
    # question rather than pretending one value describes the archive.
    reps = dict(prior_meta.get("repeats_by_question") or {})
    reps.update({q: args.repeats for q in fits})
    meta["repeats_by_question"] = reps
    save_anchor_fits(anchors_file, merged, meta=meta)
    artifacts.append_jsonl(artifacts.judgments_path(tag), all_logs)
    print(f"Wrote {artifacts.anchors_path(tag)}")


def cmd_score(args):
    scored = json.loads(Path(args.scored_file).read_text(encoding="utf-8"))
    free_gen = json.loads(Path(args.free_gen).read_text(encoding="utf-8"))
    benchmark_records = load_benchmark(args.benchmark)
    book_context_qnums = set(scored.get("book_context_qnums", benchmark_records.keys()))

    tag = artifacts.bt_tag(args.judge, args.benchmark, args.judge_effort, args.prompt_mode,
                           args.prior_dist)
    anchors_file = artifacts.anchors_path(tag)
    if not anchors_file.exists():
        raise FileNotFoundError(
            f"No anchor fits at {anchors_file}; run `anchor-fit` first."
        )
    fits, anchor_meta = load_anchor_fits(anchors_file)

    calib_file = artifacts.calibration_path(tag)
    if not calib_file.exists():
        raise FileNotFoundError(
            f"No calibration at {calib_file}; run `calibrate` first. Uncalibrated tau is "
            "not on the p_q scale and must never enter a pooled score (spec §8.9)."
        )
    calib = json.loads(calib_file.read_text(encoding="utf-8"))
    check_prior_scale_consistency(anchor_meta, calib, args.prior_scale)

    results_file = artifacts.results_path(tag)
    results = json.loads(results_file.read_text(encoding="utf-8")) if results_file.exists() else None
    default_r_q = results["r_q"] if results else None

    cache = None if args.no_cache else PromptCache(artifacts.cache_dir())
    judge_call = make_judge_call_from_args(args)

    # The calibration design travels with the scores it produced, so a scored
    # file built against an anchored curve can never be silently combined with
    # draws fit under a free intercept (drawbank.COMPATIBILITY_KEYS).
    calib_pin_p = calib.get("pin_p")
    calib_class_balance = bool(calib.get("class_balance", False))

    context_fit = dict(scored.get("context_fit", {}))
    calib_rows = []
    delta_draws_by_qnum: dict[str, object] = {}   # spec §9 item 4: persist, don't discard
    c_len_by_qnum: dict[str, int] = {}
    auto_by_qnum: dict[str, float] = {}           # qnum -> 1.0/0.0 for short-circuits
    for qnum in sorted(book_context_qnums & benchmark_records.keys() & set(free_gen.get("answers", {}))):
        rec = benchmark_records[qnum]
        items = items_from_question(rec)
        items_by_id = {it.item_id: it for it in items}
        if qnum not in fits:
            continue
        fit = fits[qnum]
        gt_ids = [it.item_id for it in items if it.kind == "ground_truth"]
        pool_ref = select_reference_gt(qnum, gt_ids, args.seed)   # who it faces
        reference_gt = gt_ids                                     # what Delta is measured from
        cand = Item("cand", free_gen["answers"][qnum]["answer"], "candidate")
        comps, withdrawn = build_candidate_design(qnum, items, cand, pool_ref,
                                                   args.repeats, args.seed)
        items_by_id["cand"] = cand

        if args.dry_run:
            continue

        # Automatic verdicts, before the first call that costs money. Everything
        # above this point is free local computation; run_comparisons below is
        # the first thing that spends. `withdrawn` must already exist, which is
        # why this sits after build_candidate_design rather than before it.
        verdict = verdicts.auto_verdict(
            cand.text,
            [it.text for it in items if it.kind == "ground_truth"],
            verdicts.autofail_strings_partial(rec),
            qnum=qnum,
        )
        if verdict is not None:
            p = 1.0 if verdict == "pass" else 0.0
            context_fit[qnum] = {
                # not f"bt:{args.judge}" -- no judge was consulted, and this
                # makes short-circuits greppable the way the pass/fail path's
                # judge="identity" already is.
                "judge": "bt:identity", "r_q": default_r_q,
                "judgments": [], "scores": [p],
                "gt_positions": [None], "gt_indices": [None],
                "bt": {
                    "p_fit": p, "p_fit_ci": [p, p],
                    "tau_mean": p, "tau_ci": [p, p],
                    # null, not NaN: json.dumps emits a bare `NaN` literal that
                    # jq and strict JSON parsers reject. NaN belongs only in the
                    # npz arrays below, where it is load-bearing.
                    "delta_cg_mean": None, "delta_cg_ci": [None, None],
                    "reference_gt": reference_gt, "withdrawn_gts": withdrawn,
                    "n_comparisons": 0, "dropped_pairs": 0,
                    "artifacts_tag": tag,
                    "auto_verdict": ("gt_identity" if verdict == "pass"
                                     else "distractor_identity"),
                    "pin_p": calib_pin_p, "class_balance": calib_class_balance,
                },
            }
            # Sentinel, not zeros: Delta=0 literally means "exactly GT-level", so
            # zeros would make any reader that ignores auto__ compute sigma(a) for
            # a question whose true value is 0.0 or 1.0 -- wrong and silent. NaN
            # is loud everywhere. Filled to the run's common row length at save
            # time, since drawbank rejects unequal-length rows.
            delta_draws_by_qnum[qnum] = _AUTO_DELTA_SENTINEL
            c_len_by_qnum[qnum] = len(cand.text)
            auto_by_qnum[qnum] = p
            continue

        def build(comp, _items_by_id=items_by_id, _withdrawn=set(withdrawn), _rec=rec,
                  _mode=args.prompt_mode):
            block = build_exemplar_block(list(_items_by_id.values()),
                                         {comp.first, comp.second}, _withdrawn, _mode)
            return build_bt_prompt(_frame(_rec), _rec.get("main_question", ""),
                                   block, _items_by_id[comp.first].text,
                                   _items_by_id[comp.second].text, _mode)

        def call(comp, system, user, _judge_call=judge_call):
            return _judge_call(comp, system, user)

        result = run_comparisons(comps, items_by_id, build, call, cache=cache,
                                 judge_model=args.judge, judge_effort=args.judge_effort)
        if not result.counts:
            continue
        score = score_candidate(fit, result.counts, "cand", reference_gt,
                                prior_scale=args.prior_scale, seed=args.seed,
                                prior_dist=args.prior_dist, prior_df=args.prior_df)

        p_mean, p_ci, p_draws = apply_calibration(calib, score.delta_draws)
        delta_draws_by_qnum[qnum] = score.delta_draws
        c_len_by_qnum[qnum] = len(cand.text)

        context_fit[qnum] = {
            "judge": f"bt:{args.judge}",
            "r_q": default_r_q,
            "judgments": [], "scores": [p_mean],
            "gt_positions": [None], "gt_indices": [None],
            "bt": {
                "p_fit": p_mean, "p_fit_ci": list(p_ci),
                "tau_mean": score.tau_mean, "tau_ci": list(score.tau_ci),
                "delta_cg_mean": score.delta_mean, "delta_cg_ci": list(score.delta_ci),
                "reference_gt": reference_gt, "withdrawn_gts": withdrawn,
                "n_comparisons": score.n_comparisons, "dropped_pairs": len(result.dropped_groups),
                "artifacts_tag": tag,
            },
        }
        if args.emit_calibration_row:
            calib_rows.append({"qid": qnum, "item_id": "cand", "delta_mean": score.delta_mean,
                               "label": None, "source": "candidate"})

    if args.dry_run:
        print(f"Would score {len(book_context_qnums & benchmark_records.keys())} context questions.")
        return

    out = dict(scored)
    out["context_fit"] = context_fit
    out["bt_context"] = {
        "judge": args.judge, "effort": args.judge_effort, "artifacts_tag": tag,
        "calibration_file": str(calib_file),
        "results_file": str(results_file) if results is not None else None,
    }
    out_path = Path(args.output) if args.output else (
        Path(args.scored_file).parent / f"{Path(args.scored_file).stem}_btcontext.json"
    )
    out_path.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"Wrote {out_path}")
    if auto_by_qnum:
        n_pass = sum(1 for v in auto_by_qnum.values() if v == 1.0)
        print(f"  {len(auto_by_qnum)} automatic verdicts, no judge calls "
              f"({n_pass} ground-truth matches, {len(auto_by_qnum) - n_pass} "
              f"distractor matches).")

    if args.emit_calibration_row and calib_rows:
        artifacts.append_jsonl(Path(args.emit_calibration_row), calib_rows)

    if args.save_delta_draws is not None and delta_draws_by_qnum:
        candidate_label = scored.get("candidate_label") or scored.get("candidate_model", "unknown")
        candidate_effort = scored.get("candidate_reasoning_effort", "none")
        rng = np.random.default_rng(args.seed)
        thin = args.thin
        # Short-circuited questions get a NaN row of the same length as every
        # judged row -- drawbank rejects unequal lengths, and their value comes
        # from auto__{qnum} rather than from Delta.
        judged_lengths = {len(np.asarray(d)) for q, d in delta_draws_by_qnum.items()
                          if d is not _AUTO_DELTA_SENTINEL}
        row_len = min(min(judged_lengths), thin) if judged_lengths else thin

        arrays = {}
        for qnum, draws in delta_draws_by_qnum.items():
            if draws is _AUTO_DELTA_SENTINEL:
                draws = np.full(row_len, np.nan, dtype=np.float32)
            else:
                draws = np.asarray(draws, dtype=np.float32)
                if draws.shape[0] > thin:
                    idx = np.sort(rng.choice(draws.shape[0], size=thin, replace=False))
                    draws = draws[idx]
            arrays[f"delta__{qnum}"] = draws
            arrays[f"c_len__{qnum}"] = np.array(c_len_by_qnum[qnum], dtype=np.int64)
        for qnum, value in auto_by_qnum.items():
            arrays[f"auto__{qnum}"] = np.array(value, dtype=np.float64)
        meta = substantive_artifacts.base_meta(
            produced_by="bt_context_scoring.py score",
            seed=args.seed, judge=args.judge, judge_effort=args.judge_effort,
            benchmark_path=str(args.benchmark), benchmark_version=artifacts.benchmark_version(args.benchmark),
            bt_tag=tag, candidate_label=candidate_label, candidate_effort=candidate_effort,
            prior_scale=args.prior_scale, prior_dist=args.prior_dist, prior_df=args.prior_df,
            prompt_mode=args.prompt_mode, reference_policy=REFERENCE_POLICY, thin=thin,
            pin_p=calib_pin_p, class_balance=calib_class_balance,
        )
        draws_path = (Path(args.save_delta_draws) if args.save_delta_draws
                     else substantive_artifacts.delta_draws_path(tag, candidate_label, candidate_effort))
        substantive_artifacts.save_npz(draws_path, arrays, meta)
        print(f"Wrote {draws_path}: {len(delta_draws_by_qnum)} questions' Delta draws")


def cmd_loo(args):
    benchmark_records = select_questions(load_benchmark(args.benchmark), args.questions)

    if args.subsample:
        stratify_by = args.stratify_by.split(",")
        subsample_qnums = stratified_subsample(benchmark_records, args.subsample, stratify_by,
                                               args.seed)
        print(f"  --subsample {args.subsample} (stratify_by={stratify_by}): "
              f"{len(subsample_qnums)}/{len(benchmark_records)} questions selected.")
        benchmark_records = {q: benchmark_records[q] for q in subsample_qnums}
        if args.subsample_out:
            Path(args.subsample_out).write_text("\n".join(subsample_qnums) + "\n",
                                                encoding="utf-8")
            print(f"  Wrote subsample list to {args.subsample_out}")

    tag = artifacts.bt_tag(args.judge, args.benchmark, args.judge_effort, args.prompt_mode,
                           args.prior_dist)
    anchors_file = artifacts.anchors_path(tag)
    if not anchors_file.exists():
        raise FileNotFoundError(f"No anchor fits at {anchors_file}; run `anchor-fit` first.")
    _fits, _meta = load_anchor_fits(anchors_file)
    judgments = dedupe_judgments(artifacts.read_jsonl(artifacts.judgments_path(tag)))
    # The log is append-only and keeps every repeat ever collected, so five
    # questions still carry the repeat=1,2 rows from the --repeats 3 probe.
    # Honour --repeats here or those questions would silently re-enter LOO at
    # n=6 while the stored anchor fits are uniform n=2 -- unequal precision
    # across questions, from a probe that changed no theta structure.
    anchor_counts_by_q: dict[str, dict] = {}
    for rec in judgments:
        if rec["phase"] != "anchor" or rec.get("dropped"):
            continue
        if rec.get("repeat", 0) >= args.repeats:
            continue
        d = anchor_counts_by_q.setdefault(rec["qid"], {})
        w, n = d.get((rec["first"], rec["second"]), (0, 0))
        d[(rec["first"], rec["second"])] = (w + (rec["choice"] == "A"), n + 1)

    cache = None if args.no_cache else PromptCache(artifacts.cache_dir())
    judge_call = make_judge_call_from_args(args)

    planned = 0
    plans = {}
    for qnum, rec in benchmark_records.items():
        items = items_from_question(rec)
        gt_ids = [it.item_id for it in items if it.kind == "ground_truth"]
        item_plans = []
        for held_out in items:
            if held_out.kind == "ground_truth" and len(gt_ids) < 2:
                continue
            reduced_items = [it for it in items if it.item_id != held_out.item_id]
            # Two different things, deliberately: `pool_ref` picks which GT
            # the candidate is compared against (unchanged, so prompts and
            # cache keys are unchanged); `delta_refs` is what Delta is
            # measured from -- the mean of every GT except the held-out one.
            if held_out.kind == "ground_truth":
                pool_ref = select_reference_gt(
                    qnum, [g for g in gt_ids if g != held_out.item_id], args.seed)
            else:
                pool_ref = select_reference_gt(qnum, gt_ids, args.seed)
            delta_refs = [g for g in gt_ids if g != held_out.item_id] or gt_ids
            comps, withdrawn = build_candidate_design(
                qnum, reduced_items, held_out, pool_ref, args.repeats, args.seed,
                phase=f"loo:{held_out.item_id}",
            )
            item_plans.append((held_out, reduced_items, delta_refs, comps, withdrawn))
            planned += len(comps)
        plans[qnum] = (items, item_plans, rec)

    print(f"{len(benchmark_records)} questions, {planned} planned LOO judge calls.")
    if args.dry_run:
        return

    all_records: list[LooRecord] = []
    all_logs = []
    for qnum, (items, item_plans, rec) in plans.items():
        reduced_fits = {}
        for held_out, reduced_items, ref, comps, withdrawn in item_plans:
            reduced_ids = [it.item_id for it in reduced_items]
            reduced_counts = restrict_counts(anchor_counts_by_q.get(qnum, {}), held_out.item_id)
            fit = fit_anchor_model(reduced_ids, reduced_counts, prior_scale=args.prior_scale,
                                   seed=args.seed, prior_dist=args.prior_dist,
                                   prior_df=args.prior_df)
            reduced_fits[held_out.item_id] = fit

            items_by_id = {it.item_id: it for it in reduced_items}
            items_by_id[held_out.item_id] = held_out

            def build(comp, _items_by_id=items_by_id, _withdrawn=set(withdrawn), _rec=rec,
                  _mode=args.prompt_mode):
                block = build_exemplar_block(list(_items_by_id.values()),
                                             {comp.first, comp.second}, _withdrawn, _mode)
                return build_bt_prompt(_frame(_rec), _rec.get("main_question", ""),
                                       block, _items_by_id[comp.first].text,
                                       _items_by_id[comp.second].text, _mode)

            def call(comp, system, user, _judge_call=judge_call):
                return _judge_call(comp, system, user)

            result = run_comparisons(comps, items_by_id, build, call, cache=cache,
                                     judge_model=args.judge, judge_effort=args.judge_effort)
            all_logs.extend(result.log_records)
            if not result.counts:
                continue
            score = score_candidate(fit, result.counts, held_out.item_id, ref,
                                    prior_scale=args.prior_scale, seed=args.seed,
                                    prior_dist=args.prior_dist, prior_df=args.prior_df)
            all_records.append(LooRecord(qid=qnum, item_id=held_out.item_id,
                                         kind=held_out.kind, reference_gt=ref, score=score,
                                         prob=held_out.prob))

    artifacts.ensure_dirs()
    artifacts.write_json(artifacts.loo_path(tag), {
        "meta": {"judge": args.judge, "benchmark": str(args.benchmark),
                 "prior_scale": args.prior_scale,
                 "prior_dist": args.prior_dist,
                 "reference_policy": REFERENCE_POLICY},
        "records": [
            {"qid": r.qid, "item_id": r.item_id, "kind": r.kind, "prob": r.prob,
             "reference_gt": r.reference_gt,
             "tau_mean": r.score.tau_mean, "tau_ci": list(r.score.tau_ci),
             "delta_mean": r.score.delta_mean, "delta_ci": list(r.score.delta_ci),
             "n_comparisons": r.score.n_comparisons}
            for r in all_records
        ],
    })
    artifacts.append_jsonl(artifacts.judgments_path(tag), all_logs)
    print(f"Wrote {artifacts.loo_path(tag)} ({len(all_records)} records)")


def cmd_validate(args):
    tag = artifacts.bt_tag(args.judge, args.benchmark, args.judge_effort, args.prompt_mode,
                           args.prior_dist)
    loo_data = artifacts.read_json(artifacts.loo_path(tag))
    # roc_from_loo/bootstrap_auc only read .qid, .kind, .score.tau_mean; a
    # lightweight shim avoids reconstructing full CandidateScore objects
    # (their draws were not persisted in bt_loo_{tag}.json).
    from types import SimpleNamespace
    records = [
        SimpleNamespace(qid=r["qid"], kind=r["kind"], prob=r.get("prob", 0.0),
                        score=SimpleNamespace(tau_mean=r["tau_mean"]))
        for r in loo_data["records"]
    ]
    roc = roc_from_loo(records)
    by_q: dict[str, list] = {}
    for r in records:
        by_q.setdefault(r.qid, []).append(r)
    auc_ci = bootstrap_auc(by_q, n_boot=args.n_boot, seed=args.seed)

    log_records = dedupe_judgments(artifacts.read_jsonl(artifacts.judgments_path(tag)))
    bias = bias_stats(log_records)

    # Carry the LOO run's provenance forward: these ROC numbers are only
    # comparable to others fitted under the same reference policy and prior.
    loo_meta = loo_data.get("meta", {})
    results = {**roc, "auc_ci": list(auc_ci), "bias": bias, "judge": args.judge,
              "benchmark": str(args.benchmark),
              "reference_policy": loo_meta.get("reference_policy"),
              "prior_scale": loo_meta.get("prior_scale")}
    artifacts.ensure_dirs()
    artifacts.write_json(artifacts.results_path(tag), results)
    print(f"Wrote {artifacts.results_path(tag)}: AUC={roc['auc']:.3f} t*={roc['t_star']:.2f} "
          f"({roc['n_ground_truth']} GT / {roc['n_distractor']} distractor, "
          f"{roc['n_excluded_partial']} partial excluded)")


def loo_label(rec: dict) -> tuple[float, str]:
    """Calibration label for one LOO record: the benchmark's own probability.

    Ground truths label 1.0 and plain distractors 0.0, exactly as before.
    Answers human judges scored between 0 and 1 — the "inauthentic but
    satisfactory" cases the spec asks for — carry that fractional value
    as a soft label, which fit_calibration takes natively.
    """
    if rec["kind"] == "ground_truth":
        return 1.0, "ground_truth"
    prob = float(rec.get("prob", 0.0) or 0.0)
    if 0.0 < prob < 1.0:
        return prob, "partial"
    return 0.0, "distractor"


def _length_lookup(benchmark_path) -> dict[str, dict[str, int]]:
    """{qid: {item_id: character length}} for every item in every BT-routed question."""
    lookup = {}
    for qid, rec in load_benchmark(benchmark_path).items():
        lookup[qid] = {it.item_id: len(it.text) for it in items_from_question(rec)}
    return lookup


def _attach_z_len(records: list[dict], benchmark_path) -> tuple[list[dict], dict]:
    """Resolve and attach standardized log-length z_len to each record.

    Records pooled from a different benchmark version (e.g. the BT pilot
    via --extra-labels) generally will not resolve against this
    benchmark's items and are dropped from the length-covariate fit --
    printed, not silent. Returns (resolved_records, {mu_loglen, sd_loglen}).
    """
    lookup = _length_lookup(benchmark_path)
    resolved = []
    for r in records:
        item_len = lookup.get(r["qid"], {}).get(r["item_id"])
        if item_len is not None:
            resolved.append({**r, "_len": item_len})
    skipped = len(records) - len(resolved)
    if skipped:
        print(f"  --length-covariate: {skipped}/{len(records)} records could not be resolved "
              f"against {benchmark_path} (likely pooled from a different benchmark version) "
              f"and were dropped from the length-covariate fit.")
    if len(resolved) < 2:
        raise ValueError(
            f"--length-covariate: only {len(resolved)} records resolved against "
            f"{benchmark_path}; cannot fit."
        )
    log_lens = np.array([math.log(max(r["_len"], 1)) for r in resolved])
    mu, sd = float(log_lens.mean()), float(log_lens.std()) or 1.0
    for r in resolved:
        r["z_len"] = (math.log(max(r["_len"], 1)) - mu) / sd
    return resolved, {"mu_loglen": mu, "sd_loglen": sd}


def _cluster_bootstrap_calibration(records: list[dict], *, n_boot: int, seed: int,
                                   use_length: bool, pin_p: float | None = None,
                                   class_balance: bool = False) -> tuple[np.ndarray, int]:
    """Cluster-bootstrap (a, b[, c]) by qid -- resampling records, not qids in
    isolation, keeps every record from a sampled question together (spec §8.7:
    239 records over 40 pilot questions is a cluster sample, effective n
    nearer 40 than 239). Returns (draws (R, 2 or 3), n_zero_positive_replicates
    -- replicates with no positive-label record, where fit_calibration would
    degenerate; these are skipped and counted, not silently included).

    pin_p and class_balance are forwarded to every replicate, so the draws
    describe the same estimator as the point fit.  Class weights are
    recomputed *inside* fit_calibration for each replicate, which is what we
    want: the GT:non-GT ratio varies across resampled question sets, and
    reusing the full-sample weights would misweight every replicate.  Under
    pinning the resulting cal_a column is constant -- ground-truth parity is
    a declared convention with no estimation error, so instrument-layer
    uncertainty lives entirely in the slope.
    """
    by_qid: dict[str, list[dict]] = {}
    for r in records:
        by_qid.setdefault(r["qid"], []).append(r)
    qids = sorted(by_qid)
    rng = np.random.default_rng(seed)

    draws = []
    n_zero_positive = 0
    for _ in range(n_boot):
        sample_qids = rng.choice(qids, size=len(qids), replace=True)
        pooled = [r for q in sample_qids for r in by_qid[q]]
        if not any(r["label"] > 0 for r in pooled):
            n_zero_positive += 1
            continue
        fit = fit_calibration(pooled, use_length=use_length,
                              pin_p=pin_p, class_balance=class_balance)
        draws.append((fit["intercept"], fit["slope"], fit["length_slope"]) if use_length
                     else (fit["intercept"], fit["slope"]))
    return np.array(draws, dtype=float), n_zero_positive


def cmd_calibrate(args):
    tag = artifacts.bt_tag(args.judge, args.benchmark, args.judge_effort, args.prompt_mode,
                           args.prior_dist)
    loo_data = artifacts.read_json(artifacts.loo_path(tag))
    this_version = artifacts.benchmark_version(args.benchmark)
    records = []
    for r in loo_data["records"]:
        label, source = loo_label(r)
        records.append({"qid": r["qid"], "item_id": r["item_id"],
                        "delta_mean": r["delta_mean"], "label": label, "source": source,
                        "benchmark_version": this_version})
    if args.extra_labels:
        # Rows may carry their own benchmark_version (recommended when
        # pooling LOO records from a different version, e.g. the BT pilot
        # via namespaced qids like "pilot:3"); default to this run's
        # version when absent.
        extra = artifacts.read_jsonl(Path(args.extra_labels))
        for r in extra:
            r.setdefault("benchmark_version", this_version)
        records.extend(extra)

    length_standardization = None
    fit_records = records
    if args.length_covariate:
        fit_records, length_standardization = _attach_z_len(records, args.benchmark)

    pin_p = None if args.no_pin else args.pin_p
    class_balance = not args.no_class_balance
    if pin_p is not None and args.length_covariate:
        sys.exit("--pin-p and --length-covariate cannot be combined yet: the length "
                 "slope shifts the curve at Delta=0 by c*z_len, so pinning the "
                 "intercept no longer pins ground-truth parity. Use --no-pin.")

    calib = fit_calibration(fit_records, use_length=args.length_covariate,
                            pin_p=pin_p, class_balance=class_balance)
    # Stamp the prior scale the LOO deltas were produced on. b is fitted on
    # that scale and only cancels it when applied on the same scale -- see
    # check_prior_scale_consistency.
    calib["prior_scale"] = loo_data.get("meta", {}).get("prior_scale")
    calib["reference_policy"] = loo_data.get("meta", {}).get("reference_policy")
    if length_standardization:
        calib["length_standardization"] = length_standardization
    artifacts.ensure_dirs()
    artifacts.write_json(artifacts.calibration_path(tag), calib)
    ps = calib["prior_scale"]
    print(f"Wrote {artifacts.calibration_path(tag)}: "
          f"intercept={calib['intercept']:.3f} slope={calib['slope']:.3f} "
          + (f"length_slope={calib['length_slope']:.3f} " if args.length_covariate else "")
          + f"n={calib['n']} {calib['n_by_source']}"
          + (f" pin_p={pin_p}" if pin_p is not None else " pin_p=none (free intercept)")
          + f" class_balance={class_balance}"
          + (f" prior_scale={ps}" if ps is not None else
             "  (no prior_scale in the LOO artifact; re-run `loo` to stamp it)"))
    print(f"  ground-truth parity (p_fit at Delta=0) = {expit(calib['intercept']):.3f}")

    if args.bootstrap:
        draws, n_zero_positive = _cluster_bootstrap_calibration(
            fit_records, n_boot=args.bootstrap, seed=args.seed,
            use_length=args.length_covariate, pin_p=pin_p, class_balance=class_balance)
        cal_a, cal_b = draws[:, 0], draws[:, 1]
        arrays = {"cal_a": cal_a, "cal_b": cal_b}
        if args.length_covariate:
            arrays["cal_c"] = draws[:, 2]
        cluster_ids = sorted({(r["qid"], r["benchmark_version"]) for r in fit_records})
        meta = substantive_artifacts.base_meta(
            produced_by="bt_context_scoring.py calibrate",
            seed=args.seed, judge=args.judge, judge_effort=args.judge_effort,
            benchmark_path=str(args.benchmark), benchmark_version=this_version,
            bt_tag=tag, prior_scale=calib["prior_scale"], prior_dist=args.prior_dist,
            prior_df=args.prior_df, prompt_mode=args.prompt_mode,
            reference_policy=calib["reference_policy"],
            n_boot=args.bootstrap, n_draws=int(draws.shape[0]), n_zero_positive=n_zero_positive,
            cluster_ids=[list(c) for c in cluster_ids], length_covariate=args.length_covariate,
            # The calibration design must travel with the draws: drawbank's
            # verify_compatible can only catch a mismatch when BOTH artifacts
            # carry the key, so stamping only the calibration JSON is a no-op.
            pin_p=pin_p, class_balance=class_balance,
        )
        draws_path = (Path(args.draws_out) if args.draws_out
                     else substantive_artifacts.calib_draws_path(tag))
        substantive_artifacts.save_npz(draws_path, arrays, meta)
        print(f"Wrote {draws_path}: {draws.shape[0]}/{args.bootstrap} replicates "
              f"({n_zero_positive} skipped, zero positive labels)")


def cmd_emit_pilot_labels(args):
    """Convert a pilot LOO artifact into namespaced --extra-labels rows.

    Namespacing (plan §4): pilot qid "3" (benchmark 0.1) and production qid
    "3" (benchmark 0.7) are different questions. The cluster bootstrap in
    `calibrate` resamples by qid, so leaving both bare would silently merge
    them into one cluster -- correlating two unrelated questions and
    narrowing the interval. Prefixing every pilot qid with "pilot:" keeps
    them distinct; verify_compatible's cluster-id check (drawbank.py) then
    catches the mistake if a caller forgets to namespace.
    """
    pilot_tag = artifacts.bt_tag(args.judge, args.pilot_benchmark, args.judge_effort,
                                 args.prompt_mode, args.prior_dist)
    loo_data = artifacts.read_json(artifacts.loo_path(pilot_tag))
    version = artifacts.benchmark_version(args.pilot_benchmark)
    rows = []
    for r in loo_data["records"]:
        label, source = loo_label(r)
        rows.append({"qid": f"pilot:{r['qid']}", "item_id": r["item_id"],
                    "delta_mean": r["delta_mean"], "label": label, "source": source,
                    "benchmark_version": version})
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text("\n".join(json.dumps(r) for r in rows) + ("\n" if rows else ""),
                                 encoding="utf-8")
    print(f"Wrote {len(rows)} namespaced pilot label rows to {args.output}")


def cmd_simulate(args):
    from bt import simulate as sim

    if args.mode in ("null", "all"):
        out = sim.run_null_control(n_items=6, replicates=args.replicates, master_seed=args.seed)
        artifacts.ensure_dirs()
        artifacts.write_json(artifacts.recovery_path("null", args.seed), out)
        print("null:", out)
    if args.mode in ("sbc", "all"):
        out = sim.run_sbc(n_items=4, replicates=args.replicates, master_seed=args.seed)
        artifacts.write_json(artifacts.recovery_path("sbc", args.seed), {
            "rank_uniformity_pvalue": out.rank_uniformity_pvalue, "coverage": out.coverage,
        })
        print("sbc p-value:", out.rank_uniformity_pvalue)
    if args.mode in ("coverage", "all"):
        theta_config = sim.structured_theta_config()
        out = sim.run_tau_coverage(theta_config, ["gt0", "gt1"], "gt0",
                                   args.replicates, args.seed)
        artifacts.write_json(artifacts.recovery_path("coverage", args.seed), {
            "bias": out.bias, "se_delta": out.se_delta, "coverage_90": out.coverage_90,
            "stratified": out.stratified,
        })
        print("coverage_90:", out.coverage_90)
    if args.mode in ("kappa", "all"):
        out = sim.run_kappa_sweep((0.5, 1, 2, 3), args.replicates, args.seed)
        artifacts.write_json(artifacts.recovery_path("kappa", args.seed),
                             {str(k): v for k, v in out.items()})
    if args.mode in ("misspec", "all"):
        out = sim.run_misspec_sweep((0, 0.25, 0.5, 1.0), (0, 0.5, 1.0), args.replicates, args.seed)
        artifacts.write_json(artifacts.recovery_path("misspec", args.seed),
                             {f"{g}_{o}": v for (g, o), v in out.items()})
    if args.mode in ("fullchain", "all"):
        theta_config = sim.structured_theta_config()
        out = sim.run_full_chain(theta_config, ["gt0", "gt1"], n_questions=5,
                                 replicates=args.replicates, master_seed=args.seed)
        artifacts.write_json(artifacts.recovery_path("fullchain", args.seed), out)
        print("fullchain:", out)
    if args.mode in ("sign", "all"):
        theta_config = sim.structured_theta_config()
        out = sim.run_sign_control(theta_config, ["gt0", "gt1"], n_questions=5,
                                   replicates=args.replicates, master_seed=args.seed)
        artifacts.write_json(artifacts.recovery_path("sign", args.seed), out)


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    def add_common(p):
        p.add_argument("--judge", default="anthropic/claude-sonnet-5")
        p.add_argument("--judge-effort", default="medium",
                       choices=["none", "low", "medium", "high"])
        p.add_argument("--seed", type=int, default=20260728)
        p.add_argument("--benchmark", required=True)
        p.add_argument("--repeats", type=int, default=1)
        p.add_argument("--prior-scale", type=float, default=1.0)
        p.add_argument("--prior-dist", default="normal",
                       choices=["normal", "studentt"],
                       help="prior shape on theta; studentt artifacts carry a __pd- suffix")
        p.add_argument("--prior-df", type=float, default=3.0,
                       help="degrees of freedom when --prior-dist studentt")
        p.add_argument("--prompt-mode", default=artifacts.DEFAULT_PROMPT_MODE,
                       choices=list(artifacts.PROMPT_MODES),
                       help="rubric style; artifacts for non-default modes carry a __pm- suffix")
        p.add_argument("--questions", default=None)
        p.add_argument("--no-cache", action="store_true")
        p.add_argument("--dry-run", action="store_true")
        p.add_argument("--debug", action="store_true")

    p_anchor = sub.add_parser("anchor-fit")
    add_common(p_anchor)
    p_anchor.set_defaults(func=cmd_anchor_fit)

    p_loo = sub.add_parser("loo")
    add_common(p_loo)
    p_loo.add_argument("--subsample", type=int, default=None,
                       help="Stratified subsample of this many questions (plan §8: run "
                            "before spending the full LOO budget).")
    p_loo.add_argument("--stratify-by", default="question_category,n_gt",
                       help="Comma list of fields to stratify on; 'n_gt' is computed "
                            "(number of ground truths), not a benchmark field.")
    p_loo.add_argument("--subsample-out", default=None,
                       help="Write the selected qnums, one per line, to this path.")
    p_loo.set_defaults(func=cmd_loo)

    p_validate = sub.add_parser("validate")
    add_common(p_validate)
    p_validate.add_argument("--n-boot", type=int, default=2000)
    p_validate.set_defaults(func=cmd_validate)

    p_calibrate = sub.add_parser("calibrate")
    add_common(p_calibrate)
    p_calibrate.add_argument("--extra-labels", default=None,
                             help="JSONL of extra {qid, item_id, delta_mean, label, source"
                                  "[, benchmark_version]} rows, e.g. namespaced pilot LOO "
                                  "records (qid 'pilot:3') for pooling into the calibration set.")
    p_calibrate.add_argument("--bootstrap", type=int, default=1000,
                             help="Cluster-bootstrap replicates by qid, saved to --draws-out. "
                                  "0 disables.")
    p_calibrate.add_argument("--length-covariate", action="store_true",
                             help="Fit sigma(a + b*Delta + c*z_len) instead of the plain "
                                  "2-parameter curve (spec §2.1). Cannot be combined "
                                  "with a pinned intercept; pass --no-pin.")
    p_calibrate.add_argument("--pin-p", type=float, default=0.90, metavar="P",
                             help="Pin p_fit at Delta=0 (ground-truth parity) to this "
                                  "value by fixing the intercept at logit(P) and solving "
                                  "for the slope only. Default 0.90.")
    p_calibrate.add_argument("--no-pin", action="store_true",
                             help="Let the intercept float. Reproduces the pre-anchored "
                                  "behavior; needed to rebuild older artifacts. Note the "
                                  "free intercept absorbs the calibration set's good:bad "
                                  "label odds, which is a benchmark design choice.")
    p_calibrate.add_argument("--no-class-balance", action="store_true",
                             help="Weight every LOO record equally instead of giving "
                                  "ground truths and non-ground-truths equal total "
                                  "weight. Reproduces the pre-anchored behavior.")
    p_calibrate.add_argument("--draws-out", default=None,
                             help="Calibration draw-bank path; default derived from the tag.")
    p_calibrate.set_defaults(func=cmd_calibrate)

    p_score = sub.add_parser("score")
    add_common(p_score)
    p_score.add_argument("--scored-file", required=True)
    p_score.add_argument("--free-gen", required=True)
    p_score.add_argument("--output", default=None)
    p_score.add_argument("--emit-calibration-row", default=None)
    p_score.add_argument("--save-delta-draws", nargs="?", const="", default=None,
                         help="Persist calibrated Delta draws (spec §9 item 4). Bare flag "
                              "uses the derived path; a value overrides it.")
    p_score.add_argument("--thin", type=int, default=1000,
                         help="Draws kept per question in the saved Delta bank (default 1000).")
    p_score.set_defaults(func=cmd_score)

    p_emit_pilot = sub.add_parser("emit-pilot-labels",
                                  help="Convert a pilot LOO artifact into namespaced "
                                       "--extra-labels rows for calibrate --extra-labels.")
    p_emit_pilot.add_argument("--judge", default="anthropic/claude-sonnet-5")
    p_emit_pilot.add_argument("--judge-effort", default="medium",
                              choices=["none", "low", "medium", "high"])
    p_emit_pilot.add_argument("--pilot-benchmark", required=True,
                              help="The pilot benchmark whose `loo` artifact to read "
                                   "(e.g. chronologic_btpilot_0.1.jsonl).")
    p_emit_pilot.add_argument("--prior-scale", type=float, default=1.0)
    p_emit_pilot.add_argument("--prior-dist", default="normal", choices=["normal", "studentt"])
    p_emit_pilot.add_argument("--prompt-mode", default=artifacts.DEFAULT_PROMPT_MODE,
                              choices=list(artifacts.PROMPT_MODES))
    p_emit_pilot.add_argument("--output", required=True)
    p_emit_pilot.set_defaults(func=cmd_emit_pilot_labels)

    p_sim = sub.add_parser("simulate")
    p_sim.add_argument("--mode", default="all",
                       choices=["sbc", "coverage", "kappa", "misspec", "fullchain",
                               "null", "sign", "all"])
    p_sim.add_argument("--replicates", type=int, default=200)
    p_sim.add_argument("--seed", type=int, default=12345)
    p_sim.add_argument("--report", action="store_true")
    p_sim.add_argument("--theta-from", default=None)
    p_sim.set_defaults(func=cmd_simulate)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
