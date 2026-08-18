"""run_pipeline.py — subprocess-based orchestrator for the substantive scoring
pipeline (plan §3/§5/§8).

    run_pipeline.py --candidate MODEL [options]

Runs the thirteen stages in dependency order (instrument column, then
candidate column, then the opt-in style batch), skipping any stage whose
output already satisfies its content-based skip predicate. Every stage is a
separate subprocess: each of the long-running scripts installs its own
SIGINT handler and resumes from its own output file, and importing them
into one process would mean only one SIGINT handler survives (plan §3).

`build_stages()` only reads the filesystem (safe to call under --dry-run);
all writes and subprocess calls happen in `execute()`.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import naming
from bt import artifacts as bt_artifacts
from bt.fit import load_anchor_fits
from judge_alpha_reliability_nocontext import (
    PENALTIES_PATH,
    RELIABILITY_DIR,
    _load_distractor_penalties,
)
from judge_scoring_nocontext import SCORED_DIR
from substantive import artifacts as substantive_artifacts
from substantive.routing import route_questions
from bt_context_scoring import stratified_subsample as _bt_stratified_subsample

BOOKSAMPLE_DIR = SCRIPT_DIR.parent / "booksample"
GENERATED_ANSWERS_DIR = SCRIPT_DIR / "generated_answers"

DEFAULT_JUDGE = "anthropic/claude-sonnet-4-6"
DEFAULT_BT_JUDGE = "anthropic/claude-sonnet-5"
DEFAULT_PYTHON = "/Users/tunder/Library/CloudStorage/Dropbox/python/py310hf/bin/python"

# Rough calls-per-question ratios lifted from the plan §8 cost table's worked
# numbers (680/79, 9152/310, 3900/80, 3508/310). These size the --dry-run
# cost table's estimate column; they are not exact per plan §8's own framing.
AVG_TRIALS_PER_ALPHA_Q = 9
AVG_CALLS_PER_ANCHOR_Q = 30
AVG_CALLS_PER_LOO_Q = 49
AVG_FITS_PER_LOO_Q = 5
AVG_CALLS_PER_BT_SCORE_Q = 11


# ---------------------------------------------------------------------------
# small filesystem helpers -- all read-only, safe under --dry-run
# ---------------------------------------------------------------------------

def _iter_jsonl(path):
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def _json_get(path) -> dict | None:
    path = Path(path)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _npz_keys(path) -> set[str]:
    path = Path(path)
    if not path.exists():
        return set()
    import numpy as np
    with np.load(path, allow_pickle=False) as data:
        return set(data.files)


def _newer(a, b) -> bool:
    """True if path `a` exists, `b` exists, and a's mtime > b's mtime."""
    a, b = Path(a), Path(b)
    return a.exists() and b.exists() and a.stat().st_mtime > b.stat().st_mtime


def _expected_alpha_trials(rec: dict, penalties: dict) -> int:
    """Mirrors judge_alpha_reliability_nocontext.py's compute_reliability
    trial count (len(valid_distractors) * len(ground_truths) * 2 slot
    orders), without making any judge calls. Used to detect a question
    whose content changed since its reliability data was seeded from an
    older benchmark version -- a stale key can't be told from a fresh one
    by presence alone, since a copied-forward seed file has the qnum
    either way."""
    answer_strings = rec.get("answer_strings", [])
    answer_types = rec.get("answer_types", [])
    gts = [s for s, t in zip(answer_strings, answer_types) if t == "ground_truth"]
    distractors = [(s, t) for s, t in zip(answer_strings, answer_types) if t != "ground_truth"]
    if not gts and answer_strings:
        gts = [answer_strings[0]]
        distractors = list(zip(answer_strings[1:], answer_types[1:]))
    n_valid_distractors = sum(1 for _, t in distractors if t in penalties)
    return n_valid_distractors * len(gts) * 2


# ---------------------------------------------------------------------------
# Stage / SkipResult
# ---------------------------------------------------------------------------

@dataclass
class SkipResult:
    skip: bool
    reason: str


@dataclass
class Stage:
    number: int
    name: str
    scope: str  # "instrument" | "candidate" | "batch"
    skip: SkipResult
    argv: list[str] | None = None
    action: Callable[[Callable], None] | None = None
    pre_action: Callable[[], None] | None = None
    cwd: Path = field(default_factory=lambda: SCRIPT_DIR)
    est_calls: int = 0
    est_fits: int = 0
    note: str = ""

    def resume_cmd(self) -> str:
        if self.argv is None:
            return f"(stage {self.number} {self.name} has no subprocess form; re-run run_pipeline.py)"
        return " ".join(self.argv)


def _stage_matches(stage: Stage, token: str) -> bool:
    return token == str(stage.number) or token.lower() == stage.name.lower()


def select_stages(stages: list[Stage], *, only: str | None = None,
                  stop_after: str | None = None) -> list[Stage]:
    if only:
        tokens = [t.strip() for t in only.split(",") if t.strip()]
        return [s for s in stages if any(_stage_matches(s, t) for t in tokens)]
    if stop_after:
        for i, s in enumerate(stages):
            if _stage_matches(s, stop_after):
                return stages[: i + 1]
        raise ValueError(f"--stop-after {stop_after!r} does not match any stage")
    return stages


# ---------------------------------------------------------------------------
# startup checks
# ---------------------------------------------------------------------------

def check_pymc_importable(python: str, runner=subprocess.run) -> None:
    """Fail at second 0, not hour 3 (plan §3)."""
    result = runner([python, "-c", "import pymc"], capture_output=True)
    rc = getattr(result, "returncode", 0)
    if rc != 0:
        stderr = getattr(result, "stderr", b"")
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", errors="replace")
        sys.exit(f"ERROR: {python} cannot import pymc (exit {rc}).\n{stderr}")


def check_judge_effort_matches_seed(judge: str, benchmark_version: str, judge_effort: str,
                                    seed_reliability_from: str) -> None:
    """The seeded reliability file inherits reasoning_effort from whichever
    file it is seeded from; judge_alpha_reliability_nocontext.py hard-exits
    on a mismatch with --judge-effort at its own default of "none" (plan §5).
    Catching it here means failing before any subprocess runs at all."""
    target = RELIABILITY_DIR / f"{naming.judge_tag(judge)}__{benchmark_version}.json"
    source = target if target.exists() else RELIABILITY_DIR / f"{naming.judge_tag(judge)}__{seed_reliability_from}.json"
    data = _json_get(source)
    if data is None:
        return  # nothing to seed from yet; stage 1 will report this itself
    existing_effort = data.get("reasoning_effort")
    if existing_effort is not None and existing_effort != judge_effort:
        sys.exit(
            f"ERROR: {source} was produced with reasoning_effort={existing_effort!r}, "
            f"but --judge-effort={judge_effort!r} was requested. judge_alpha_reliability_"
            f"nocontext.py will hard-exit on this mismatch at stage 2 -- pass a matching "
            f"--judge-effort or seed a fresh file."
        )


# ---------------------------------------------------------------------------
# build_stages -- read-only; safe to call under --dry-run
# ---------------------------------------------------------------------------

def build_stages(args) -> list[Stage]:
    py = args.python
    judge = args.judge
    judge_effort = args.judge_effort
    bt_judge = args.bt_judge
    candidate = args.candidate
    candidate_label = args.candidate_label or candidate
    candidate_effort = args.candidate_effort
    prior_scale = args.prior_scale
    prompt_mode = args.prompt_mode

    benchmark_path = Path(args.benchmark) if args.benchmark else naming.latest_benchmark(BOOKSAMPLE_DIR)
    bver = naming.benchmark_version(benchmark_path)

    routing = route_questions(benchmark_path)
    pf_qnums = set(routing.pass_fail)
    pc_qnums = set(routing.partial)
    total_questions = len(pf_qnums) + len(pc_qnums)

    tag = bt_artifacts.bt_tag(bt_judge, benchmark_path, judge_effort,
                              prompt_mode=prompt_mode, prior_dist="normal")

    reliability_target = RELIABILITY_DIR / f"{naming.judge_tag(judge)}__{bver}.json"
    reliability_seed = RELIABILITY_DIR / f"{naming.judge_tag(judge)}__{args.seed_reliability_from}.json"

    stages: list[Stage] = []

    # ---- stage 0: distractor_sorter -------------------------------------
    penalties = _load_distractor_penalties(PENALTIES_PATH) if PENALTIES_PATH.exists() else {}
    missing_types: set[str] = set()
    for rec in _iter_jsonl(benchmark_path):
        for t in rec.get("answer_types", []):
            if t != "ground_truth" and t not in penalties:
                missing_types.add(t)
    stages.append(Stage(
        0, "distractor_sorter", "instrument",
        skip=SkipResult(not missing_types,
                        "all answer_types classified" if not missing_types
                        else f"{len(missing_types)} unclassified answer_types: {sorted(missing_types)[:10]}"),
        argv=[py, "distractor_sorter.py"], cwd=SCRIPT_DIR,
    ))

    # ---- stage 1: seed reliability file ----------------------------------
    def _seed_reliability():
        if not reliability_seed.exists():
            sys.exit(f"ERROR: seed file {reliability_seed} not found; cannot seed {reliability_target}. "
                     f"Pass --seed-reliability-from VERSION to point at an existing reliability file.")
        reliability_target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(reliability_seed, reliability_target)
        print(f"Seeded {reliability_target} from {reliability_seed}")

    stages.append(Stage(
        1, "seed_reliability", "instrument",
        skip=SkipResult(reliability_target.exists(),
                        f"{reliability_target.name} already exists" if reliability_target.exists()
                        else f"{reliability_target.name} missing"),
        argv=None, action=lambda runner: _seed_reliability(),
    ))

    # ---- stage 2: judge_alpha_reliability_nocontext ----------------------
    existing_reliability = _json_get(reliability_target) or _json_get(reliability_seed) or {}
    existing_per_question = (existing_reliability or {}).get("per_question", {})
    existing_alpha_qnums = set(existing_per_question)
    new_alpha_qnums = pf_qnums - existing_alpha_qnums

    # A qnum can be a stale key, not a fresh one: seeding copies whatever was
    # keyed under the source version forward verbatim, so a question whose
    # ground-truth/distractor set changed since then still shows up as
    # "already scored" by presence alone. Recompute the trial count current
    # content implies and compare against what's stored.
    stale_alpha_qnums = sorted(
        (qnum for qnum in (pf_qnums & existing_alpha_qnums)
         if existing_per_question[qnum].get("question_total")
         != _expected_alpha_trials(routing.pass_fail[qnum], penalties)),
        key=int,
    )
    missing_alpha_qnums = sorted(new_alpha_qnums | set(stale_alpha_qnums), key=int)
    pending_questions_path = RELIABILITY_DIR / f"_pending_{naming.judge_tag(judge)}__{bver}.txt"

    def _prepare_stage_2():
        if reliability_target.exists():
            backup = reliability_target.with_suffix(
                f".json.bak-{datetime.now(timezone.utc):%Y%m%dT%H%M%S}")
            shutil.copyfile(reliability_target, backup)
            print(f"Backed up {reliability_target} to {backup} "
                 f"(compute_reliability's write is non-atomic, plan §5)")
            if stale_alpha_qnums:
                data = _json_get(reliability_target) or {}
                per_q = data.get("per_question", {})
                removed = [q for q in stale_alpha_qnums if per_q.pop(q, None) is not None]
                if removed:
                    # judge_alpha_reliability_nocontext.py's own resume logic
                    # unconditionally drops any qnum already present as a key
                    # in per_question, regardless of --questions -- so a
                    # stale entry has to be deleted here, not just listed as
                    # pending, or it would be silently re-skipped downstream.
                    substantive_artifacts.write_json(reliability_target, data)
                    print(f"Removed {len(removed)} stale per_question entries "
                         f"(content changed since seeding): {removed}")
        pending_questions_path.parent.mkdir(parents=True, exist_ok=True)
        pending_questions_path.write_text("\n".join(missing_alpha_qnums) + "\n", encoding="utf-8")

    if not missing_alpha_qnums:
        reason = "all pass/fail qnums already in per_question with matching content"
    else:
        reason = f"{len(new_alpha_qnums)} missing"
        if stale_alpha_qnums:
            reason += f" + {len(stale_alpha_qnums)} stale (content changed since seeding: {stale_alpha_qnums})"
        reason += " pass/fail reliability qnums"

    stages.append(Stage(
        2, "alpha_reliability", "instrument",
        skip=SkipResult(not missing_alpha_qnums, reason),
        argv=[py, "judge_alpha_reliability_nocontext.py", "--judge", judge,
             "--benchmark", str(benchmark_path), "--reasoning-effort", judge_effort,
             "--questions", f"@{pending_questions_path}"],
        pre_action=_prepare_stage_2,
        cwd=SCRIPT_DIR, est_calls=len(missing_alpha_qnums) * AVG_TRIALS_PER_ALPHA_Q,
    ))

    # ---- stage 3: fit_beta_regression_nocontext --------------------------
    pairs_path = substantive_artifacts.BETA_RELIABILITY_DIR / (
        f"gt_pairs_{naming.judge_tag(judge)}__{args.seed_reliability_from}.jsonl")
    beta_draws_path = substantive_artifacts.beta_draws_path(judge, benchmark_path)
    stages.append(Stage(
        3, "beta_regression", "instrument",
        skip=SkipResult(_newer(beta_draws_path, pairs_path),
                        f"{beta_draws_path.name} newer than {pairs_path.name}"
                        if _newer(beta_draws_path, pairs_path)
                        else f"{beta_draws_path.name} missing or stale vs {pairs_path.name}"),
        argv=[py, "fit_beta_regression_nocontext.py", str(pairs_path),
             "--benchmark", str(benchmark_path), "--save-draws", str(beta_draws_path)],
        cwd=SCRIPT_DIR, est_fits=1,
    ))

    # ---- stage 4: bt_context_scoring anchor-fit ---------------------------
    anchors_file = bt_artifacts.anchors_path(tag)
    fitted_pc_qnums: set[str] = set()
    if anchors_file.exists():
        fits, _meta = load_anchor_fits(anchors_file)
        fitted_pc_qnums = set(fits)
    missing_anchor_qnums = sorted(pc_qnums - fitted_pc_qnums, key=int)
    stages.append(Stage(
        4, "anchor_fit", "instrument",
        skip=SkipResult(not missing_anchor_qnums,
                        "every partial-credit qnum has a fitted anchor" if not missing_anchor_qnums
                        else f"{len(missing_anchor_qnums)} partial-credit qnums missing an anchor fit"),
        argv=[py, "bt_context_scoring.py", "anchor-fit", "--judge", bt_judge,
             "--judge-effort", judge_effort, "--benchmark", str(benchmark_path),
             "--prior-scale", str(prior_scale), "--prompt-mode", prompt_mode],
        cwd=SCRIPT_DIR, est_calls=len(missing_anchor_qnums) * AVG_CALLS_PER_ANCHOR_Q,
    ))

    # ---- stage 5: bt_context_scoring loo ----------------------------------
    loo_data = _json_get(bt_artifacts.loo_path(tag))
    existing_loo_qids = {r["qid"] for r in (loo_data or {}).get("records", [])}
    subsample_qnums: list[str] = []
    if pc_qnums:
        subsample_qnums = _bt_stratified_subsample(
            routing.partial, args.loo_subsample, ["question_category", "n_gt"], seed=20260728)
    missing_loo_qnums = sorted(set(subsample_qnums) - existing_loo_qids, key=int)
    stages.append(Stage(
        5, "loo", "instrument",
        skip=SkipResult(not missing_loo_qnums and bool(subsample_qnums),
                        "subsample qids already all in the LOO artifact" if not missing_loo_qnums and subsample_qnums
                        else f"{len(missing_loo_qnums)}/{len(subsample_qnums)} subsample qnums missing LOO records"),
        argv=[py, "bt_context_scoring.py", "loo", "--judge", bt_judge,
             "--judge-effort", judge_effort, "--benchmark", str(benchmark_path),
             "--prior-scale", str(prior_scale), "--prompt-mode", prompt_mode,
             "--subsample", str(args.loo_subsample), "--stratify-by", "question_category,n_gt"],
        cwd=SCRIPT_DIR,
        est_calls=len(missing_loo_qnums) * AVG_CALLS_PER_LOO_Q,
        est_fits=len(missing_loo_qnums) * AVG_FITS_PER_LOO_Q,
    ))

    # ---- stage 6: bt_context_scoring validate -----------------------------
    results_path = bt_artifacts.results_path(tag)
    loo_path = bt_artifacts.loo_path(tag)
    stages.append(Stage(
        6, "validate", "instrument",
        skip=SkipResult(_newer(results_path, loo_path),
                        f"{results_path.name} newer than {loo_path.name}"
                        if _newer(results_path, loo_path)
                        else f"{results_path.name} missing or stale vs {loo_path.name}"),
        argv=[py, "bt_context_scoring.py", "validate", "--judge", bt_judge,
             "--judge-effort", judge_effort, "--benchmark", str(benchmark_path),
             "--prior-scale", str(prior_scale), "--prompt-mode", prompt_mode],
        cwd=SCRIPT_DIR,
    ))

    # ---- stage 7: bt_context_scoring calibrate ----------------------------
    calib_draws_path = substantive_artifacts.calib_draws_path(tag)
    calibrate_argv = [py, "bt_context_scoring.py", "calibrate", "--judge", bt_judge,
                      "--judge-effort", judge_effort, "--benchmark", str(benchmark_path),
                      "--prior-scale", str(prior_scale), "--prompt-mode", prompt_mode,
                      "--bootstrap", "1000", "--draws-out", str(calib_draws_path)]
    if args.pool_pilot:
        if args.pilot_labels and Path(args.pilot_labels).exists():
            calibrate_argv += ["--extra-labels", str(args.pilot_labels)]
        else:
            print("note: --pool-pilot requested but no --pilot-labels file found "
                 "(emit one with `bt_context_scoring.py emit-pilot-labels` first); "
                 "running calibrate without pilot pooling.")
    stages.append(Stage(
        7, "calibrate", "instrument",
        skip=SkipResult(_newer(calib_draws_path, loo_path),
                        f"{calib_draws_path.name} newer than {loo_path.name}"
                        if _newer(calib_draws_path, loo_path)
                        else f"{calib_draws_path.name} missing or stale vs {loo_path.name}"),
        argv=calibrate_argv, cwd=SCRIPT_DIR,
    ))

    # ---- stage 8: free_generation ------------------------------------------
    ctag = naming.candidate_tag(candidate_label)
    free_gen_path = GENERATED_ANSWERS_DIR / f"free_gen_{ctag}__{bver}.json"
    free_gen_data = _json_get(free_gen_path)
    n_answered = len((free_gen_data or {}).get("answers", {}))
    stages.append(Stage(
        8, "free_generation", "candidate",
        skip=SkipResult(n_answered >= total_questions,
                        f"{free_gen_path.name} already has all {total_questions} answers"
                        if n_answered >= total_questions
                        else f"{free_gen_path.name} has {n_answered}/{total_questions} answers"),
        argv=[py, "free_generation.py", candidate, str(benchmark_path),
             "--reasoning-effort", candidate_effort, "--candidate-label", candidate_label],
        cwd=SCRIPT_DIR, est_calls=max(total_questions - n_answered, 0),
    ))

    # ---- stage 9: judge_scoring_nocontext --route pass-fail ---------------
    scored_path = SCORED_DIR / naming.scored_answers_filename(
        judge, candidate_label, bver, candidate_effort, judge_effort)
    scored_data = _json_get(scored_path)
    scored_pf_qnums = set((scored_data or {}).get("question_fit", {}))
    missing_pf_scored = sorted(pf_qnums - scored_pf_qnums, key=int)
    stages.append(Stage(
        9, "judge_scoring", "candidate",
        skip=SkipResult(not missing_pf_scored,
                        f"{scored_path.name} already has all {len(pf_qnums)} question_fit keys"
                        if not missing_pf_scored
                        else f"{scored_path.name} missing {len(missing_pf_scored)}/{len(pf_qnums)} question_fit keys"),
        argv=[py, "judge_scoring_nocontext.py", str(free_gen_path), "--judge", judge,
             "--benchmark", str(benchmark_path), "--reasoning-effort", judge_effort,
             "--route", "pass-fail"],
        cwd=SCRIPT_DIR, est_calls=len(missing_pf_scored),
    ))

    # ---- stage 10: bt_context_scoring score --save-delta-draws ------------
    bt_scored_path = scored_path.parent / f"{scored_path.stem}_btcontext.json"
    bt_scored_data = _json_get(bt_scored_path)
    scored_pc_qnums = set((bt_scored_data or {}).get("context_fit", {}))
    missing_pc_scored = sorted(pc_qnums - scored_pc_qnums, key=int)
    delta_draws_path = substantive_artifacts.delta_draws_path(tag, candidate_label, candidate_effort)
    stage10_done = not missing_pc_scored and delta_draws_path.exists()
    stages.append(Stage(
        10, "bt_score", "candidate",
        skip=SkipResult(stage10_done,
                        "all context_fit keys present and delta draws exist" if stage10_done
                        else f"{len(missing_pc_scored)}/{len(pc_qnums)} context_fit keys missing"
                             f"{'' if delta_draws_path.exists() else '; delta draws missing'}"),
        argv=[py, "bt_context_scoring.py", "score", "--judge", bt_judge,
             "--judge-effort", judge_effort, "--benchmark", str(benchmark_path),
             "--prior-scale", str(prior_scale), "--prompt-mode", prompt_mode,
             "--scored-file", str(scored_path), "--free-gen", str(free_gen_path),
             "--save-delta-draws"],
        cwd=SCRIPT_DIR, est_calls=len(missing_pc_scored) * AVG_CALLS_PER_BT_SCORE_Q,
    ))

    # ---- stage 11: score_substantive score --------------------------------
    stages.append(Stage(
        11, "score_substantive", "candidate",
        skip=SkipResult(False, "never skipped (cheap; always rewrites report + ledger)"),
        argv=[py, "score_substantive.py", "score", "--scored-file", str(scored_path),
             "--benchmark", str(benchmark_path)],
        cwd=SCRIPT_DIR,
    ))

    # ---- stage 12: style refresh (batch, opt-in) --------------------------
    style_dir = SCRIPT_DIR.parent / "stylejudge"
    cohort_stems = sorted(p.stem for p in GENERATED_ANSWERS_DIR.glob("free_gen_*.json"))
    cohort_id = hashlib.sha256("\n".join(cohort_stems).encode("utf-8")).hexdigest()[:16]

    def _refresh_style(runner):
        answers_q = style_dir / "answers_q.jsonl"
        benchmark_answers = style_dir / "benchmark_answers.jsonl"
        report_path = SCRIPT_DIR / "results" / f"style_report_{cohort_id}.md"
        stats_out = SCRIPT_DIR / "results" / f"style_report_stats_{cohort_id}.json"
        (SCRIPT_DIR / "results").mkdir(parents=True, exist_ok=True)
        steps = [
            [py, "diagnose_e1_stats.py", "sample-benchmark-answers", "--out", str(benchmark_answers)],
            [py, "typicality.py", "qscore", "--answers", str(benchmark_answers), "--out", str(answers_q)],
            [py, "typicality.py", "model-report", "--answers-q", str(answers_q),
             "--report", str(report_path), "--stats-out", str(stats_out)],
        ]
        for step_argv in steps:
            result = runner(step_argv, cwd=str(style_dir))
            if getattr(result, "returncode", 0) != 0:
                sys.exit(f"style refresh step failed: {' '.join(step_argv)}")
        print(f"Style cohort {cohort_id}: wrote {stats_out}.")
        print("Ledger style columns were NOT auto-updated -- the join between "
             "typicality.py's per-model stats and the ledger's candidate_label/"
             "candidate_model columns is not yet wired (plan §5's style_cohort_id "
             f"is {cohort_id}; update results/chronologic_scores.csv by hand or "
             "extend this stage once that join is verified).")

    stages.append(Stage(
        12, "style_refresh", "batch",
        skip=SkipResult(not args.refresh_style, "opt-in via --refresh-style"),
        argv=None, action=_refresh_style, cwd=style_dir,
        note=f"style_cohort_id={cohort_id}",
    ))

    return stages


# ---------------------------------------------------------------------------
# execute
# ---------------------------------------------------------------------------

def execute(stages: list[Stage], *, runner=subprocess.run, dry_run: bool = False,
           force: tuple[str, ...] = ()) -> bool:
    """Run `stages` in order. Returns True if every stage ran or was skipped
    without failure; False if a stage failed (and stops there).

    `runner` takes an argv list and a `cwd` kwarg, mirroring subprocess.run's
    signature, and must return an object with a `.returncode` attribute --
    tests inject a fake to avoid ever spawning a real process.
    """
    force_tokens = {str(f) for f in force}
    for stage in stages:
        forced = any(_stage_matches(stage, t) for t in force_tokens)
        if stage.skip.skip and not forced:
            print(f"[{stage.number}] {stage.name}: SKIP -- {stage.skip.reason}")
            continue

        label = "RUN (forced)" if forced and stage.skip.skip else "RUN"
        print(f"[{stage.number}] {stage.name}: {label}")
        if dry_run:
            continue

        if stage.pre_action is not None:
            stage.pre_action()

        if stage.action is not None:
            stage.action(runner)
            continue

        result = runner(stage.argv, cwd=str(stage.cwd))
        rc = getattr(result, "returncode", 0)
        if rc != 0:
            print(f"\nStage {stage.number} ({stage.name}) failed (exit {rc}).")
            print(f"Resume with:\n  {stage.resume_cmd()}")
            return False
    return True


# ---------------------------------------------------------------------------
# cost table
# ---------------------------------------------------------------------------

def total_estimated_cost(stages: list[Stage]) -> tuple[int, int]:
    """(calls, fits) summed over stages that would actually run (not skipped)."""
    running = [s for s in stages if not s.skip.skip]
    return sum(s.est_calls for s in running), sum(s.est_fits for s in running)


def print_stage_plan(stages: list[Stage]) -> None:
    print(f"{'#':>2}  {'stage':<18} {'scope':<10} {'action':<7} {'est_calls':>10} {'est_fits':>9}  reason")
    for s in stages:
        action = "skip" if s.skip.skip else "run"
        note = f" ({s.note})" if s.note else ""
        print(f"{s.number:>2}  {s.name:<18} {s.scope:<10} {action:<7} {s.est_calls:>10} {s.est_fits:>9}  "
             f"{s.skip.reason}{note}")
    total_calls, total_fits = total_estimated_cost(stages)
    print(f"\nEstimated total (stages that would run): {total_calls} judge calls, {total_fits} PyMC fits.")
    print("Estimates are approximate ratios from plan §8's worked example, not measured costs.")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--candidate", required=True, metavar="MODEL_ID")
    parser.add_argument("--candidate-label", default=None, metavar="LABEL")
    parser.add_argument("--benchmark", default=None, metavar="PATH")
    parser.add_argument("--judge", default=DEFAULT_JUDGE)
    parser.add_argument("--bt-judge", default=DEFAULT_BT_JUDGE)
    parser.add_argument("--judge-effort", default="medium", choices=["none", "low", "medium", "high"])
    parser.add_argument("--candidate-effort", default="none",
                        choices=["none", "minimal", "low", "medium", "high"])
    parser.add_argument("--prior-scale", type=float, default=3.0)
    parser.add_argument("--prompt-mode", default="rationales")
    parser.add_argument("--loo-subsample", type=int, default=80)
    parser.add_argument("--pool-pilot", dest="pool_pilot", action="store_true", default=True)
    parser.add_argument("--no-pool-pilot", dest="pool_pilot", action="store_false")
    parser.add_argument("--pilot-labels", default=None, metavar="PATH",
                        help="Namespaced pilot LOO labels (see `bt_context_scoring.py "
                             "emit-pilot-labels`); used with --pool-pilot.")
    parser.add_argument("--refresh-style", action="store_true")
    parser.add_argument("--only", default=None, metavar="STAGE[,...]")
    parser.add_argument("--stop-after", default=None, metavar="STAGE")
    parser.add_argument("--force", default=None, metavar="STAGE[,...]")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--python", default=DEFAULT_PYTHON)
    parser.add_argument("--seed-reliability-from", default="0.4", metavar="VERSION",
                        help="Benchmark version whose reliability/gt-pairs files seed a "
                             "freshly-versioned run (plan §5: '0.4' as of this build).")
    return parser


def main():
    args = build_parser().parse_args()

    check_pymc_importable(args.python)

    benchmark_path = Path(args.benchmark) if args.benchmark else naming.latest_benchmark(BOOKSAMPLE_DIR)
    bver = naming.benchmark_version(benchmark_path)
    check_judge_effort_matches_seed(args.judge, bver, args.judge_effort, args.seed_reliability_from)

    stages = build_stages(args)
    stages = select_stages(stages, only=args.only, stop_after=args.stop_after)

    print_stage_plan(stages)
    if args.dry_run:
        return

    force = tuple(t.strip() for t in (args.force or "").split(",") if t.strip())
    ok = execute(stages, dry_run=False, force=force)
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
