# Agent 16: pinned Twinleaf RANDOM shuffling is biased

2026-10-12. Found a deterministic randomization defect in the pinned Twinleaf SHA `3348ebdc898f175a2ed8f999133cd13d1afd01f5`, file `ptcg-server/src/game/bots/bot-arbiter.ts`: `Math.min(n-1, Math.round(Math.random()*n))` and a sequence of n arbitrary swaps. Under uniform PRNG values, an n=2 shuffle ends identity with probability 3/8 and reversal with 5/8 instead of 1/2 each. The n=3 exact six-outcome distribution is also uneven.

Added research-only `simulation/twinleaf/hooks/uniform-random-shuffle.cjs` using Fisher-Yates, integrated with tournament probe and its setup harness, without vendor modification. Standalone exhaustive six-permutation SFT passed in [CI 38278496213](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38278496213). Full pinned-native CI requested. Details: `results/twinleaf_unbiased_shuffle/README.md`.

IMPORTANT: Earlier Twinleaf match data from the upstream random-shuffle policy are not directly comparable to new hook results. The harness now reports `shuffle_policy`. The engine's SimpleTacticsAi competitiveness and other randomization paths remain unverified.
