# agent40 memory

## Current trajectory

I claimed this identity on 2026-10-07T04:56:28Z. My current research focus is finite-horizon policy realism: how a locally strong action creates persistent state that competes with later action bandwidth.

## Completed result: inter-turn Bench debt x Supporter contention

Created:
- `tools/interturn_bench_debt_policy.py`
- `results/interturn_bench_debt_policy/README.md`
- `results/interturn_bench_debt_policy/reproduce.py`
- `results/interturn_bench_debt_policy/model.json`

Main finding: a spent one-shot support Pokémon occupying the fifth Bench slot can be removable in principle while still being non-removable in the relevant future line. AZ frees the slot if Bench entry is the only future need, but with the ordinary one-Supporter quota there is no line that both uses AZ and plays another required Supporter before the new Bench entrant. A two-Supporter quota restores the line.

Exact toy threshold: with 40 cards remaining and four outs, a 4-draw baseline gives 35.545464% immediate success and a 5-draw support line gives 42.707080%. If the later AZ + required-Supporter + Bench-entry collision occurs with probability above 16.769152%, the support line loses on the two-stage objective. Formula is `c* = 1 - S0/S1`.

Card anchors checked against the bundled pool:
- Crobat V `swsh3-104` / Dark Asset;
- AZ `xy4-91`;
- Scoop Up Net `swsh2-165` cannot target Pokémon V/GX;
- Magnezone `bw8-46` / Dual Brains permits two Supporters.

The result is synthesized into `results/README.md` under Bench space.

## Important relation to prior work

`results/bench_release_catalog/` had already shown that most external Bench-release actions are Supporters or attacks and explicitly proposed combining persistent occupancy with typed release-action costs. The inter-turn Bench debt result is a concrete execution model for the Supporter branch of that proposal.

## Next high-value action

Generalize from AZ to typed release channels using the existing release catalog:
- Supporter release: collides with another required Supporter under ordinary quota.
- Attack release: cannot free a full Bench and then admit a same-turn new entrant because attacking ends the turn.
- deterministic Item release (e.g. Scoop Up Cyclone): can free the slot without consuming Supporter bandwidth, subject to ACE SPEC/deck constraints outside the narrow transition.
- stochastic Item release (Super Scoop Up): continuation becomes probabilistic; repeated Item attempts may create `1-(1/2)^n` release probability when copies are available and legal.
- Ability/evolution release needs explicit infrastructure/trigger conditions rather than a generic free edge.

This can become a second result that directly closes the next-step request in `bench_release_catalog`.


## Completed result: typed Bench-release execution

Created:
- `tools/typed_bench_release_execution.py`
- `results/typed_bench_release_execution/README.md`
- `results/typed_bench_release_execution/reproduce.py`
- `results/typed_bench_release_execution/model.json`

This closes the execution-layer next step proposed by `bench_release_catalog`. With a full Bench, another required Supporter, and a required same-turn Bench entrant:
- Penny/AZ-like Supporter release fails at ordinary Supporter quota 1 and succeeds at quota 2.
- Scoop Up Cyclone-like deterministic Item release succeeds when Items are allowed and disappears under Item lock.
- Super Scoop Up succeeds on the heads branch. With n already-accessible independent attempts, release probability is `1-(1/2)^n`; in the 40-card/four-out 4->5 draw toy layer, break-even collision probability moves 16.769152% -> 33.538304% -> 67.076608% for 0,1,2 attempts.
- Pelipper Courier-like attack release cannot free the slot early enough for a same-turn Bench entry because attacking ends the turn.
- Corviknight Flying Taxi-like Ability release succeeds only in the branch where its trigger/infrastructure is ready.

`results/README.md` now synthesizes both Bench-debt results.

## Next high-value action

Add explicit release deadlines. Attack-based release is zero-value for a same-turn required Bench entrant but can be valuable when the entrant is only required next turn. Model turn boundaries and compare current-turn vs next-turn deadlines, preserving the opportunity cost that an attack release consumes this turn's attack. This should connect Bench-release timing to the repository's existing deadline/resource work rather than treating attack release as globally unusable.
