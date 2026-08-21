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
from substantive.estimator import BootstrapResult, GroupResult, PlugPoint
from substantive.groups import GROUPS, LEDGER_PREFIX
from substantive.report import write_report
from substantive.routing import Routing


@pytest.fixture
def synthetic_scenario():
    rng = np.random.default_rng(0)
    n_pf, n_pc, R = 40, 20, 500
    routing = Routing(basis="partial_credit",
                      pass_fail={str(i): {} for i in range(n_pf)},
                      partial={str(i): {} for i in range(n_pc)})
    # A mix of pass (1.0), fail (0.0), and fractional verdicts so
    # n_binary_pass/fail/split is exercised.
    p_binary = np.concatenate([np.ones(12), np.zeros(20), rng.uniform(0.1, 0.9, 8)])
    bank = Bank(
        routing=routing, qnums_pf=[str(i) for i in range(n_pf)],
        v_hat=p_binary, qnums_pc=[str(i) for i in range(n_pc)],
        delta_draws=rng.normal(0.5, 1.0, (n_pc, 200)),
        cal_a=np.zeros(50), cal_b=np.ones(50),
        auto_pf=np.full(n_pf, np.nan), auto_pc=np.full(n_pc, np.nan),
        metas={"calib_draws": {"produced_by": "bt_context_scoring.py calibrate",
                               "produced_at": "2026-08-17T00:00:00Z", "git_head": "abc123",
                               "benchmark_version": "0.7"},
              "delta_draws": {"produced_by": "bt_context_scoring.py score",
                              "produced_at": "2026-08-17T00:00:00Z", "git_head": "abc123",
                              "benchmark_version": "0.7"}},
        benchmark_version="0.7",
    )
    point = PlugPoint(
        passfail=float(p_binary.mean()), partial=0.62, pooled_count=0.58, pooled_equal=0.585,
        p_binary=p_binary, p_partial=rng.uniform(0, 1, n_pc),
        n_passfail=n_pf, n_partial=n_pc,
    )
    boot = BootstrapResult(
        passfail=rng.uniform(0.4, 0.7, R),
        partial=rng.uniform(0.5, 0.7, R),
        pooled_count=rng.uniform(0.45, 0.65, R),
        pooled_equal=rng.uniform(0.45, 0.65, R),
        p_binary_qr=rng.uniform(0, 1, (n_pf, R)), p_partial_qr=rng.uniform(0, 1, (n_pc, R)),
    )
    provenance = {"calib_draws": {"produced_by": "bt_context_scoring.py calibrate",
                                  "produced_at": "2026-08-17T00:00:00Z", "git_head": "abc123"},
                 "delta_draws": {"produced_by": "bt_context_scoring.py score",
                                 "produced_at": "2026-08-17T00:00:00Z", "git_head": "abc123"}}
    return dict(point=point, boot=boot, bank=bank, provenance=provenance,
               benchmark_version="0.7")


@pytest.fixture
def synthetic_groups():
    return {
        "cloze": GroupResult(point=0.61, lo=0.55, hi=0.67, n=30, n_pf=25, n_pc=5),
        "constrained_generation": GroupResult(point=0.49, lo=0.40, hi=0.58, n=15, n_pf=5, n_pc=10),
        "knowledge_inference": GroupResult(point=0.72, lo=0.65, hi=0.79, n=15, n_pf=10, n_pc=5),
    }


class TestWriteReport:
    def test_mandated_sections_present(self, synthetic_scenario, tmp_path):
        path = tmp_path / "report.md"
        write_report(path, candidate_label="gpt-5.4", judge="anthropic/claude-sonnet-4-6",
                    judge_effort="medium", run_date="2026-08-21", **synthetic_scenario)
        text = path.read_text()
        for heading in ("## Scores", "## Diagnostics", "## Provenance"):
            assert heading in text

    def test_checks_section_only_when_provided(self, synthetic_scenario, tmp_path):
        path = tmp_path / "report.md"
        write_report(path, candidate_label="x", judge="y", **synthetic_scenario)
        assert "## Verification checks" not in path.read_text()

        write_report(path, candidate_label="x", judge="y",
                    checks={"binary identity": "|passfail - mean(v_q)| = 0.00e+00"},
                    **synthetic_scenario)
        text = path.read_text()
        assert "## Verification checks" in text
        assert "binary identity" in text

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
        assert str(row["n_binary_pass"]) in text
        assert str(row["n_binary_fail"]) in text
        assert str(row["n_binary_split"]) in text
        assert row["scoring_version"] == "direct_binary_v1"

    def test_binary_verdict_counts_match_p_binary(self, synthetic_scenario, tmp_path):
        path = tmp_path / "report.md"
        row = write_report(path, candidate_label="x", judge="y", **synthetic_scenario)
        p_binary = synthetic_scenario["point"].p_binary
        assert row["n_binary_pass"] == int(np.count_nonzero(p_binary == 1.0))
        assert row["n_binary_fail"] == int(np.count_nonzero(p_binary == 0.0))
        assert (row["n_binary_pass"] + row["n_binary_fail"] + row["n_binary_split"]
               == synthetic_scenario["point"].n_passfail)

    def test_no_rogan_gladen_columns_in_the_row(self, synthetic_scenario, tmp_path):
        path = tmp_path / "report.md"
        row = write_report(path, candidate_label="x", judge="y", **synthetic_scenario)
        for retired in ("alpha_prior", "n_excluded_floor", "clip_rate",
                       "near_floor_frac", "sigma_u", "mean_alpha"):
            assert retired not in row

    def test_groups_section_omitted_when_not_provided(self, synthetic_scenario, tmp_path):
        path = tmp_path / "report.md"
        write_report(path, candidate_label="x", judge="y", **synthetic_scenario)
        assert "## Scores by reasoning type" not in path.read_text()

    def test_groups_section_and_row_keys_present_when_provided(
        self, synthetic_scenario, synthetic_groups, tmp_path
    ):
        path = tmp_path / "report.md"
        row = write_report(path, candidate_label="x", judge="y", groups=synthetic_groups,
                           **synthetic_scenario)
        text = path.read_text()
        assert "## Scores by reasoning type" in text

        for g in GROUPS:
            gr = synthetic_groups[g]
            prefix = LEDGER_PREFIX[g]
            for suffix, val in (("score", gr.point), ("lo", gr.lo), ("hi", gr.hi)):
                key = f"{prefix}_{suffix}"
                assert key in row
                assert f"{row[key]:.1%}" in text
            assert row[f"{prefix}_n_pf"] == gr.n_pf
            assert row[f"{prefix}_n_pc"] == gr.n_pc
            assert str(gr.n_pf) in text
            assert str(gr.n_pc) in text

    def test_row_is_upsert_ready(self, synthetic_scenario, tmp_path):
        """The returned dict should slot directly into ledger.upsert_row."""
        from substantive.ledger import KEY_COLUMNS, upsert_row

        path = tmp_path / "report.md"
        row = write_report(path, candidate_label="gpt-5.4", candidate_effort="medium",
                           judge="anthropic/claude-sonnet-4-6", judge_effort="medium",
                           bt_tag="tag1", **synthetic_scenario)
        assert all(k in row for k in KEY_COLUMNS)
        upsert_row(row, path=tmp_path / "ledger.csv")  # must not raise
