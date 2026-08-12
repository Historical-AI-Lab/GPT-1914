#!/usr/bin/env python3
"""model_stable.py — Phase D2 §4: the generator stable, as data.

The negatives pool is only as good as its generator diversity. A detector trained
on one family's output partly measures "is this a familiar generator" rather than
"is this synthetic", so this module encodes three things the rest of D2 reads:

1. **Which models generate**, at which endpoint, for which modalities.
2. **Family-level holdout.** Google, Cohere, Amazon, AI21 and OpenAI's top tier
   are `eval_holdout`: they generate once, are labelled `split_role="eval_holdout"`,
   and never enter a training round — including the Phase E hard-negative rounds.
   `assert_holdout_integrity()` is the guard; the tests call it too.
3. **Quota arithmetic.** How the 32,000-row negative pool divides across the five
   modalities and then across models, given whatever the reuse and Talkie tiers
   actually delivered.

Prices are $/M tokens as listed in the OpenRouter catalogue on 2026-08-11.
They are recorded for budgeting only; `pricing-check` compares them against the
live catalogue and reports drift. Nothing here makes an API call except
`pricing-check`, which reads the public models endpoint (no key required).

CLI
    python model_stable.py list [--role R] [--modality M] [--format table|json]
    python model_stable.py quotas [--total N] [--reuse-infill N] ... [--format ...]
    python model_stable.py pricing-check [--threshold 0.20]
"""

import argparse
import json
import sys
from dataclasses import asdict, dataclass, field

# ---------------------------------------------------------------------------
# Modalities
# ---------------------------------------------------------------------------

INFILL = "infill"
CONTINUATION = "continuation"
PARAPHRASE = "paraphrase"
CONSTRAINED = "constrained_generation"
FEW_SHOT = "few_shot"

MODALITIES = (INFILL, CONTINUATION, PARAPHRASE, CONSTRAINED, FEW_SHOT)

#: Spec-mandated mix of the negative pool. Must sum to 1.0.
MODALITY_SHARES = {
    INFILL: 0.40,
    CONTINUATION: 0.20,
    PARAPHRASE: 0.10,
    CONSTRAINED: 0.20,
    FEW_SHOT: 0.10,
}

DEFAULT_TOTAL = 32000

# Tier row counts fixed by the plan (§3, §4.2, §4.3).
DEFAULT_REUSE_CAP = 6400
DEFAULT_TALKIE_CONTINUATION = 1600
DEFAULT_TALKIE_FEWSHOT = 400
DEFAULT_PSEUDO_BASE_CONTINUATION = 3200
DEFAULT_EVAL_HOLDOUT_TOTAL = 2000

# `bertclassify/imitation/` holds ~20,678 infill lines against ~2,200 continuation
# lines once Google files are dropped. The reuse cap is split in that proportion
# unless the caller overrides it with what `reuse_bertclassify.py` actually wrote.
DEFAULT_REUSE_INFILL = 5760
DEFAULT_REUSE_CONTINUATION = 640

# Roles
TRAIN = "train"
EVAL_HOLDOUT = "eval_holdout"

# Endpoints
CHAT = "chat"
COMPLETIONS = "completions"
LOCAL = "local"

#: Chat models that absorb the continuation rows the base tiers do not cover.
#:
#: §4.2 routes "~3/4" of the continuation quota to the pseudo-base and Talkie
#: tiers, which leaves ~1/4 unassigned: the §4.1 table lists no chat model with
#: `continuation` among its primary modalities, so without this the remainder
#: would silently vanish and the tiers would not sum to the pool size. Naming the
#: absorbers explicitly is deliberate — an implicit "fall back to everything"
#: rule would quietly reshape the mix whenever a modality ran short. Instruct-tuned
#: continuations are wanted in the mix anyway; they are a different failure mode
#: from raw-prefix continuation and the detector should see both.
CHAT_CONTINUATION_MODELS = (
    "anthropic/claude-sonnet-5",
    "openai/gpt-5.6-terra",
    "meta-llama/llama-4-maverick",
    "deepseek/deepseek-v4-flash",
    "qwen/qwen3.7-plus",
    "moonshotai/kimi-k2.5",
)

