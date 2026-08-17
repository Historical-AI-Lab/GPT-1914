"""test_substantive_drawbank.py — npz round-trip and cross-bank verification.

Fixtures are synthetic on-disk artifacts matching the schema drawbank.py
documents, so this suite validates assemble()/verify_compatible()/freeze()/
load_frozen() in isolation from the producers (bt_context_scoring.py's
calibrate/score --save-* flags, fit_beta_regression_nocontext.py) that
will eventually write files in this format.
"""

import json
import sys
from pathlib import Path

import numpy as np
import pytest

MODELASJUDGE = Path(__file__).parent.parent
sys.path.insert(0, str(MODELASJUDGE))

from substantive import artifacts, drawbank
from substantive.drawbank import ArtifactMismatch, Bank, assemble, freeze, load_frozen, verify_compatible


FRAME_TYPES = ["world_context", "book_context", "passage_context"]


def _base_meta(**extra):
    meta = {"schema_version": 1, "produced_by": "test", "produced_at": "now", "git_head": "abc"}
    meta.update(extra)
    return meta


def _write_beta_bank(path, *, frame_types=FRAME_TYPES, benchmark_version="0.7", D=50):
    rng = np.random.default_rng(0)
    arrays = {"b0": rng.normal(-1, 0.1, D), "b_len": rng.normal(0, 0.1, D),
             "u_frame": rng.normal(0, 0.1, (D, len(frame_types)))}
    meta = _base_meta(benchmark_version=benchmark_version, frame_types=frame_types,
                      standardization={"mu_loglen": 4.3, "sd_loglen": 1.2},
                      sigma_u=0.5, sigma_u_diagnostics={"overdispersion_ratio": 1.5},
                      routing_basis="partial_credit", judge_effort="none",
                      prompt_mode="rationales", prior_dist="normal", prior_df=3.0,
                      prior_scale=3.0)
    artifacts.save_npz(path, arrays, meta)


def _write_calib_bank(path, *, benchmark_version="0.7", C=50, cluster_ids=None):
    rng = np.random.default_rng(1)
    arrays = {"cal_a": rng.normal(0, 0.1, C), "cal_b": rng.normal(1, 0.1, C)}
    meta = _base_meta(benchmark_version=benchmark_version, routing_basis="partial_credit",
                      judge_effort="none", prompt_mode="rationales", prior_dist="normal",
                      prior_df=3.0, prior_scale=3.0, frame_types=FRAME_TYPES)
    if cluster_ids:
        meta["cluster_ids"] = cluster_ids
    artifacts.save_npz(path, arrays, meta)


def _write_delta_bank(path, qnums, *, benchmark_version="0.7", n_draws=100):
    rng = np.random.default_rng(2)
    arrays = {f"delta__{q}": rng.normal(0.5, 1.0, n_draws) for q in qnums}
    meta = _base_meta(benchmark_version=benchmark_version, routing_basis="partial_credit",
                      judge_effort="none", prompt_mode="rationales", prior_dist="normal",
                      prior_df=3.0, prior_scale=3.0, frame_types=FRAME_TYPES)
    artifacts.save_npz(path, arrays, meta)


def _write_benchmark(path, pf_qnums, pc_qnums):
    with open(path, "w") as f:
        for q in pf_qnums:
            f.write(json.dumps({
                "question_number": int(q), "partial_credit": 0,
                "frame_type": "world_context", "reasoning_type": "knowledge",
                "answer_strings": ["a ground truth answer"],
            }) + "\n")
        for q in pc_qnums:
            f.write(json.dumps({
                "question_number": int(q), "partial_credit": 1,
                "frame_type": "book_context", "reasoning_type": "constrained_generation",
                "answer_strings": ["a ground truth answer"],
            }) + "\n")


def _write_scored(path, pf_qnums):
    question_fit = {q: {"scores": [1, 0, 1]} for q in pf_qnums}
    Path(path).write_text(json.dumps({"question_fit": question_fit}))


