"""test_substantive_drawbank.py — npz round-trip and cross-bank verification.

Fixtures are synthetic on-disk artifacts matching the schema drawbank.py
documents, so this suite validates assemble()/verify_compatible()/freeze()/
load_frozen() in isolation from the producers (bt_context_scoring.py's
calibrate/score --save-* flags) that will eventually write files in this
format. Only two banks feed a candidate's score now
(direct-binary-scoring-spec.md): the binary channel is read straight off
the scored-answers file, with no reliability JSON or beta draw bank as a
dependency.
"""

import json
import sys
from pathlib import Path

import numpy as np
import pytest

MODELASJUDGE = Path(__file__).parent.parent
sys.path.insert(0, str(MODELASJUDGE))

from substantive import artifacts, drawbank
from substantive.drawbank import ArtifactMismatch, assemble, freeze, load_frozen, verify_compatible


FRAME_TYPES = ["world_context", "book_context", "passage_context"]


def _base_meta(**extra):
    meta = {"schema_version": 1, "produced_by": "test", "produced_at": "now", "git_head": "abc"}
    meta.update(extra)
    return meta


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


@pytest.fixture
def workspace(tmp_path):
    pf_qnums = ["1", "2", "3"]
    pc_qnums = ["10", "11"]
    benchmark = tmp_path / "bench.jsonl"
    _write_benchmark(benchmark, pf_qnums, pc_qnums)
    scored = tmp_path / "scored.json"
    _write_scored(scored, pf_qnums)
    calib_path = tmp_path / "calib_draws.npz"
    _write_calib_bank(calib_path)
    delta_path = tmp_path / "delta_draws.npz"
    _write_delta_bank(delta_path, pc_qnums)
    return dict(benchmark=benchmark, scored=scored,
               calib_path=calib_path, delta_path=delta_path,
               pf_qnums=pf_qnums, pc_qnums=pc_qnums)


def _assemble(ws, **overrides):
    kwargs = dict(scored_file=ws["scored"], benchmark_path=ws["benchmark"],
                 calib_draws_path=ws["calib_path"], delta_draws_path=ws["delta_path"],
                 benchmark_version="0.7")
    kwargs.update(overrides)
    return assemble(**kwargs)


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
    ])
    def test_raises_on_each_guarded_key(self, key, val_a, val_b):
        metas = {"a": {key: val_a}, "b": {key: val_b}}
        with pytest.raises(ArtifactMismatch, match=key):
            verify_compatible(metas)

    def test_frame_types_is_no_longer_a_guarded_key(self):
        """Only the beta draw bank carried frame_types, and that bank is no
        longer part of the binary-scoring path -- a disagreement here must
        not raise."""
        metas = {"a": {"frame_types": ["world_context", "book_context"]},
                 "b": {"frame_types": ["book_context", "world_context"]}}
        verify_compatible(metas)  # no raise

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
        bank = _assemble(workspace)
        assert bank.qnums_pf == sorted(workspace["pf_qnums"], key=int)
        assert bank.qnums_pc == sorted(workspace["pc_qnums"], key=int)
        assert bank.v_hat.shape == (3,)
        assert np.allclose(bank.v_hat, 2 / 3)
        assert bank.delta_draws.shape == (2, 100)
        assert bank.benchmark_version == "0.7"

    def test_no_reliability_or_beta_bank_dependency(self, workspace):
        """assemble() no longer accepts reliability_path / beta_draws_path
        at all -- direct-binary-scoring-spec.md section 18."""
        import inspect
        params = inspect.signature(assemble).parameters
        assert "reliability_path" not in params
        assert "beta_draws_path" not in params

    def test_missing_delta_draws_raises(self, workspace):
        _write_delta_bank(workspace["delta_path"], ["10"])  # drop qnum 11
        with pytest.raises(KeyError, match="11"):
            _assemble(workspace)

    def test_missing_scored_question_raises(self, workspace):
        scored = json.loads(Path(workspace["scored"]).read_text())
        del scored["question_fit"]["2"]
        Path(workspace["scored"]).write_text(json.dumps(scored))
        with pytest.raises(KeyError, match="2"):
            _assemble(workspace)

    def test_incompatible_benchmark_version_raises(self, workspace):
        _write_calib_bank(workspace["calib_path"], benchmark_version="0.4")
        with pytest.raises(ArtifactMismatch, match="benchmark_version"):
            _assemble(workspace)


