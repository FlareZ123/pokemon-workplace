# Conditional Tyranitar-GX Lost Out versus Huntail Diver's Catch

## Question and card-text evidence

This study grounds the existing destination-program compiler in two real card effects, under the paper Expanded research scope.

- **Tyranitar-GX, Lost Thunder `sm8-121`**: its *Lost Out* Ability sends an opponent's Pokémon Knocked Out by damage from its attacks, together with all attached cards, to the Lost Zone in place of the discard pile. *Dusty Ruckus* has 130 Active damage and 30 damage to each opposing Benched Basic Pokémon. Official card text: https://www.pokemon.com/uk/pokemon-tcg/pokemon-cards/series/sm8/121
- **Huntail, Destined Rivals `sv10-55`**: its *Diver's Catch* Ability can return Basic Water Energy from the owner's Water Pokémon that was Knocked Out by opponent attack damage to hand in place of discard. Official card text: https://www.pokemon.com/uk/pokemon-tcg/pokemon-cards/series/sv10/55
- **Lapras `bw4-25`**: Basic Water, 100 HP, Lightning Weakness, per the bundled card database.

The bounded scenario has Tyranitar-GX attacking with Dusty Ruckus, Knock Out damage of 130 against an opposing 100-HP Lapras with two attached Basic Water Energy and one Double Colorless Energy. Lapras's Lightning Weakness does not increase the Darkness attack damage. The defending player has an evolved Huntail on the Bench, with no applicable Ability suppression. Huntail survives Dusty Ruckus's Bench damage because that attack selects Benched **Basic** Pokémon, whereas Huntail is a Stage 1.

The setup is structurally possible from the printed conditions. The study does not claim that both effect orders are permitted by every tournament's current rulings.

## Conditional destination conflict

The existing route compiler produces:

`Lost Out -> {Lapras: lost_zone, Basic Water 1: lost_zone, Basic Water 2: lost_zone, DCE: lost_zone}`

`Diver's Catch -> {Basic Water 1: hand, Basic Water 2: hand}`

In the repository's *first explicit destination assignment wins* model:

| Supplied effect order | Lapras | Double Colorless Energy | Two Basic Water Energy |
| --- | --- | --- | --- |
| Lost Out before Diver's Catch | Lost Zone | Lost Zone | Lost Zone |
| Diver's Catch before Lost Out | Lost Zone | Lost Zone | Hand |

The exact order solver finds two different endpoint assignments for two possible total orderings. Each branch is independently materialized by the conserved board/ledger kernel, with the complete card-class totals unchanged and the surviving Huntail promoted to the Active Spot.

This replaces the earlier purely abstract three-effect construction with a **concrete pair of printed card-text predicates**. The consequence is conditional on which effect gets applied first. The result is a fork of physical possibilities, **not a determination of who chooses the order or which branch official tournament policy selects**.

## Rulebook boundary and unresolved authority

The supplied Advanced Player's Rulebook v3.4 places Knock Out-triggered effects before KO disposal (E-04) and provides a current-turn-player ordering rule for several Pokémon being Knocked Out simultaneously. Its text does not by itself establish the general precedence of these two different replacement effects on a **single** Knocked Out Pokémon.

Earlier repository work [ko_redirection_authorized_order](../ko_redirection_authorized_order/) documents differing official source interpretations for a related Lost City/Reuniclus situation. This test deliberately does not transfer those chooser conclusions to Tyranitar/Huntail without a card-specific authoritative ruling.

All findings assume qualifying trigger eligibility when the KO window begins and that the compiled destination programs represent the relevant card text. Re-evaluating prerequisites after earlier effects, especially when attached cards have been moved, remains a separately testable step.

## Reproduction

`python results/huntail_lost_out_conflict/reproduce.py` rebuilds the victim-side conserved board from exact Pokémon and attachment instances, compiles both classified route signatures, enumerates the two conditional effect orders, verifies the full KO disposal and survivor promotion under both branches, checks physical totals, and cross-validates the optimized signature projection against its independent uncompressed implementation.

Use the result as a realistic conflict fixture for future sourced ordering and phase-sensitive trigger research. The board simulator currently represents the victim's side; the opposing attacking Tyranitar-GX and attack damage are explicit certified inputs to the fixture, not independently computed with a complete two-player attack engine.