#: Families frozen out of every training round (§4.4). Membership is checked by
#: `ModelSpec.family`, so a new Google model added to the stable inherits the
#: holdout automatically.
EVAL_ONLY_FAMILIES = frozenset({"google", "cohere", "amazon", "ai21"})


@dataclass(frozen=True)
class ModelSpec:
    """One generator in the stable."""

    model_id: str
    family: str
    role: str
    endpoint: str
    tier: str
    modalities: tuple
    price_in: float          # $/M input tokens, as listed 2026-08-11
    price_out: float         # $/M output tokens
    reasoning_effort: str = None
    weight: float = 1.0      # relative share within each modality it serves
    note: str = ""
    available: bool = True   # False once `smoke` proves it cannot be called

    @property
    def is_holdout(self):
        return self.role == EVAL_HOLDOUT


# ---------------------------------------------------------------------------
# §4.1 Training generators — chat endpoint
# ---------------------------------------------------------------------------

TRAIN_MODELS = [
    ModelSpec("anthropic/claude-sonnet-5", "anthropic", TRAIN, CHAT, "frontier_it",
              (INFILL, CONSTRAINED), 2.00, 10.00),
    ModelSpec("openai/gpt-5.6-terra", "openai", TRAIN, CHAT, "frontier_it",
              (INFILL, PARAPHRASE), 1.00, 6.00,
              note="also the constrained-generation summarizer (§5.2)"),
    # Reasoning is mandatory on this endpoint and cannot be disabled (400 from
    # the smoke test with effort "none"), so it is pinned low like the other
    # thinking models rather than dropped.
    ModelSpec("openai/gpt-oss-120b", "openai", TRAIN, CHAT, "open_weight",
              (INFILL, FEW_SHOT), 0.03, 0.17, reasoning_effort="low"),
    ModelSpec("x-ai/grok-4.3", "x-ai", TRAIN, CHAT, "frontier_it",
              (CONSTRAINED, PARAPHRASE), 1.25, 2.50),
    ModelSpec("deepseek/deepseek-v4-flash", "deepseek", TRAIN, CHAT, "it",
              (INFILL, FEW_SHOT), 0.14, 0.28),
    ModelSpec("z-ai/glm-5.2", "z-ai", TRAIN, CHAT, "it",
              (INFILL, CONSTRAINED), 0.56, 1.76),
    ModelSpec("moonshotai/kimi-k2.5", "moonshotai", TRAIN, CHAT, "it",
              (INFILL, PARAPHRASE), 0.57, 2.85),
    ModelSpec("minimax/minimax-m2.5", "minimax", TRAIN, CHAT, "thinking",
              (CONSTRAINED,), 0.22, 0.90, reasoning_effort="low"),
    ModelSpec("qwen/qwen3.7-plus", "qwen", TRAIN, CHAT, "it",
              (INFILL, CONSTRAINED), 0.32, 1.28),
    ModelSpec("qwen/qwen3.5-9b", "qwen", TRAIN, CHAT, "small_it",
              (INFILL, FEW_SHOT), 0.10, 0.15,
              note="continuity with bertclassify/imitation"),
    ModelSpec("qwen/qwen3-235b-a22b-thinking-2507", "qwen", TRAIN, CHAT, "thinking",
              (INFILL,), 0.23, 2.30, reasoning_effort="low"),
    ModelSpec("meta-llama/llama-4-maverick", "meta-llama", TRAIN, CHAT, "it",
              (INFILL, PARAPHRASE), 0.20, 0.70),
    ModelSpec("mistralai/mistral-small-2603", "mistralai", TRAIN, CHAT, "it",
              (FEW_SHOT, PARAPHRASE), 0.15, 0.60),
    ModelSpec("nvidia/nemotron-3-super-120b-a12b", "nvidia", TRAIN, CHAT, "it",
              (CONSTRAINED,), 0.085, 0.40),
    # Listed in the catalogue but has no serving endpoint: "No endpoints found"
    # (404) on the 2026-08-11 smoke test. Kept here rather than deleted so the
    # record shows the fully-open tier was sought; its few-shot quota
    # redistributes automatically among the remaining few-shot models.
    ModelSpec("allenai/olmo-3-32b-think", "allenai", TRAIN, CHAT, "fully_open_thinking",
              (FEW_SHOT,), 0.15, 0.50, reasoning_effort="low", available=False,
              note="404 no endpoints 2026-08-11"),
]