def _write_reliability(path, pf_qnums):
    per_question = {q: {"question_correct": 7, "question_total": 8} for q in pf_qnums}
    Path(path).write_text(json.dumps({"per_question": per_question}))


@pytest.fixture
def workspace(tmp_path):
    pf_qnums = ["1", "2", "3"]
    pc_qnums = ["10", "11"]
    benchmark = tmp_path / "bench.jsonl"
    _write_benchmark(benchmark, pf_qnums, pc_qnums)
    scored = tmp_path / "scored.json"
    _write_scored(scored, pf_qnums)
    reliability = tmp_path / "reliability.json"
    _write_reliability(reliability, pf_qnums)
    beta_path = tmp_path / "beta_draws.npz"
    _write_beta_bank(beta_path)
    calib_path = tmp_path / "calib_draws.npz"
    _write_calib_bank(calib_path)
    delta_path = tmp_path / "delta_draws.npz"
    _write_delta_bank(delta_path, pc_qnums)
    return dict(benchmark=benchmark, scored=scored, reliability=reliability,
               beta_path=beta_path, calib_path=calib_path, delta_path=delta_path,
               pf_qnums=pf_qnums, pc_qnums=pc_qnums)


class TestNpzRoundTrip:
    def test_save_load_allow_pickle_false(self, tmp_path):
        path = tmp_path / "x.npz"
        artifacts.save_npz(path, {"a": np.array([1.0, 2.0])}, {"k": "v"})
        arrays, meta = artifacts.load_npz(path)
        assert np.allclose(arrays["a"], [1.0, 2.0])
        assert meta == {"k": "v"}
        # allow_pickle=False must not raise -- load_npz itself uses it internally
        raw = np.load(path, allow_pickle=False)
        assert "a" in raw.files


class TestVerifyCompatible:
    @pytest.mark.parametrize("key,val_a,val_b", [
        ("benchmark_version", "0.7", "0.4"),
        ("routing_basis", "partial_credit", "context_judged"),
        ("prompt_mode", "rationales", "exemplars"),
        ("prior_dist", "normal", "studentt"),
        ("prior_df", 3.0, 5.0),
        ("prior_scale", 3.0, 1.0),
        ("judge_effort", "none", "medium"),
        ("frame_types", FRAME_TYPES, list(reversed(FRAME_TYPES))),
    ])
    def test_raises_on_each_guarded_key(self, key, val_a, val_b):
        metas = {"a": {key: val_a}, "b": {key: val_b}}
        with pytest.raises(ArtifactMismatch, match=key):
            verify_compatible(metas)

    def test_frame_types_reordered_with_identical_values_still_raises(self):
        metas = {"a": {"frame_types": ["world_context", "book_context"]},
                 "b": {"frame_types": ["book_context", "world_context"]}}
        with pytest.raises(ArtifactMismatch):
            verify_compatible(metas)

    def test_agreement_passes(self):
        metas = {"a": {"benchmark_version": "0.7"}, "b": {"benchmark_version": "0.7"}}
        verify_compatible(metas)  # no raise

    def test_missing_key_in_one_role_is_ignored(self):
        metas = {"a": {"benchmark_version": "0.7"}, "b": {}}
        verify_compatible(metas)  # no raise

    def test_namespaced_pilot_qids_do_not_collide(self):
        """cluster_ids is a list of [qid, version] pairs -- one per LOO
        record -- because a plain {qid: version} dict cannot represent the
        collision case at all (the second write would just overwrite the
        first). Namespacing the pilot qid ("pilot:3" vs "3") keeps them
        distinct."""
        metas = {"calib": {"cluster_ids": [["pilot:3", "0.1"], ["3", "0.7"]]}}
        verify_compatible(metas)  # no raise

    def test_unnamespaced_merge_collides_and_raises(self):
        """The trap: merging pilot LOO records into production without
        namespacing means qid "3" resolves to two different benchmark
        versions -- two unrelated questions clustered as one."""
        metas = {"calib": {"cluster_ids": [["3", "0.1"], ["3", "0.7"]]}}
        with pytest.raises(ArtifactMismatch, match="more than one benchmark version"):
            verify_compatible(metas)