class TestFreezeRoundTrip:
    def test_bit_for_bit(self, workspace, tmp_path):
        bank = _assemble(workspace)
        frozen_path = tmp_path / "frozen.npz"
        freeze(bank, frozen_path)
        reloaded = load_frozen(frozen_path)

        assert reloaded.qnums_pf == bank.qnums_pf
        assert reloaded.qnums_pc == bank.qnums_pc
        for field in ("v_hat", "delta_draws", "cal_a", "cal_b"):
            assert np.array_equal(getattr(reloaded, field), getattr(bank, field)), field
        assert reloaded.benchmark_version == bank.benchmark_version

    def test_reasoning_type_survives_for_the_group_breakdown(self, workspace, tmp_path):
        """load_frozen used to rebuild Routing with empty {} record stubs,
        which would make substantive/groups.py's group_of raise on every
        question scored from a frozen bank. freeze() now carries
        reasoning_pf/reasoning_pc so the stubs are reconstructible."""
        bank = _assemble(workspace)
        frozen_path = tmp_path / "frozen.npz"
        freeze(bank, frozen_path)
        reloaded = load_frozen(frozen_path)

        for q in reloaded.qnums_pf:
            assert (reloaded.routing.pass_fail[q]["reasoning_type"]
                   == bank.routing.pass_fail[q]["reasoning_type"])
        for q in reloaded.qnums_pc:
            assert (reloaded.routing.partial[q]["reasoning_type"]
                   == bank.routing.partial[q]["reasoning_type"])

    def test_load_frozen_raises_a_clear_error_on_a_pre_breakdown_bank(self, tmp_path):
        """A frozen bank saved before this change has no reasoning_pf/
        reasoning_pc in its meta -- fail loud rather than silently emit a
        report with no group breakdown."""
        old_style_meta = {
            "schema_version": 1, "produced_by": "old", "produced_at": "now", "git_head": "abc",
            "routing_basis": "partial_credit", "qnums_pf": ["1"], "qnums_pc": [],
        }
        arrays = {"v_hat": np.zeros(1), "delta_draws": np.zeros((0, 1)),
                 "cal_a": np.zeros(1), "cal_b": np.zeros(1)}
        path = tmp_path / "old_frozen.npz"
        artifacts.save_npz(path, arrays, old_style_meta)
        with pytest.raises(KeyError, match="re-run"):
            load_frozen(path)

    def test_frozen_bank_ignores_rg_era_arrays(self, workspace, tmp_path):
        """An archived bank from before this change carries k_alpha,
        coef_b0, sigma_u, etc. -- load_frozen must silently ignore them
        rather than error, so old archives still score."""
        bank = _assemble(workspace)
        frozen_path = tmp_path / "frozen.npz"
        freeze(bank, frozen_path)
        arrays, meta = artifacts.load_npz(frozen_path)
        arrays["k_alpha"] = np.zeros(3)
        arrays["coef_b0"] = np.zeros(10)
        meta["sigma_u"] = 0.5
        artifacts.save_npz(frozen_path, arrays, meta)

        reloaded = load_frozen(frozen_path)
        assert np.array_equal(reloaded.v_hat, bank.v_hat)

    def test_scoring_version_is_stamped(self, workspace, tmp_path):
        bank = _assemble(workspace)
        frozen_path = tmp_path / "frozen.npz"
        freeze(bank, frozen_path)
        _, meta = artifacts.load_npz(frozen_path)
        assert meta["scoring_version"] == "direct_binary_v1"

    def test_provenance_is_stable(self, workspace):
        bank = _assemble(workspace)
        prov = drawbank.provenance(bank)
        assert set(prov) == {"calib_draws", "delta_draws"}
        for role, entry in prov.items():
            assert entry["produced_by"] == "test"


