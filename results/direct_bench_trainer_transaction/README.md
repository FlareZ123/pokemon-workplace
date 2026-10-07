# Atomic direct-Bench Trainer transaction

## Question

Can a direct-Bench Trainer such as Nest Ball use the repository's existing atomic Trainer lifecycle without pretending the searched Basic Pokémon ever entered the hand?

Yes.

Implementation: `tools/direct_bench_trainer_transaction.py`  
Regression: `results/direct_bench_trainer_transaction/reproduce.py`

## Composition

The direct-Bench compiler projects Trainer profiles onto the shared `CompiledTrainerSearchProfile` schema. Destination remains outside that schema.

The shared `trainer_search_transaction` now accepts an explicit search destination, with `hand` retained as the default for every existing caller. All pre-existing dependent CI remained green after this change.

For a direct-Bench Trainer, the shared transaction routes the exact typed target selection into a private `direct_bench_selected` staging zone. The direct-Bench transaction immediately consumes those staged copies by materializing them as in-play Basic Pokémon board objects.

The searched Pokémon therefore never occupies `hand`.

## Nest Ball witness

The regression executes Nest Ball `sv1-181` searching Tapu Lele-GX `sm2-60`.

The atomic result has:

- Nest Ball moved from hand through the resolving-Trainer lifecycle into discard;
- the selected Tapu Lele-GX removed from the physical deck;
- no Tapu Lele-GX count in hand;
- no residue in the private staging zone;
- one stable Tapu Lele-GX instance bound to a new Bench Pokémon object;
- unchanged Item turn budget;
- exact card-class conservation across the combined transition.

A full-Bench state is rejected before the Trainer transaction starts.

## Why the private staging zone matters

Routing the searched card through hand would make the final zone counts look correct after a later Bench placement, while encoding the wrong intermediate semantics.

That intermediate error could become observable to:

- effects that care about cards entering or leaving hand;
- hand-to-Bench Ability triggers;
- provenance or causal audits;
- future action sequencing that treats a searched card in hand as temporarily available.

The private staging zone makes the transaction atomic without asserting a false game zone.

## Backwards compatibility

`trainer_search_transaction.py` still defaults to `search_destination_zone="hand"`.

The repository workflows triggered by the destination generalization all passed, including Trainer transaction, hidden-state search, provenance, continuation-aware discard, reacquisition, optional-discard, and replacement-contention regressions.

## Boundaries

The current direct-Bench Trainer transaction covers the positive search branch. It does not yet integrate the following shuffle/K1 belief update, target-selection signaling, or Battle VIP Pass's first-turn regression in this result.

Those are the next composition layer. The physical destination and Trainer lifecycle are now ready for that bridge.
