"""bt_context_scoring.py — CLI for the Bradley-Terry context judge.

Thin argparse wrapper over the bt/ package. See bt-context-judge-plan.md
and bradley/bradley-terry-spec.md for the full design.

Subcommands
-----------
  anchor-fit   Fit the per-question Bradley-Terry anchor model for every
               context-scored question in a benchmark.
  loo          Leave-one-out: score every answer option as if it were a
               candidate, reusing the anchor comparisons already collected.
  validate     Threshold sweep, AUC + question bootstrap, bias stats, QC
               flags. Pure post-processing of anchor-fit/loo artifacts.
  calibrate    Fit p_fit = sigma(intercept + slope * Delta_cg) from LOO deltas.
  score        Score one candidate's free-generated answers, filling
               context_fit in a scored_answers file.
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
import sys
from pathlib import Path

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

    context_fit = dict(scored.get("context_fit", {}))
    calib_rows = []
    delta_draws_by_qnum: dict[str, object] = {}   # spec §9 item 4: persist, don't discard
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

    if args.emit_calibration_row and calib_rows:
        artifacts.append_jsonl(Path(args.emit_calibration_row), calib_rows)


def cmd_loo(args):
    benchmark_records = select_questions(load_benchmark(args.benchmark), args.questions)
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


def cmd_calibrate(args):
    tag = artifacts.bt_tag(args.judge, args.benchmark, args.judge_effort, args.prompt_mode,
                           args.prior_dist)
    loo_data = artifacts.read_json(artifacts.loo_path(tag))
    records = []
    for r in loo_data["records"]:
        label, source = loo_label(r)
        records.append({"qid": r["qid"], "item_id": r["item_id"],
                        "delta_mean": r["delta_mean"], "label": label, "source": source})
    if args.extra_labels:
        records.extend(artifacts.read_jsonl(Path(args.extra_labels)))
    calib = fit_calibration(records)
    # Stamp the prior scale the LOO deltas were produced on. b is fitted on
    # that scale and only cancels it when applied on the same scale -- see
    # check_prior_scale_consistency.
    calib["prior_scale"] = loo_data.get("meta", {}).get("prior_scale")
    calib["reference_policy"] = loo_data.get("meta", {}).get("reference_policy")
    artifacts.ensure_dirs()
    artifacts.write_json(artifacts.calibration_path(tag), calib)
    ps = calib["prior_scale"]
    print(f"Wrote {artifacts.calibration_path(tag)}: "
          f"intercept={calib['intercept']:.3f} slope={calib['slope']:.3f} "
          f"n={calib['n']} {calib['n_by_source']}"
          + (f" prior_scale={ps}" if ps is not None else
             "  (no prior_scale in the LOO artifact; re-run `loo` to stamp it)"))


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
    p_loo.set_defaults(func=cmd_loo)

    p_validate = sub.add_parser("validate")
    add_common(p_validate)
    p_validate.add_argument("--n-boot", type=int, default=2000)
    p_validate.set_defaults(func=cmd_validate)

    p_calibrate = sub.add_parser("calibrate")
    add_common(p_calibrate)
    p_calibrate.add_argument("--extra-labels", default=None)
    p_calibrate.set_defaults(func=cmd_calibrate)

    p_score = sub.add_parser("score")
    add_common(p_score)
    p_score.add_argument("--scored-file", required=True)
    p_score.add_argument("--free-gen", required=True)
    p_score.add_argument("--output", default=None)
    p_score.add_argument("--emit-calibration-row", default=None)
    p_score.set_defaults(func=cmd_score)

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
