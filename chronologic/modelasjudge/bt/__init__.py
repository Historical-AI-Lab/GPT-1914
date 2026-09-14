"""bt — Bradley-Terry context judge for ChronoLogic.

Pure-logic package: no module here opens a network connection. The only
entry point that talks to a judge model is an injected `judge_call`
callable (see bt.collect.run_comparisons), supplied by the CLI wrapper
in ../bt_context_scoring.py or by a stub in tests/simulation.

See ../bt-context-judge-plan.md and bradley/bradley-terry-spec.md.
"""
