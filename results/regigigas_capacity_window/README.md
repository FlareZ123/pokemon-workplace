# Ancient Wisdom versus Bench contraction: a conserved order-sensitive Regigigas line

## Strategic question

Can a player obtain real, physically conserved value from a full-board conditional Ability immediately before a Bench-restricting Stadium takes effect, even though the restriction makes that Ability unusable afterward?

Yes. The Expanded-legal Regigigas `swsh10-130` **Ancient Wisdom** Ability is an exact-card witness. Its text requires Regirock, Regice, Registeel, Regieleki, and Regidrago in play and allows attaching up to three Energy from the discard pile to one of the player's Pokémon once during the turn. The source Regigigas adds a sixth required Pokémon.

With Regigigas Active and the other five required Pokémon Benched under a five-slot limit, the full condition is present. Changing to a four-slot Bench by playing Collapsed Stadium discards at least one required partner and invalidates the named guard. However, an Energy attachment completed before that contraction remains on its receiving Pokémon.

Implementation and tests: `tools/regigigas_capacity_window.py`, using the name-guard catalog plus the stack-bearing `IdentityLedger` and [bench_contraction_batch_conservation/](../bench_contraction_batch_conservation/) transition.

## Model and assumptions

The executable physical fixture contains:

- Regigigas Active;
- all five other named Regi Pokémon on the Bench;
- three Basic Grass Energy cards in the discard pile;
- each Pokémon represented by one exact materialized card in the identity ledger;
- no Ability lock or other effect preventing Ancient Wisdom.

The fixture chooses print `swsh10-130`; its required named set and five-slot lower bound are checked against the catalog compiled from the card database.

The Ancient Wisdom evaluator checks its named prerequisite, once-per-turn usage flag, and actual discard Energy availability, then materializes up to three selected Basic Grass Energy copies from discard and attaches them to Regigigas in the physical board model. It does not model other types of Energy, destination restrictions, or general Ability execution.

For controlled order comparison, both lines begin in the same legal six-Pokémon board. The player controls whether the ability is used before the Stadium restriction. The contraction is applied exactly once by the player, discarding one of the five named Benched Pokémon through the physically conserved Bench-choice transition.

## Exact order comparison

| Sequence | Outcome |
| --- | --- |
| Use Ancient Wisdom, attach three Grass Energy, then reduce Bench capacity 5→4 | Three Energy remain attached to Regigigas; one required Regi leaves play, so the Ability's named guard is now false |
| Reduce Bench capacity 5→4, then attempt Ancient Wisdom | Every legal choice of one Benched discard removes a uniquely named required Regi, so Ancient Wisdom is unavailable and all three Energy remain in the discard pile |

In the model, the first line increases Regigigas's attached Energy by **3**, while the reversed order increases it by **0**. Physical-card conservation is checked independently for both outcomes. This is an attachment-bandwidth distinction; no game winner, Prize exchange, damage calculation, or deck win probability is inferred.

The model validates all **five** legal choices for which Regi the player discards when reducing to four slots. Each choice breaks the condition, so no selection can preserve Ancient Wisdom under the restriction as modeled.

## Restoration requires material recovery

A capacity increase from four to eight can restore structural room for all six required Pokémon. It cannot by itself retrieve a previously discarded required Regi.

The regression changes the contracted board's capacity to eight with no other physical movement and verifies that the named condition remains false. Recovering the discarded card and putting the missing named Pokémon back into play would require an additional legal line.

This isolates two separate resource deficits after a Bench contraction:

1. **Geometric:** at the restrictive capacity, six distinct names cannot fit.
2. **Material:** even when capacity reexpands, a previously discarded named card must be recovered and put into play again.

## Validation

Run `python tools/regigigas_capacity_window.py --self-test` for five checks:

- exact card-list name guard, source print, and required Bench slots;
- ability-first sequence retaining three attached Energy after the contraction;
- contraction-first sequence disabling the ability for every legal discard choice;
- reexpansion without physical recovery failing to restore the condition;
- use-once and chosen Energy-count bounds.

Run without flags for a reproducible JSON comparison.

[GitHub Actions 37920684422](https://github.com/FlareZ123/pokemon-workplace/actions/runs/37920684422) passed both unit tests and the executable example.

## Larger implication

A prerequisite-dependent action creates a **deadline** before the card effect that destroys its prerequisite. The optional order of use can change the reachable physical state even when the final board has the same capacity and loses the same Pokémon.

For an optimizer, named guard satisfaction at the end of a sequence is therefore insufficient. It must check each action's prerequisites at the time the action is resolved, conserve the effects already achieved, and distinguish future restoration of capacity from restoration of missing material.

## Limits

The executable witness assumes the user has access to the restricting Stadium on their turn and may play it after their available Ancient Wisdom activation. It does not model an opponent's ability to remove the source, all alternative ways to establish a sixth Pokémon under other effects, actual timing of Energy attached from discard if replacing card text, or future Energy movement/disruption. Three Basic Grass Energy cards are available by construction and chosen only for a narrow, auditable timing example.
