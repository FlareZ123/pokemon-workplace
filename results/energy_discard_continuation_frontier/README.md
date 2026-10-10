# Continuation-aware Energy discard frontier: Regidrago VSTAR

## Research question

Is minimizing the number of physical Energy cards discarded sufficient to preserve a copied attacker's next-attack readiness?

**No.** This is a constructed, card-text-grounded counterexample, rather than a gameplay win-rate claim.

## Concrete legal card sources

- Regidrago VSTAR (Silver Tempest, `swsh12-136`), **Apex Dragon**: cost Grass, Grass, Fire; copies an attack of a Dragon Pokémon in the discard pile.
- Salamence ex (Journey Together, `sv9-114`), **Dragon Impact**: 300 damage; `Discard 2 Energy from this Pokémon.`
- Double Dragon Energy (Roaring Skies, `xy6-97`): attached to Dragon Pokémon, provides every Energy type and two units at a time.

The script checks these three printed cards against the local `resources/` database and the snapshot's Expanded set flags.

## Attachment state and result

Regidrago VSTAR has four physical Energy cards providing five Energy units:

1. Double Dragon Energy, two units, every type;
2. Basic Grass Energy, one Grass unit;
3. Basic Fire Energy A, one Fire unit;
4. Basic Fire Energy B, one Fire unit.

Regidrago can initially pay Apex Dragon's Grass/Grass/Fire cost, and Salamence ex is assumed to be in the discard pile. After Apex Dragon copies Dragon Impact, it must discard two Energy units.

| Irredundant payment | Physical cards discarded | Remaining Energy units | Apex Dragon energy-ready afterward? |
| --- | ---: | ---: | --- |
| Double Dragon Energy | 1 | 3 | **No**: Grass/Fire/Fire has only one Grass |
| Basic Grass + Basic Fire A | 2 | 3 | **Yes**: DDE + Fire covers Grass/Grass/Fire |
| Basic Grass + Basic Fire B | 2 | 3 | **Yes** |
| Both Basic Fire cards | 2 | 3 | **Yes**: DDE + Grass covers Grass/Grass/Fire |

The globally minimum physical-card payment is the **only** enumerated payment that fails to retain the next Apex Dragon cost. All three two-card payments retain that cost.

In every row, exactly two Energy units are removed, and three Energy units remain. The difference is the *types still provided* and the conditional two-unit card that remains attached.

## Method and validation

`tools/energy_discard_continuation_frontier.py` enumerates irredundant physical-card subsets of a generic Energy-unit discard requirement. Each card is indivisible. A payment can overshoot the required units only where the physical provider itself is indivisible; no added card may be redundant. For each payment it uses the shared `max_typed_match` matcher in `tools/energy_discard_solver.py` to test whether retained provider slots satisfy the future attack's typed Energy cost.

Local independent tests enumerated all unit arrays of one to five cards with each card supplying one, two, or three Energy, across requirements zero to seven; candidate payments agreed with brute-force irredundancy predicates. The concrete source-backed scenario and four-payment assertions passed.

Reproduce from the repository root with `python -m tools.energy_discard_continuation_frontier`.

## Interpretation and limitations

Minimizing physical-card loss is a poor proxy for minimizing the cost of the resulting state. The optimization objective should retain attack-readiness constraints, future action values, and provider flexibility. The finding refines the earlier `results/apex_dragon_special_energy_burden/` minimum-card metric without invalidating its physical-card counts.

The solver's generic payment enumerator is a controlled model, not a comprehensive interpreter of all discard text. It assumes the attachment's provider profile is already active, does not handle typed or named Basic Energy discard clauses, and does not simulate subsequent opponent turns, Energy recovery, attack damage prevention, or game outcomes. Regidrago's continued survival is assumed when assessing next-attack readiness.

The rules basis is the Advanced Player's Rulebook's multi-unit Ignition Energy example, its requirements for attack costs and copy attacks, and the source card texts. Legal reprint/ban adjudication outside the bundled snapshot is not proved by this demonstration.
