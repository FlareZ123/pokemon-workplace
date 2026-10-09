# Player-chosen Bench contraction with complete physical-card conservation

## Research question

How can a forced Bench-size reduction be resolved after the affected player chooses the Pokémon to discard, while preserving every evolution card, attachment, and zone count?

The implementation `tools/bench_contraction_batch_conservation.py` composes the existing atomic multi-Pokémon exit engine with a capacity-change validator. It returns a stable `StackBoardMaterialState` whose surviving Bench fits the new capacity, plus the identity of every discarded Pokémon object, every removed Pokémon stack card, and every discarded attachment.

It establishes the missing physical bridge between [bench_contraction_choice_space/](../bench_contraction_choice_space/) and the shared materialized-stack/zone-exit machinery.

## Rules and semantics

The Advanced Player's Rulebook permits card text to modify Bench capacity. Collapsed Stadium and the restricting side of Parallel City force the affected player to discard excess Benched Pokémon until the new limit is satisfied.

Those forced discards are **not Knock Outs**. They do not take Prize cards. An entire evolved Pokémon in play leaves, and attached cards go to their ordinary discard zone under those Stadium effects.

The new transition selects `max(0, n-new_capacity)` distinct IDs from the existing Bench, where `n` is the number of Benched Pokémon. An Active ID, unknown ID, duplicate ID, or wrong number of selected Pokémon is rejected.

All selected Pokémon leave in one atomic batch via `batch_zone_exit_conservation.leave_play_batch_before_promotion()`; the physical-card destination for both stack cards and attachments is `discard`. The pending state's capacity is then set to the new maximum before reconstructing the ordinary board. Because only Bench objects are removed, the Active remains unchanged and no promotion is required.

The implementation returns no result for a terminal `board=None`, and changing to an expanded capacity with no forced discards returns a valid updated state with the same identity ledger.

## Detailed six-Pokémon witness

The reproducible initial state has:

- one Active Bidoof;
- five Benched Pokémon: an evolved Tarountula -> Spidops, Solrock, Lunatone, Regirock, and Regice;
- one Grass Energy and one Muscle Band attached to the evolved Spidops.

Every physical copy exists in an exact `IdentityLedger` and is bound to its board object.

Contraction from **five Benched to four** yields five possible one-Pokémon discard choices. When the player selects the evolved Spidops object, the following **four physical cards** go to the discard pile:

| Physical card | Destination |
| --- | --- |
| Tarountula (lower evolution card) | discard |
| Spidops (current top card) | discard |
| attached Grass Energy | discard |
| attached Muscle Band | discard |

The other four Benched objects and the Active Bidoof remain unchanged. Each selected card is dematerialized back into its exchangeable discard count, and the conservation invariant confirms no card was lost or duplicated.

A direct **five-to-three** contraction has ten possible two-Pokémon discard sets. An explicitly chosen sequential **five-to-four-to-three** path routes both selected Pokémon and attached cards correctly, without using the Knock Out or Prize-taking pipeline.

## Validation

Run `python tools/bench_contraction_batch_conservation.py --self-test` to check:

1. all five 5→4 choices and the four-card evolved stack plus attachments;
2. ten distinct 5→3 choices with exact card conservation;
3. two successive chosen contractions, with all intermediate ledger states valid;
4. rejection of illegal selections and Active discards;
5. a nonconstricting capacity increase preserving all physical identities.

Run the file without flags to show JSON for a selected contraction.

[GitHub Actions run 37920407200](https://github.com/FlareZ123/pokemon-workplace/actions/runs/37920407200) completed successfully.

## Research significance

This separates three responsibilities:

- The **capacity mechanics** determine the permitted survivor-set cardinality.
- The **player policy** chooses which complete Pokémon objects to discard.
- The **physical zone engine** conserves the exact cards routed off the board.

The earlier `board_object_kernel.contract_bench()` applies one additive-value default. Here, the complete legal choice is passed into the stack-bearing physical state. This supports continuation-aware payoff policies with the same underlying mechanical transition.

The helper `enumerate_contractions()` also enumerates and materializes every legal choice to enable small-board exact game-state evaluation.

## Limitations and next work

The caller must supply the applicable Bench capacity based on actual simultaneous Stadiums, Abilities, and other effects. Current code does not evaluate which capacity change happened first or update other players. Triggered effects responding to a Pokémon leaving play, card-text replacement effects, and external restrictions beyond the selected Stadium family also remain outside this bridge.

The next useful integration is to score each legal physical successor using a validated ability-dependency evaluator, then connect access to actual Supporter and Stadium timing. A prerequisite Ability may disappear when one named partner is discarded, so the valuation of survivors should be conditioned on whether its source, partner, and activation resources remain usable.
