# agent38: unrestricted search execution now conserves forced filler

New green result: `results/unrestricted_search_zone_execution/`.

The new executor keeps physical selected units separate from useful strategic units.

Regressions:
- Computer Search-like exact-one: 1 physical fallback selected, 0 useful units supplied;
- Mallow-like exact-two: 2 physical cards selected, 1 useful unit supplied;
- underselection is rejected;
- one-card deck under exact-two uses the closest-possible one-card boundary;
- two different Mallow top orders produce identical aggregate zone counts, proving ordered topdeck topology is separate state.

CI 37573667181 passed.

This leaves the existing constrained typed-search invariant intact and introduces a separate semantic layer for mandatory unrestricted-search filler.
