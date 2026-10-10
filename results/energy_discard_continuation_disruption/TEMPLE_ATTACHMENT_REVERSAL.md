# Temple of Sinnoh reverses the preferred Dragon Impact payment after one Grass attachment

## Source-grounded tactical reversal

The earlier [Regidrago payment witness](../energy_discard_continuation_frontier/) establishes that discarding two Basic Energy cards retains DDE and makes the next Apex Dragon attack **immediately Energy-ready**, while discarding one DDE leaves Basic Grass/Fire/Fire and is initially unready.

Now add the following legal, highly specific matchup line:

1. Regidrago VSTAR has DDE + one Basic Grass + two Basic Fire attached. Salamence ex is in the discard pile, and Regidrago uses Apex Dragon to copy 300-damage Dragon Impact.
2. The player chooses one of the four irredundant ways to discard two Energy units as directed by the copied attack.
3. On its turn, the opponent plays **Temple of Sinnoh** (`swsh10-155`), which makes all attached Special Energy provide only one Colorless Energy with no other effect.
4. On Regidrago's next turn, it has exactly **one Basic Grass Energy in hand** available for the normal Energy attachment. Temple stays in play. No other Energy acceleration or Stadium removal occurs.

**The payment preference reverses.** Discarding DDE itself leaves Grass/Fire/Fire. Attaching one additional Grass makes Grass/Grass/Fire/Fire, immediately satisfying Apex Dragon's Grass/Grass/Fire cost despite Temple.

Every two-Basic payment retains DDE, which Temple makes a single Colorless unit. With one more Basic Grass attachment, neither DDE+Fire nor DDE+Grass supplies both required Grass units and a Fire unit. Those states are not ready for Apex Dragon on that turn.

## Exact attachment deficit

| First Dragon Impact payment | After Temple, before attachment | After attaching 1 Basic Grass | Minimum number of additional Basic attachments to restore Apex |
| --- | --- | --- | ---: |
| **Discard DDE (1 card)** | Grass + Fire + Fire | **Ready**: Grass + Grass + Fire + Fire | **1 Grass** |
| Discard Grass + Fire A (2 cards) | Colorless + Fire | Not ready: Colorless + Grass + Fire | **2 Grass** |
| Discard Grass + Fire B (2 cards) | Colorless + Fire | Not ready | **2 Grass** |
| Discard Fire A + Fire B (2 cards) | Colorless + Grass | Not ready: Colorless + Grass + Grass | **1 Grass + 1 Fire** |

Because a normal turn permits one Energy-card attachment from hand, the minimum two-attachment branches cannot restore this attack in the same turn without a separate acceleration effect. The one-DDE payment can.

The source supports the realism of the extra Basic Grass: the [official published 2025 Expanded Regidrago list](https://www.pokemon.com/uk/features/a-deep-dive-into-the-2025-pokemon-tcg-expanded-format) has **three** Basic Grass Energy copies. Our state uses one already attached and assumes another is in hand; it does not estimate the chance that this hand is reached.

## Verification

`tools/energy_discard_temple_attachment_reversal.py` checks the exact Temple text, Regidrago's Dragon type, and the source-backed four payments. It uses the shared attack-cost matcher after applying Temple's suppression, tries one Grass attachment, and exhaustively enumerates three-symbol Basic Energy type multiset additions to find the **minimum number and types** of Basic attachments each state needs.

Run `python -m tools.energy_discard_temple_attachment_reversal` from the repository root.

## Implications for state-aware optimization

The original two-Basic payment is better on *immediate readiness before the opponent responds*. Yet, after this concrete Stadium intervention, the discarded-DDE branch becomes the only one to restore next-turn Apex via the stated single manual Grass attachment.

This illustrates why a card's discardability and an action's value depend on future access windows and matchup counterplay. A planner that enforces Special Energy suppression, attachment timing, and a known Basic Energy in hand can rank the same payment alternatives differently from one that examines only the post-attack state.

## Limits

The demonstration fixes Temple remaining active. Playing a different Stadium, using Field Blower or other anti-Stadium effects, accelerating Energy, using Legacy Star under a different Stadium state, switching Pokémon, or having a different hand can change the optimal line. Opponent damage, further turns, Prizes and game win probability are not modeled. The result establishes one legal conditional matchup state, not a recommendation to routinely discard DDE against all Stadium decks.
