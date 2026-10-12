# Agent 8: pinned Twinleaf outcome decoding and paired-seat diagnostics

The pinned upstream `GameWinner` enum is **NONE=-1, PLAYER_1=0, PLAYER_2=1, DRAW=3**, confirmed in `ptcg-server/src/game/store/state/state.ts` at `3348ebdc898f175a2ed8f999133cd13d1afd01f5`. A bare `winner:0` is a **seat-1** victory, never an archetype label.

The [manual CI run 38292409329](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38292409329) completed the exact 60-card Aichi Vileplume vs Mew/Genesect seed-20261012 pair under the separated policy/game RNG streams. Both orientations returned `winner:0`, with Vileplume winning as seat 1 in one game and Mew/Genesect winning as seat 1 in the other. The correct tiny-sample deck counts are **1-1**, not 2-0 for either deck. This does not estimate matchup strength; native SimpleTacticsAi is still unvalidated.

Added `simulation/twinleaf/paired-result-summary.cjs` and a dependency-free SFT with winner/seat mapping, draw=3 handling, error/censor separation, seed and orientation assertions; integrated into the manual-only Twinleaf workflow. Detailed [result note](../../results/tests/paired_engine_outcome_audit/README.md). Future evaluation tools should consume labeled outcomes, count unresolved games in the denominator, and not conflate seed reuse with identical shuffled physical draws.

Editorial coordination: the repository owner has requested a deck-first, concise `results/README.md`. New atomic research should primarily live under `results/tests/` (or its still-unmigrated reproducibility path) and be linked under a relevant section of the index rather than adding independent findings above the main document title.

Agent 8; 2026-10-12 UTC.
