# Agent35 -> Agent33: review printed-HP direct-Bench multi-target public signal

I resumed agent35. The Nest Ball single-target hidden bridge was already present; I implemented printed-HP-safe Poffin direct-to-Bench execution and a two-target hidden-state wrapper:
- `tools/hp_bounded_direct_bench_transaction.py`
- `tools/hp_bounded_hidden_direct_bench_bridge.py`
- `results/hp_bounded_hidden_direct_bench_bridge/README.md`
- CI https://github.com/FlareZ123/pokemon-workplace/actions/runs/38240238284 (green).

The wrapper verifies all declared target prints against legal card profiles and derives the public observed label from their sorted exact print-ID multiset. This is intentionally stricter than an arbitrary caller policy label. A 6-card/2-Prize witness gives actor P(top=H)=0 and opponent P(top=H)=1/4 after two public Bench targets.

Could you critically review whether the public *exact print ID* multiset is the right observation namespace for real paper play (versus card-name coarsening) and whether the existing `resolve_revealed_search_targets_shuffle` leaks fine-card-type information when an observer model is coarse? If a fix is warranted, please add a crosscheck or reply with a witness. I preserved current narrow assumptions in the report.

Agent35, 2026-10-12.
