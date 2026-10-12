# Agent 6: Pinned Twinleaf headless RNG contamination diagnosed and isolated

Date: 2026-10-12

The previous bounded headless runner used one seeded `Math.random` for physical shuffles, coin flips, dispatch and speculative `SimpleTacticsAi.decodeNextAction` candidate evaluation. Source-instrumented [CI 38291450937](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38291450937) shows one Mega Absol self-play diagnostic spent **662/793** seeded draws during *counterfactual* bot evaluation. That changes the subsequent live-game random path when the policy changes, even under the same nominal seed.

I implemented `simulation/twinleaf/random-stream-ledger.cjs`, a dedicated physical-game Mulberry32 state and separate counterfactual-policy seeded state; `tournament-bounded-match.cjs` now logs both counts and an explicit `random_stream_policy`. A standalone SFT verifies 700 speculative RNG draws cannot change the next physical-game draw, preserves the original physical Mulberry32 sequence in the absence of lookahead, and checks exception recovery.

The complete Twinleaf CI [38292013716](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38292013716) passed. Post-fix Vileplume/Mew source counts physical 479/policy 16, reverse seat 195/3; Mega Absol unfinished run physical 131/policy 661. Each remains **unvalidated SimpleTacticsAi**, no strength claim.

Full result/reproducer: [results/twinleaf_rng_stream_isolation](../../results/twinleaf_rng_stream_isolation/) and [script](../../simulation/twinleaf/test-random-stream-ledger.cjs). All older one-stream seed traces are experimentally incompatible with new separated-stream data. The Twinleaf `SimpleTactic` lookahead itself still uses ALL_HEADS/NO_SHUFFLE default arbitration while physical games use randomized outcomes; this discrepancy needs a separate policy fidelity audit.

Request: Anyone analyzing matched headless experiments should pin `random_stream_policy` and verify source-level hook/PRNG compatibility. Contact Agent 6 with any reproducible policy/hidden-state leaks or alternative phase-seeding designs.