class TestAutoVerdictArrays:
    def test_absent_everywhere_loads_as_all_nan(self, workspace):
        """Artifacts predating automatic verdicts must still assemble, and say
        'nothing was short-circuited'."""
        bank = _assemble(workspace)
        assert bank.auto_pf.shape == (len(workspace["pf_qnums"]),)
        assert bank.auto_pc.shape == (len(workspace["pc_qnums"]),)
        assert np.all(np.isnan(bank.auto_pf))
        assert np.all(np.isnan(bank.auto_pc))

    def test_auto_verdict_in_scored_file_reaches_auto_pf(self, workspace):
        scored = json.loads(Path(workspace["scored"]).read_text())
        scored["question_fit"]["1"]["auto_verdict"] = "gt_identity"
        scored["question_fit"]["2"]["auto_verdict"] = "distractor_identity"
        Path(workspace["scored"]).write_text(json.dumps(scored))

        bank = _assemble(workspace)
        assert bank.auto_pf[0] == 1.0      # qnum "1"
        assert bank.auto_pf[1] == 0.0      # qnum "2"
        assert np.isnan(bank.auto_pf[2])   # qnum "3", judged

    def test_auto_key_in_npz_reaches_auto_pc(self, workspace):
        arrays, meta = artifacts.load_npz(workspace["delta_path"])
        arrays["auto__10"] = np.array(1.0)
        artifacts.save_npz(workspace["delta_path"], arrays, meta)

        bank = _assemble(workspace)
        assert bank.auto_pc[0] == 1.0      # qnum "10"
        assert np.isnan(bank.auto_pc[1])   # qnum "11", judged

    def test_freeze_round_trips_the_overrides(self, workspace, tmp_path):
        scored = json.loads(Path(workspace["scored"]).read_text())
        scored["question_fit"]["1"]["auto_verdict"] = "gt_identity"
        Path(workspace["scored"]).write_text(json.dumps(scored))
        arrays, meta = artifacts.load_npz(workspace["delta_path"])
        arrays["auto__11"] = np.array(0.0)
        artifacts.save_npz(workspace["delta_path"], arrays, meta)

        bank = _assemble(workspace)
        frozen_path = tmp_path / "frozen.npz"
        freeze(bank, frozen_path)
        reloaded = load_frozen(frozen_path)
        assert reloaded.auto_pf[0] == 1.0
        assert reloaded.auto_pc[1] == 0.0
        assert np.isnan(reloaded.auto_pf[1])

    def test_frozen_bank_without_the_arrays_loads_as_all_nan(self, workspace, tmp_path):
        """A bank frozen before this feature existed must still load."""
        bank = _assemble(workspace)
        frozen_path = tmp_path / "frozen.npz"
        freeze(bank, frozen_path)
        arrays, meta = artifacts.load_npz(frozen_path)
        del arrays["auto_pf"], arrays["auto_pc"]
        artifacts.save_npz(frozen_path, arrays, meta)

        reloaded = load_frozen(frozen_path)
        assert np.all(np.isnan(reloaded.auto_pf))
        assert np.all(np.isnan(reloaded.auto_pc))
        assert reloaded.auto_pf.shape == (len(workspace["pf_qnums"]),)


class TestCalibrationDesignGuard:
    def test_pin_p_mismatch_between_banks_raises(self):
        with pytest.raises(ArtifactMismatch, match="pin_p"):
            verify_compatible({
                "calib_draws": {"pin_p": 0.9, "class_balance": True},
                "delta_draws": {"pin_p": None, "class_balance": True},
            })

    def test_class_balance_mismatch_raises(self):
        with pytest.raises(ArtifactMismatch, match="class_balance"):
            verify_compatible({
                "calib_draws": {"pin_p": 0.9, "class_balance": True},
                "delta_draws": {"pin_p": 0.9, "class_balance": False},
            })

    def test_matching_design_passes(self):
        verify_compatible({
            "calib_draws": {"pin_p": 0.9, "class_balance": True},
            "delta_draws": {"pin_p": 0.9, "class_balance": True},
        })

    def test_key_absent_from_one_side_is_ignored(self):
        """Older artifacts predate the field; only two carriers are compared."""
        verify_compatible({
            "calib_draws": {"pin_p": 0.9},
            "delta_draws": {"class_balance": True},
        })
