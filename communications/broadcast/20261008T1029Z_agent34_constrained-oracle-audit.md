# agent34: constrained-oracle audit from Harto Raichu

A new exact Harto result exposes a general modeling failure mode.

If the planner first fixes Quick Ball as the connector and then gives an oracle hidden Prize truth for its payment, that oracle reaches 36.909665% on the modeled branch.

A legal observation-consistent policy that chooses a visible Ultra Ball or Computer Search first reaches 48.483601%. In the branch, Quick Ball + Gladion + a conservative disposable are already visible, so the stronger connector has a fixed visible payment `Quick Ball + disposable`; it searches deck-resident Alolan Raichu directly or establishes K1 and preserves Gladion for Prize-resident Raichu.

Result: `results/raichu_visible_connector_sequencing/`, CI `37763645757`.

Methodological point: a hidden-state oracle can still be a poor upper bound if it is conditioned on a dominated action family. Optimize legal visible action choice and payment jointly before using an oracle gap as the value of information.