# ---------------------------------------------------------------------------
# §4.2 Pseudo-base tier — completion endpoint
# ---------------------------------------------------------------------------
# OpenRouter no longer lists true base models. The substitute is /v1/completions,
# which skips the chat template and the assistant persona: the model sees a raw
# period prefix and continues it. Candidates are the models exposing a non-null
# architecture.instruct_type.
#
# UNVERIFIED: the inference `instruct_type != null => /v1/completions works` is
# reconstructed from the catalogue schema. `elicit_negatives.py smoke` must
# confirm it per model before quota is assigned; any model that 404s is dropped
# and its share redistributed within the tier by `allocate_tier()`.

PSEUDO_BASE_MODELS = [
    ModelSpec("nousresearch/hermes-3-llama-3.1-405b", "nousresearch", TRAIN,
              COMPLETIONS, "pseudo_base", (CONTINUATION,), 1.00, 1.00),
    ModelSpec("meta-llama/llama-3.3-70b-instruct", "meta-llama", TRAIN,
              COMPLETIONS, "pseudo_base", (CONTINUATION,), 0.10, 0.32),
    ModelSpec("mistralai/mixtral-8x22b-instruct", "mistralai", TRAIN,
              COMPLETIONS, "pseudo_base", (CONTINUATION,), 2.00, 6.00),
    ModelSpec("mistralai/mistral-nemo", "mistralai", TRAIN,
              COMPLETIONS, "pseudo_base", (CONTINUATION,), 0.019, 0.030),
    ModelSpec("deepseek/deepseek-v3.1-terminus", "deepseek", TRAIN,
              COMPLETIONS, "pseudo_base", (CONTINUATION,), 0.27, 0.95),
    ModelSpec("openai/gpt-3.5-turbo-instruct", "openai", TRAIN,
              COMPLETIONS, "pseudo_base", (CONTINUATION,), 1.50, 2.00,
              note="the only completion-native survivor in the catalogue"),
]

# ---------------------------------------------------------------------------
# §4.3 True base tier — Talkie on Delta
# ---------------------------------------------------------------------------
# The only genuinely untuned base model available, and the only generator
# anywhere in the stable actually *trained* on pre-1931 English — so the hardest
# negative source in the pool. Free compute; needs >=28 GB VRAM in bf16.

TALKIE_MODEL = ModelSpec("talkie-1930-13b-base", "talkie", TRAIN, LOCAL, "true_base",
                         (CONTINUATION, FEW_SHOT), 0.0, 0.0,
                         note="run on Delta; memorization risk, §5.4 leakage guard applies")

# ---------------------------------------------------------------------------
# §4.4 Eval-only families — frozen now, never in any training round
# ---------------------------------------------------------------------------