class TestAssemble:
    def test_shapes_and_alignment(self, workspace):
        bank = assemble(scored_file=workspace["scored"], benchmark_path=workspace["benchmark"],
                        reliability_path=workspace["reliability"], beta_draws_path=workspace["beta_path"],
                        calib_draws_path=workspace["calib_path"], delta_draws_path=workspace["delta_path"])
        assert bank.qnums_pf == sorted(workspace["pf_qnums"], key=int)
        assert bank.qnums_pc == sorted(workspace["pc_qnums"], key=int)
        assert bank.v_hat.shape == (3,)
        assert np.allclose(bank.v_hat, 2 / 3)
        assert bank.k_alpha.shape == (3,)
        assert bank.delta_draws.shape == (2, 100)
        assert bank.coef_u_frame.shape == (50, 3)
        assert bank.sigma_u == pytest.approx(0.5)

    def test_missing_alpha_reliability_raises(self, workspace):
        reliability = json.loads(workspace["reliability"].read_text())
        del reliability["per_question"]["2"]
        workspace["reliability"].write_text(json.dumps(reliability))
        with pytest.raises(KeyError, match="2"):
            assemble(scored_file=workspace["scored"], benchmark_path=workspace["benchmark"],
                    reliability_path=workspace["reliability"], beta_draws_path=workspace["beta_path"],
                    calib_draws_path=workspace["calib_path"], delta_draws_path=workspace["delta_path"])

    def test_missing_delta_draws_raises(self, workspace):
        _write_delta_bank(workspace["delta_path"], ["10"])  # drop qnum 11
        with pytest.raises(KeyError, match="11"):
            assemble(scored_file=workspace["scored"], benchmark_path=workspace["benchmark"],
                    reliability_path=workspace["reliability"], beta_draws_path=workspace["beta_path"],
                    calib_draws_path=workspace["calib_path"], delta_draws_path=workspace["delta_path"])

    def test_incompatible_benchmark_version_raises(self, workspace):
        _write_beta_bank(workspace["beta_path"], benchmark_version="0.4")
        with pytest.raises(ArtifactMismatch, match="benchmark_version"):
            assemble(scored_file=workspace["scored"], benchmark_path=workspace["benchmark"],
                    reliability_path=workspace["reliability"], beta_draws_path=workspace["beta_path"],
                    calib_draws_path=workspace["calib_path"], delta_draws_path=workspace["delta_path"])


class TestFreezeRoundTrip:
    def test_bit_for_bit(self, workspace, tmp_path):
        bank = assemble(scored_file=workspace["scored"], benchmark_path=workspace["benchmark"],
                        reliability_path=workspace["reliability"], beta_draws_path=workspace["beta_path"],
                        calib_draws_path=workspace["calib_path"], delta_draws_path=workspace["delta_path"])
        frozen_path = tmp_path / "frozen.npz"
        freeze(bank, frozen_path)
        reloaded = load_frozen(frozen_path)

        assert reloaded.qnums_pf == bank.qnums_pf
        assert reloaded.qnums_pc == bank.qnums_pc
        for field in ("v_hat", "n_v", "k_alpha", "n_alpha", "frame_idx", "z_loglen",
                     "coef_b0", "coef_b_len", "coef_u_frame", "delta_draws", "cal_a", "cal_b"):
            assert np.array_equal(getattr(reloaded, field), getattr(bank, field)), field
        assert reloaded.sigma_u == bank.sigma_u

    def test_provenance_is_stable(self, workspace, tmp_path):
        bank = assemble(scored_file=workspace["scored"], benchmark_path=workspace["benchmark"],
                        reliability_path=workspace["reliability"], beta_draws_path=workspace["beta_path"],
                        calib_draws_path=workspace["calib_path"], delta_draws_path=workspace["delta_path"])
        prov = drawbank.provenance(bank)
        assert set(prov) == {"beta_draws", "calib_draws", "delta_draws"}
        for role, entry in prov.items():
            assert entry["produced_by"] == "test"
