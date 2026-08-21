"""test_bt_recovery.py — Recovery tests for the Bradley-Terry estimator,
through bt/simulate.py only (production code paths, judge stubbed).

CI gate is small and loose per spec: catches broken indexing / label
leakage, not tight statistical precision. Full sweeps (large R, kappa,
misspecification) are reported artifacts via `simulate --report`, not
pass/fail here -- marked slow and skipped by default.

Run with:
    pytest modelasjudge/tests/test_bt_recovery.py -v
    pytest modelasjudge/tests/test_bt_recovery.py -v -m slow   # full sweeps
"""

import sys
from pathlib import Path

import numpy as np
import pytest

MODELASJUDGE = Path(__file__).parent.parent
sys.path.insert(0, str(MODELASJUDGE))

from bt.fit import FitConfig
from bt.simulate import (
    run_full_chain,
    run_null_control,
    run_sbc,
    run_sign_control,
    structured_theta_config,
)

FAST = FitConfig(draws=150, tune=250, chains=2)


class TestSbc:
    def test_rank_uniformity_and_coverage(self):
        report = run_sbc(n_items=4, replicates=40, master_seed=12345,
                         n_thin=30, fit_config=FAST)
        assert report.rank_uniformity_pvalue > 0.001
        assert 0.30 <= report.coverage["50%"] <= 0.70
        assert 0.75 <= report.coverage["90%"] <= 1.0

    def test_deterministic_rerun(self):
        r1 = run_sbc(n_items=3, replicates=10, master_seed=7, n_thin=20, fit_config=FAST)
        r2 = run_sbc(n_items=3, replicates=10, master_seed=7, n_thin=20, fit_config=FAST)
        assert r1.ranks == r2.ranks


class TestNullControl:
    def test_auc_near_half_and_no_signal(self):
        result = run_null_control(n_items=6, replicates=30, master_seed=999, fit_config=FAST)
        if not np.isnan(result["recovered_auc_mean"]):
            assert 0.30 <= result["recovered_auc_mean"] <= 0.70
        assert abs(result["true_auc"] - 0.5) < 1e-9


class TestSignControl:
    def test_negation_flips_auc(self):
        theta_config = structured_theta_config(n_distractors=3, kappa=1.5)
        gt_ids = ["gt0", "gt1"]
        result = run_sign_control(theta_config, gt_ids, n_questions=3, replicates=2,
                                  master_seed=2024, fit_config=FAST)
        pos_auc = result["positive"]["true_auc"]
        neg_auc = result["negated"]["true_auc"]
        assert abs((pos_auc + neg_auc) - 1.0) < 1e-9


class TestFullChainDeterminism:
    def test_bitwise_reproducible(self):
        theta_config = structured_theta_config(n_distractors=3, kappa=1.0)
        gt_ids = ["gt0", "gt1"]
        r1 = run_full_chain(theta_config, gt_ids, n_questions=2, replicates=2,
                            master_seed=555, fit_config=FAST)
        r2 = run_full_chain(theta_config, gt_ids, n_questions=2, replicates=2,
                            master_seed=555, fit_config=FAST)
        assert r1 == r2


@pytest.mark.slow
class TestFullSweeps:
    def test_kappa_sweep_reports_adequacy_range(self):
        from bt.simulate import run_kappa_sweep
        out = run_kappa_sweep((0.5, 1, 2, 3), replicates=50, master_seed=1, fit_config=FAST)
        assert set(out) == {0.5, 1, 2, 3}

    def test_misspec_sweep_false_alarm_rate(self):
        from bt.simulate import run_misspec_sweep
        out = run_misspec_sweep((0.0, 0.5), (0.0, 1.0), replicates=30, master_seed=1,
                                fit_config=FAST)
        baseline = out[(0.0, 0.0)]
        assert baseline["ppc_alarm_rate"] <= 0.25