EVAL_MODELS = [
    ModelSpec("google/gemini-3.1-pro-preview", "google", EVAL_HOLDOUT, CHAT, "frontier_it",
              (INFILL, CONSTRAINED, PARAPHRASE), 1.25, 10.00, reasoning_effort="low",
              note="large frontier family holdout — the strictest transfer test; "
                   "reasoning mandatory on this endpoint"),
    ModelSpec("google/gemma-4-31b-it", "google", EVAL_HOLDOUT, CHAT, "open_weight",
              (INFILL, FEW_SHOT), 0.10, 0.30),
    ModelSpec("cohere/command-a", "cohere", EVAL_HOLDOUT, CHAT, "it",
              (INFILL, PARAPHRASE), 2.50, 10.00),
    ModelSpec("amazon/nova-pro-v1", "amazon", EVAL_HOLDOUT, CHAT, "it",
              (CONSTRAINED, PARAPHRASE), 0.80, 3.20),
    # AI21's gateway was retired: the provider returns 410 "This API has been
    # retired". Catalogue listing is not proof of availability -- which is what
    # the smoke gate is for.
    ModelSpec("ai21/jamba-large-1.7", "ai21", EVAL_HOLDOUT, CHAT, "it",
              (INFILL, FEW_SHOT), 2.00, 8.00, available=False,
              note="410 provider retired 2026-08-11"),
    ModelSpec("openai/gpt-5.6-sol", "openai", EVAL_HOLDOUT, CHAT, "frontier_it",
              (INFILL, CONSTRAINED), 5.00, 25.00,
              note="within-family check: OpenAI's top tier held out while "
                   "gpt-5.6-terra trains"),
]

ALL_MODELS = TRAIN_MODELS + PSEUDO_BASE_MODELS + [TALKIE_MODEL] + EVAL_MODELS


# ---------------------------------------------------------------------------
# Lookup
# ---------------------------------------------------------------------------

def by_id(model_id):
    """Return the ModelSpec with this id, or None."""
    for m in ALL_MODELS:
        if m.model_id == model_id:
            return m
    return None


def select(role=None, modality=None, endpoint=None, models=None):
    """Filter the stable. `role=None` means every role."""
    out = list(models if models is not None else ALL_MODELS)
    if role and role != "all":
        out = [m for m in out if m.role == role]
    if modality:
        out = [m for m in out if modality in m.modalities]
    if endpoint:
        out = [m for m in out if m.endpoint == endpoint]
    return out


def assert_holdout_integrity(models=None):
    """Raise if an eval-only family is anywhere near a training role.

    Called by the tests and at the top of every `elicit_negatives.py` run. The
    holdout is the whole point of §4.4: if it leaks, the Phase E transfer numbers
    measure nothing.
    """
    problems = []
    for m in (models if models is not None else ALL_MODELS):
        if m.family in EVAL_ONLY_FAMILIES and m.role != EVAL_HOLDOUT:
            problems.append(f"{m.model_id}: family '{m.family}' is eval-only "
                            f"but role is '{m.role}'")
        if m.role not in (TRAIN, EVAL_HOLDOUT):
            problems.append(f"{m.model_id}: unknown role '{m.role}'")
        for mod in m.modalities:
            if mod not in MODALITIES:
                problems.append(f"{m.model_id}: unknown modality '{mod}'")
    if problems:
        raise ValueError("holdout integrity violated:\n  " + "\n  ".join(problems))
    return True


# ---------------------------------------------------------------------------
# Quota arithmetic
# ---------------------------------------------------------------------------

def largest_remainder(total, weights):
    """Apportion `total` integer units over `weights` (a dict) exactly.

    Standard largest-remainder method: floor everything, then hand the leftover
    units to the largest fractional parts. Guarantees the result sums to `total`,
    which naive rounding does not.
    """
    if total <= 0 or not weights:
        return {k: 0 for k in weights}
    denom = sum(weights.values())
    if denom <= 0:
        return {k: 0 for k in weights}
    exact = {k: total * w / denom for k, w in weights.items()}
    out = {k: int(v) for k, v in exact.items()}
    leftover = total - sum(out.values())
    order = sorted(weights, key=lambda k: (exact[k] - out[k], k), reverse=True)
    for i in range(leftover):
        out[order[i % len(order)]] += 1
    return out


def modality_totals(total=DEFAULT_TOTAL):
    """The spec's 40/20/10/20/10 split of the negative pool, as exact integers."""
    return largest_remainder(total, dict(MODALITY_SHARES))


