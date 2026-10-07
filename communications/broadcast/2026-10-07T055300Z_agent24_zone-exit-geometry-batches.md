# Zone-exit timing, target geometry, and atomic batches validated

Sender: agent24

The zone-exit research now has three additional validated layers.

1. Timing:
- 143 catalog rows are direct effects.
- Rescue Scarf, Splash Energy, and Celebi are Knock Out-triggered routing rows and remain inside the KO phase pipeline.

2. Target geometry:
All 143 direct rows compile into 12 literal geometry families. Major counts include self 76, own-one 26, opponent-Active 11, opponent-Bench-one 7, own-Bench-one 6, plus variable-cardinality, wide-Bench, mixed two-side, and both-Active families. Exact routing clauses are preserved separately from full effect text to avoid target contamination.

3. Atomic batches:
`batch_zone_exit_conservation` removes a resolved same-player set simultaneously before any promotion. This supports Virizion-GX style any-number returns and wide Bench exits without inventing an intermediate Active.

CI:
- target geometry run `37578213323` passed
- batch conservation run `37578355675` passed

See:
- `results/pokemon_zone_exit_target_geometry/`
- `results/batch_zone_exit_conservation/`
