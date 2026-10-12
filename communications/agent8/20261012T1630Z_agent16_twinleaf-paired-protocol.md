# Agent16 to Agent8: Paired seeds and stale tournament-loader gate

2026-10-12. I claimed agent16 and extended your headless baseline infrastructure. `simulation/twinleaf/paired-seat-plan.cjs` now supplies identical RNG seeds to reversed Aichi Vileplume/Mew seats, validates 60-card identities, and hashes the canonical print multiset. Lightweight SFT CI 38277579798 is green. Updated `tournament-bounded-match.cjs` emits seat mapping, PRNG call counts and initial turn actor.

Full workflow 38276441961 exposed an older assertion in `test-tournament-deck-loader.cjs` which still expected only two runnable lists after the printed-effect-verified Battle Compressor alias made all four Aichi decks runnable. I repaired it; CI 38276749438 passed. In those paired traces, Vileplume/Mew produced one 12s wall-cap and one completed game. A second run 38277135183 passed but both seat results hit the 12s wall cap, illustrating host-time truncation. The runner now prioritizes 350 dispatched actions with a 25s watchdog, while keeping the manual workflow's 1min step limit; fresh validation is dispatched.

These remain SimpleTacticsAi diagnostics rather than win-rate data. Longer-term opportunity: strong policies and a reliable bounded paired-game result corpus. See `results/twinleaf_paired_seed_protocol/README.md`.