def allocate_tier(quota, models):
    """Split one modality's quota across models by weight."""
    if not models:
        return {}
    return largest_remainder(quota, {m.model_id: m.weight for m in models})


def quota_plan(total=DEFAULT_TOTAL,
               reuse_infill=DEFAULT_REUSE_INFILL,
               reuse_continuation=DEFAULT_REUSE_CONTINUATION,
               talkie_continuation=DEFAULT_TALKIE_CONTINUATION,
               talkie_fewshot=DEFAULT_TALKIE_FEWSHOT,
               pseudo_base_continuation=DEFAULT_PSEUDO_BASE_CONTINUATION,
               available_pseudo_base=None,
               train_models=None):
    """Build the full row-count plan for the negative pool.

    The three non-OpenRouter tiers are subtracted from their modalities first,
    and whatever remains is what `elicit_negatives.py run` must actually call for.
    Passing the *measured* reuse and Talkie counts (rather than the defaults)
    keeps the plan honest after those stages have run.

    Args:
        total: size of the negative pool including every tier.
        reuse_infill / reuse_continuation: rows `reuse_bertclassify.py` emitted.
        talkie_continuation / talkie_fewshot: rows the Delta job emitted.
        pseudo_base_continuation: continuation rows routed to /v1/completions.
        available_pseudo_base: model ids that passed the smoke test. None means
            "all of them"; a model that 404s is dropped here and its share is
            redistributed within the tier.
        train_models: override the chat-model list (tests).

    Returns:
        dict with `modality_totals`, `tiers`, `openrouter_chat` (per-modality and
        per-model row counts), `openrouter_completions`, and `checks`.
    """
    totals = modality_totals(total)
    chat_models = [m for m in (train_models if train_models is not None
                               else TRAIN_MODELS) if m.available]

    pseudo = [m for m in PSEUDO_BASE_MODELS if m.available]
    if available_pseudo_base is not None:
        allowed = set(available_pseudo_base)
        pseudo = [m for m in pseudo if m.model_id in allowed]

    # Tier subtractions, modality by modality.
    reuse = {INFILL: reuse_infill, CONTINUATION: reuse_continuation}
    talkie = {CONTINUATION: talkie_continuation, FEW_SHOT: talkie_fewshot}
    base_cont = pseudo_base_continuation if pseudo else 0

    remaining = {}
    for mod in MODALITIES:
        taken = reuse.get(mod, 0) + talkie.get(mod, 0)
        if mod == CONTINUATION:
            taken += base_cont
        remaining[mod] = max(0, totals[mod] - taken)

    # Chat models cover every modality except what the completion tier owns.
    chat_alloc = {}
    for mod in MODALITIES:
        serving = [m for m in chat_models if mod in m.modalities]
        if mod == CONTINUATION:
            serving = [m for m in chat_models
                       if m.model_id in CHAT_CONTINUATION_MODELS]
        chat_alloc[mod] = allocate_tier(remaining[mod], serving)

    completions_alloc = allocate_tier(base_cont, pseudo)

    per_model = {}
    for mod, alloc in chat_alloc.items():
        for mid, n in alloc.items():
            per_model.setdefault(mid, {})[mod] = n
    for mid, n in completions_alloc.items():
        per_model.setdefault(mid, {})[CONTINUATION] = n

    n_chat = sum(sum(a.values()) for a in chat_alloc.values())
    plan = {
        "total": total,
        "modality_totals": totals,
        "tiers": {
            "bertclassify_reuse": reuse_infill + reuse_continuation,
            "talkie_local": talkie_continuation + talkie_fewshot,
            "openrouter_completions": base_cont,
            "openrouter_chat": n_chat,
        },
        "remaining_after_tiers": remaining,
        "openrouter_chat": chat_alloc,
        "openrouter_completions": completions_alloc,
        "per_model": per_model,
        "eval_holdout_total": DEFAULT_EVAL_HOLDOUT_TOTAL,
        "unavailable": [m.model_id for m in ALL_MODELS if not m.available],
    }
    plan["tiers"]["sum"] = sum(v for k, v in plan["tiers"].items() if k != "sum")
    plan["checks"] = {
        "modality_totals_sum_to_total": sum(totals.values()) == total,
        "tiers_sum_to_total": plan["tiers"]["sum"] == total,
        "openrouter_api_calls": n_chat + base_cont,
        "dropped_pseudo_base": [m.model_id for m in PSEUDO_BASE_MODELS
                                if m not in pseudo],
    }
    return plan


