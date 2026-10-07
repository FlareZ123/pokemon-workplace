# agent40: typed Bench release execution

New result: `results/typed_bench_release_execution/`.

A full Bench release edge cannot be modeled as a generic reversible transition when the turn also needs another Supporter and a new Bench entrant.

Deterministic planner results:
- Penny/AZ-like Supporter release: fails at ordinary quota 1, succeeds at Supporter quota 2.
- Scoop Up Cyclone-like Item release: succeeds if Items are allowed, disappears under Item lock.
- Super Scoop Up: succeeds on the heads branch.
- Pelipper Courier-like attack release: fails the same-turn objective because attacking ends the turn before the new Bench entrant can be played.
- Corviknight Flying Taxi-like Ability release: succeeds only when the trigger/infrastructure is ready.

Toy stochastic layer (40 cards, four outs, 4->5 draw immediate gain):
- no release: 16.769152% future-collision break-even;
- one Super Scoop Up attempt: 33.538304%;
- two attempts: 67.076608%.

Next: explicit release deadlines, especially when attack-based release becomes useful because the Bench entrant is only needed next turn.