"""test_substantive_report.py — renders from a synthetic bank.

The load-bearing property: every number the report shows also appears in
the dict write_report returns (which score_substantive.py hands straight
to ledger.upsert_row), so the report and the ledger row cannot drift.
"""

import sys
from pathlib import Path

import numpy as np
import pytest

MODELASJUDGE = Path(__file__).parent.parent
sys.path.insert(0, str(MODELASJUDGE))

from substantive.drawbank import Bank
from substantive.estimator import BootstrapResult, PlugPoint
from substantive.report import write_report
from substantive.routing import Routing


@pytest.fixture
def synthetic_scenario():
    rng = np.random.default_rng(0)
    n_pf, n_pc, R = 40, 20, 500
    routing = Routing(basis="partial_credit",
                      pass_fail={str(i): {} for i in range(n_pf)},
                      partial={str(i): {} for i in range(n_pc)})
    bank = Bank(
        routing=routing, qnums_pf=[str(i) for i in range(n_pf)],
        v_hat=rng.uniform(0.3, 0.7, n_pf), n_v=np.full(n_pf, 9),
        k_alpha=np.full(n_pf, 7), n_alpha=np.full(n_pf, 8),
        frame_idx=np.zeros(n_pf, dtype=int), z_loglen=np.zeros(n_pf),
        coef_b0=np.zeros(50), coef_b_len=np.zeros(50), coef_u_frame=np.zeros((50, 1)),
        sigma_u=0.4, qnums_pc=[str(i) for i in range(n_pc)],
        delta_draws=rng.normal(0.5, 1.0, (n_pc, 200)),
        cal_a=np.zeros(50), cal_b=np.ones(50),
        metas={"beta_draws": {"produced_by": "fit_beta_regression_nocontext.py",
                              "produced_at": "2026-08-17T00:00:00Z", "git_head": "abc123",
                              "benchmark_version": "0.7"}},
    )
    point = PlugPoint(
        passfail=0.55, partial=0.62, pooled_count=0.58, pooled_equal=0.585,
        p_binary=rng.uniform(0, 1, n_pf), p_partial=rng.uniform(0, 1, n_pc),
        q_bar=0.5, n_passfail=n_pf, n_partial=n_pc, n_excluded_floor=2,
        excluded_mask=np.zeros(n_pf, dtype=bool),
    )
    boot = BootstrapResult(
        passfail=np.clip(rng.normal(0.55, 0.03, R), 0, 1),
        partial=np.clip(rng.normal(0.62, 0.05, R), 0, 1),
        pooled_count=np.clip(rng.normal(0.58, 0.03, R), 0, 1),
        pooled_equal=np.clip(rng.normal(0.585, 0.03, R), 0, 1),
        p_binary_qr=rng.uniform(0, 1, (n_pf, R)), p_partial_qr=rng.uniform(0, 1, (n_pc, R)),
    )
    provenance = {"beta_draws": {"produced_by": "fit_beta_regression_nocontext.py",
                                 "produced_at": "2026-08-17T00:00:00Z", "git_head": "abc123"}}
    return dict(point=point, boot=boot, bank=bank, provenance=provenance)


class TestWriteReport:
    def test_mandated_sections_present(self, synthetic_scenario, tmp_path):
        path = tmp_path / "report.md"
        write_report(path, candidate_label="gpt-5.4", judge="anthropic/claude-sonnet-4-6",
                    judge_effort="medium", run_date="2026-08-17", **synthetic_scenario)
        text = path.read_text()
        for heading in ("## Scores", "## Diagnostics", "## Provenance"):
            assert heading in text

    def test_checks_section_only_when_provided(self, synthetic_scenario, tmp_path):
        path = tmp_path / "report.md"
        write_report(path, candidate_label="x", judge="y", **synthetic_scenario)
        assert "## Verification checks" not in path.read_text()

        write_report(path, candidate_label="x", judge="y",
                    checks={"layer ablation": "instrument noise widens CI by 3.2x"},
                    **synthetic_scenario)
        text = path.read_text()
        assert "## Verification checks" in text
        assert "layer ablation" in text

    def test_every_returned_number_appears_in_the_report(self, synthetic_scenario, tmp_path):
        path = tmp_path / "report.md"
        row = write_report(path, candidate_label="gpt-5.4", judge="anthropic/claude-sonnet-4-6",
                           **synthetic_scenario)
        text = path.read_text()

        pct_fields = ["passfail", "passfail_lo", "passfail_hi", "partial", "partial_lo", "partial_hi",
                     "pooled_count", "pooled_count_lo", "pooled_count_hi",
                     "pooled_equal", "pooled_equal_lo", "pooled_equal_hi"]
        for field in pct_fields:
            formatted = f"{row[field]:.1%}"
            assert formatted in text, f"{field}={formatted} missing from report"

        assert f"{row['n_passfail']}" in text
        assert f"{row['n_partial']}" in text
        assert str(row["n_excluded_floor"]) in text
        assert f"{row['sigma_u']:.4f}" in text

    def test_row_is_upsert_ready(self, synthetic_scenario, tmp_path):
        """The returned dict should slot directly into ledger.upsert_row."""
        from substantive.ledger import KEY_COLUMNS, upsert_row

        path = tmp_path / "report.md"
        row = write_report(path, candidate_label="gpt-5.4", candidate_effort="medium",
                           judge="anthropic/claude-sonnet-4-6", judge_effort="medium",
                           bt_tag="tag1", **synthetic_scenario)
        assert all(k in row for k in KEY_COLUMNS)
        upsert_row(row, path=tmp_path / "ledger.csv")  # must not raise
