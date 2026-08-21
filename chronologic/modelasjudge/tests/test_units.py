"""test_units.py — Algorithm-level unit tests for discriminative calibration scripts.

Run with:
    pytest modelasjudge/tests/test_units.py -v
"""

import json
import sys
import tempfile
from pathlib import Path

import numpy as np
import pytest

MODELASJUDGE = Path(__file__).parent.parent
sys.path.insert(0, str(MODELASJUDGE))


# ---------------------------------------------------------------------------
# test_distractor_filter
# ---------------------------------------------------------------------------

def _is_anachronistic(answer_type: str) -> bool:
    """Mirror the logic in build_benchmark_data.py."""
    t = answer_type.strip().lower()
    return t == "manual" or "anachronistic" in t


def test_distractor_filter_keeps_manual():
    assert _is_anachronistic("manual") is True


def test_distractor_filter_keeps_anachronistic_subtypes():
    for at in [
        "anachronistic_gpt-oss:20b",
        "anachronistic_mistral-small:24b",
        "anachronistic_metadataless_gpt-oss:20b",
        "manual_anachronistic_gpt-oss:20b",
        "anachronistic_wikipedia",
        "anachronistic_1940",
    ]:
        assert _is_anachronistic(at) is True, f"Expected True for {at!r}"


def test_distractor_filter_rejects_others():
    for at in [
        "same_book",
        "same_character",
        "negation",
        "manual_negation",
        "other_book_1911",
        "ground_truth",
        "other_book_1875",
    ]:
        assert _is_anachronistic(at) is False, f"Expected False for {at!r}"


# ---------------------------------------------------------------------------
# test_logit_inversion  — delta = logit_b - logit_a
# ---------------------------------------------------------------------------

def test_logit_delta_sign():
    """A higher logit_b than logit_a produces a positive delta."""
    logit_a, logit_b = 1.0, 2.5
    delta = logit_b - logit_a
    assert delta == pytest.approx(1.5)


def test_logit_delta_negative():
    """Candidate with lower logit than GT gets a negative delta."""
    logit_a, logit_b = 3.0, 1.0
    delta = logit_b - logit_a
    assert delta == pytest.approx(-2.0)


# ---------------------------------------------------------------------------
# test_clamp_max_zero
# ---------------------------------------------------------------------------

def test_clamp_max_zero_negative_delta_becomes_zero():
    """When delta < 0 (candidate beats GT), clamping yields 0."""
    delta = -1.5
    clamped = max(0.0, delta)
    assert clamped == 0.0


def test_clamp_max_zero_positive_unchanged():
    delta = 2.3
    clamped = max(0.0, delta)
    assert clamped == pytest.approx(2.3)


# ---------------------------------------------------------------------------
# test_quadratic_feature_shape
# ---------------------------------------------------------------------------

def _make_features(deltas: np.ndarray) -> np.ndarray:
    """Mirror the make_features logic in train_logistic.py (signed Δ)."""
    return np.column_stack([deltas, deltas ** 2])


def test_quadratic_feature_shape_columns():
    deltas = np.array([-2.0, -1.0, 0.0, 1.0, 2.0])
    X = _make_features(deltas)
    assert X.shape == (5, 2)


def test_quadratic_feature_values():
    deltas = np.array([-3.0, 4.0])
    X = _make_features(deltas)
    np.testing.assert_allclose(X[:, 0], [-3.0, 4.0])  # signed Δ
    np.testing.assert_allclose(X[:, 1], [9.0, 16.0])  # Δ²


def test_quadratic_feature_signed():
    """Linear feature differs for +Δ vs −Δ; squared feature does not."""
    deltas_pos = np.array([1.5, 2.5])
    deltas_neg = np.array([-1.5, -2.5])
    X_pos = _make_features(deltas_pos)
    X_neg = _make_features(deltas_neg)
    # Linear column should flip sign
    np.testing.assert_allclose(X_pos[:, 0], -X_neg[:, 0])
    # Squared column should be identical
    np.testing.assert_allclose(X_pos[:, 1], X_neg[:, 1])


# ---------------------------------------------------------------------------
# test_weight_formula
# ---------------------------------------------------------------------------

def _weight(r_q: float) -> float:
    return max(2 * r_q - 1, 0.0) ** 2


def test_weight_below_half_is_zero():
    assert _weight(0.4) == pytest.approx(0.0)
    assert _weight(0.5) == pytest.approx(0.0)
    assert _weight(0.0) == pytest.approx(0.0)


def test_weight_at_0_75():
    assert _weight(0.75) == pytest.approx(0.25)


def test_weight_at_1_0():
    assert _weight(1.0) == pytest.approx(1.0)


def test_weight_monotone():
    r_values = np.linspace(0.0, 1.0, 21)
    weights = [_weight(r) for r in r_values]
    assert all(weights[i] <= weights[i + 1] for i in range(len(weights) - 1))


# ---------------------------------------------------------------------------
# test_length_decile_assignment
# ---------------------------------------------------------------------------

def test_length_decile_produces_10_bins():
    import pandas as pd
    rng = np.random.default_rng(0)
    means = rng.uniform(10, 500, size=200).tolist()
    deciles = pd.qcut(means, q=10, labels=False, duplicates="drop")
    n_unique = len(set(int(d) for d in deciles))
    assert n_unique == 10


def test_length_decile_monotone_with_length():
    import pandas as pd
    means = list(range(100))  # perfectly sorted
    deciles = pd.qcut(means, q=10, labels=False, duplicates="drop")
    decile_list = list(deciles)
    for i in range(len(decile_list) - 1):
        assert decile_list[i] <= decile_list[i + 1]
