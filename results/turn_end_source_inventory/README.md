# Paper Expanded turn-ending effect inventory and action-channel split

## Question

Which effects in the bundled Expanded card pool explicitly end a player's turn, and what event must occur before the generic turn budget closes?

## Audited inventory

`tools/turn_end_source_catalog.py` scans the set-in-scope, effectively legal English prints for explicit wording of the form "your turn ends" or "their turn ends" and classifies each actual source by how its effect arises.

| Action/effect channel | Legal print rows | Important example |
| --- | ---: | --- |
| Legacy Mega/Primal evolution | 92 | M Charizard-EX `xy2-13`; 2026 label-free M Gardevoir-EX `me55c-106m` |
| Ability use | 46 | Koraidon ex `sv1-125` Dino Cry; Zacian V `swsh1-138` Intrepid Sword |
| Supporter effect | 12 | Steven's Resolve `sm7-145`; Café Master `swsh9-133` |
| Item effect | 7 | Rotom Bike `swsh1-181`; Boxed Order `sv5-143` |
| Stadium activated effect | 5 | Lumiose City `me3-77`; Pokémon Research Lab `sm11-205` |
| Delayed opponent attachment reaction | 2 | Slakoth `sm11-167` Lazy Howl; Hypno `sv6pt5-17` Daydream |
| **Total** | **164** | |

These are **print rows**, and reprints may share identical gameplay text. This is a bounded inventory of these printed wording families in the supplied snapshot. It does not claim exhaustiveness for paraphrases such as "end the turn," effects which force attacks, or all future print variants.

## Semantic finding: a printed end does not imply an immediate card-play end

The major subtlety is **which action triggers the end**:

- Playing a Supporter such as Steven's Resolve causes the end after the Supporter's effects have resolved, unless an applicable active Ability such as Metagross Extend exempts that Supporter.
- Playing an Item such as Boxed Order causes an end after the Item's effect resolves, while leaving ordinary Supporter and Stadium quotas untouched.
- A turn-ending Ability (such as Koraidon ex Dino Cry) closes after Ability use; its effect attaches Energy from a separate source zone and does not spend the player's ordinary one-per-turn manual attachment.
- **Playing a Stadium such as Lumiose City from hand does not itself end the turn.** Activating its optional search effect triggers the end afterward. The current Stadium can also have been played on a previous turn, and using its activated effect does not consume the once-per-turn Stadium-play quota.
- A legacy Mega Pokémon-EX turns its evolution into a turn boundary unless a matching effective Spirit Link prevents it. Modern Mega Evolution ex cards have different rules.
- Lazy Howl/Daydream create a delayed next-turn, physical target-bound end condition, not an immediate end of the attacker's turn beyond normal attack rules.

This distinction prevents a graph or simulator from assigning a turn-ending penalty to the wrong action. In particular, a Stadium can be useful as a persistent board effect without committing the player to activate its turn-ending optional action on the same turn.

## Executable model

`tools/direct_action_turn_end.py` handles three immediate-after-completion channels: `item_effect`, `ability_use`, and `stadium_activation`. It verifies the Expanded source print and action channel, binds Abilities to the matching physical in-play print and its enabled status, and demands an exact current Stadium print for its activated effect.

The bridge is deliberately a **completion** action: the card's primary effect has already legally resolved. It then consumes `END_TURN` in the canonical `TurnActionBudget`. It never consumes a Supporter, manual Energy attachment, or Stadium-play quota merely to mark an activated effect's turn boundary.

Other channel-specific models:
- [Supporter closure and Active Ability exemptions](../supporter_turn_end_exemptions/)
- [Legacy Mega / Primal and Spirit Link](../legacy_mega_evolution_turn_end/)
- [Delayed attachment trigger](../hand_attachment_turn_end/)

## Reproducibility

`results/turn_end_source_inventory/reproduce.py` asserts all six channel counts and identifies source witnesses, including the label-free 2026 Mega reprint.

`results/turn_end_source_inventory/reproduce_direct.py` verifies Item turn endings, the distinction between playing and activating Lumiose City, Pokémon Research Lab activation, three printed Ability-ending sources, no false use on non-ending Items or replaced Stadiums, and rejection of suppressed Abilities.

## Boundaries

The physical effect's execution, card movement, timing legality and phase-specific constraints belong upstream. For example, this bridge never performs a Boxed Order search or a Koraidon discard-pile Energy attachment. Its inputs assert those source-card operations were already valid and resolved.

The Stadium source is identified by exact print ID in this narrow projection; an upstream Stadium owner should supply that identity from the live Stadium zone. Ability enablement must reflect the causal lock solver and all relevant printed source conditions before an Ability is executed.

A future event scheduler should connect these completion actions directly to full physical transitions. The inventory provides a finite, auditable list of closure cases to guide that integration.
