"""substantive — the fully automated substantive scoring pipeline.

Pure-logic package: imports numpy + scipy only, no LLM calls, no PyMC, so
its tests run in under a second. Mirrors the ../bt/ package precedent. See
../direct-binary-scoring-spec.md for the binary channel and
../estimator_and_calibration_explained.md for the philosophy of both channels.
"""