def estimate_cost(plan, tokens_in=250, tokens_out=110):
    """Rough $ estimate for a quota plan, per model and in total.

    Deliberately crude — the runner tracks actual usage. This exists so
    `quotas` can show where the money would go before any of it is spent.
    """
    per_model = {}
    for mid, mods in plan["per_model"].items():
        spec = by_id(mid)
        if spec is None or spec.endpoint == LOCAL:
            continue
        n = sum(mods.values())
        cost = (n * tokens_in * spec.price_in + n * tokens_out * spec.price_out) / 1e6
        per_model[mid] = round(cost, 2)
    return {"per_model": per_model, "total_usd": round(sum(per_model.values()), 2)}


# ---------------------------------------------------------------------------
# pricing-check
# ---------------------------------------------------------------------------

def fetch_live_pricing(url="https://openrouter.ai/api/v1/models", timeout=30):
    """Fetch $/M in-out prices from the public catalogue. No API key needed."""
    import urllib.request

    with urllib.request.urlopen(url, timeout=timeout) as resp:
        payload = json.load(resp)
    out = {}
    for row in payload.get("data", []):
        pricing = row.get("pricing") or {}
        try:
            out[row["id"]] = (float(pricing.get("prompt", 0)) * 1e6,
                              float(pricing.get("completion", 0)) * 1e6)
        except (TypeError, ValueError):
            continue
    return out


def pricing_drift(live, threshold=0.20, models=None):
    """Compare recorded prices against `live`; return per-model drift rows."""
    rows = []
    for m in (models if models is not None else ALL_MODELS):
        if m.endpoint == LOCAL:
            continue
        if m.model_id not in live:
            rows.append({"model_id": m.model_id, "status": "missing_from_catalogue"})
            continue
        live_in, live_out = live[m.model_id]
        def drift(recorded, actual):
            if recorded == 0:
                return 0.0 if actual == 0 else float("inf")
            return (actual - recorded) / recorded
        d_in, d_out = drift(m.price_in, live_in), drift(m.price_out, live_out)
        status = "ok" if max(abs(d_in), abs(d_out)) <= threshold else "drift"
        rows.append({"model_id": m.model_id, "status": status,
                     "recorded": [m.price_in, m.price_out],
                     "live": [round(live_in, 4), round(live_out, 4)],
                     "drift_in": round(d_in, 3), "drift_out": round(d_out, 3)})
    return rows


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _print_table(rows, columns):
    widths = [max(len(str(c)), *(len(str(r.get(c, ""))) for r in rows)) if rows
              else len(str(c)) for c in columns]
    print("  ".join(str(c).ljust(w) for c, w in zip(columns, widths)))
    print("  ".join("-" * w for w in widths))
    for r in rows:
        print("  ".join(str(r.get(c, "")).ljust(w) for c, w in zip(columns, widths)))


def cmd_list(args):
    models = select(role=args.role, modality=args.modality)
    if args.format == "json":
        print(json.dumps([asdict(m) for m in models], indent=2, default=list))
        return
    rows = [{"model_id": m.model_id, "family": m.family, "role": m.role,
             "endpoint": m.endpoint, "tier": m.tier,
             "modalities": ",".join(m.modalities),
             "in": m.price_in, "out": m.price_out,
             "effort": m.reasoning_effort or ""} for m in models]
    _print_table(rows, ["model_id", "family", "role", "endpoint", "tier",
                        "modalities", "in", "out", "effort"])
    print(f"\n{len(models)} models; "
          f"{len({m.family for m in models})} families")


