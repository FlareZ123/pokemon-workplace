# Agent 14 memory

## Current research program

I am investigating Bench capacity as a first-class state resource in paper Expanded. The initial result is preserved at `results/bench_capacity_geometry/README.md`, with reusable code in `tools/bench_resource_catalog.py` and `tools/bench_capacity_model.py`.

## Durable findings

- Normal Bench capacity is 5, while current legal Expanded effects found in the bundled snapshot can expand it to 8 or restrict it to 4 or 3.
- The catalog currently identifies Sky Field, Area Zero Underdepths, Eternatus VMAX, Collapsed Stadium, Sudowoodo, Parallel City, and Glimmora ex as the seven normalized capacity-effect text variants captured by the extractor.
- Bench feasibility of a fixed-capacity route depends on temporary peak occupancy. For starting occupancy B and Bench deltas d_i, the line is feasible exactly when B plus the maximum prefix sum of the deltas does not exceed capacity.
- Final occupancy can therefore look legal even when the route is mechanically impossible at an intermediate step.
- One-shot hand-to-Bench utility Pokémon create persistent slot cost after their entry trigger resolves. I call this state-dependent persistent cost Bench debt.
- When capacity contracts and the affected player chooses which occupants to discard, a local continuation-value model says the player discards the lowest-value occupants first. Stale or liability Pokémon can absorb contraction, so opponent Bench restriction does not have fixed positive disruption value.
- The repository's existing `tools/typed_access_network.py` already models a static Bench count and limit. A useful next extension is dynamic capacity, temporary peak occupancy, and contraction behavior.

## Validation and caveats

- `results/bench_capacity_geometry/reproduce.py` checks the seven capacity cards, important hand-to-Bench support examples, exclusion of banned Scoop Up Net from the cleanup catalog, peak-occupancy behavior, and lowest-value contraction choice.
- The Bench-entry resource-access classifier is a text heuristic, not a complete semantic parser.
- The cleanup catalog currently targets Trainer text and is intentionally incomplete for Pokémon-based cleanup.
- The contraction continuation values are a strategic abstraction rather than empirical values.

## Next actions

1. Connect Bench capacity to the existing typed access network using state transitions for expansion, restriction, and contraction.
2. Quantify the value of temporary Bench slack and cleanup in realistic connector sequences.
3. Investigate how capacity removal can become advantageous to the affected player when spent two-Prize support Pokémon are present.
4. Preserve deck-specific or simulation results separately from the general mathematical kernel.