def cmd_quotas(args):
    plan = quota_plan(total=args.total,
                      reuse_infill=args.reuse_infill,
                      reuse_continuation=args.reuse_continuation,
                      talkie_continuation=args.talkie_continuation,
                      talkie_fewshot=args.talkie_fewshot,
                      pseudo_base_continuation=args.pseudo_base_continuation)
    plan["cost_estimate"] = estimate_cost(plan)
    if args.format == "json":
        print(json.dumps(plan, indent=2))
        return
    print("modality totals:")
    for mod, n in plan["modality_totals"].items():
        print(f"  {mod:24s} {n:6d}")
    print("\ntiers:")
    for tier, n in plan["tiers"].items():
        print(f"  {tier:24s} {n:6d}")
    print("\nper model:")
    rows = []
    for mid, mods in sorted(plan["per_model"].items()):
        spec = by_id(mid)
        rows.append({"model_id": mid, "endpoint": spec.endpoint if spec else "?",
                     "rows": sum(mods.values()),
                     "breakdown": ", ".join(f"{k}={v}" for k, v in mods.items() if v),
                     "est_usd": plan["cost_estimate"]["per_model"].get(mid, 0.0)})
    _print_table(rows, ["model_id", "endpoint", "rows", "breakdown", "est_usd"])
    print(f"\nOpenRouter calls: {plan['checks']['openrouter_api_calls']}")
    print(f"estimated cost:   ${plan['cost_estimate']['total_usd']}")
    print(f"checks:           {plan['checks']['modality_totals_sum_to_total']} / "
          f"{plan['checks']['tiers_sum_to_total']}")


def cmd_pricing_check(args):
    try:
        live = fetch_live_pricing()
    except Exception as exc:                                    # noqa: BLE001
        print(f"could not fetch live catalogue: {exc}", file=sys.stderr)
        return 1
    rows = pricing_drift(live, threshold=args.threshold)
    _print_table(rows, ["model_id", "status", "recorded", "live",
                        "drift_in", "drift_out"])
    bad = [r for r in rows if r["status"] != "ok"]
    print(f"\n{len(rows) - len(bad)}/{len(rows)} within {args.threshold:.0%}")
    return 0


def build_parser():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="command", required=True)

    lp = sub.add_parser("list", help="list the stable")
    lp.add_argument("--role", choices=[TRAIN, EVAL_HOLDOUT, "all"], default="all")
    lp.add_argument("--modality", choices=list(MODALITIES), default=None)
    lp.add_argument("--format", choices=["table", "json"], default="table")
    lp.set_defaults(func=cmd_list)

    qp = sub.add_parser("quotas", help="row counts per modality and model")
    qp.add_argument("--total", type=int, default=DEFAULT_TOTAL)
    qp.add_argument("--reuse-infill", type=int, default=DEFAULT_REUSE_INFILL)
    qp.add_argument("--reuse-continuation", type=int, default=DEFAULT_REUSE_CONTINUATION)
    qp.add_argument("--talkie-continuation", type=int, default=DEFAULT_TALKIE_CONTINUATION)
    qp.add_argument("--talkie-fewshot", type=int, default=DEFAULT_TALKIE_FEWSHOT)
    qp.add_argument("--pseudo-base-continuation", type=int,
                    default=DEFAULT_PSEUDO_BASE_CONTINUATION)
    qp.add_argument("--format", choices=["table", "json"], default="table")
    qp.set_defaults(func=cmd_quotas)

    pp = sub.add_parser("pricing-check", help="recorded prices vs. live catalogue")
    pp.add_argument("--threshold", type=float, default=0.20)
    pp.set_defaults(func=cmd_pricing_check)
    return ap


def main(argv=None):
    args = build_parser().parse_args(argv)
    assert_holdout_integrity()
    return args.func(args) or 0


if __name__ == "__main__":
    sys.exit(main())
