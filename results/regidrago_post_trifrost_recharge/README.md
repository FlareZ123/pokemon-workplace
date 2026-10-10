# After Trifrost, Regidrago needs another Energy acceleration action

## Question

The [Timeless-GX bonus-turn Kyurem Trifrost line](../regidrago_bonus_turn_mimikyu_snipe/README.md) can knock out an exposed 70-HP Mimikyu, but copied Trifrost's first clause discards **all Energy from the attacking Regidrago VSTAR**. From zero attached Energy, how can Regidrago attack with Apex Dragon again on its next turn?

## Exact Energy condition

Regidrago VSTAR's Apex Dragon costs **Grass, Grass, Fire** (three Energy units). Its Dragon typing allows Double Dragon Energy to attach, supplying any two Energy types/units toward its cost. One Double Dragon Energy plus **one Basic Grass or one Basic Fire** satisfies the cost:

| Physical attached cards | Available relevant Energy | Apex Dragon ready? |
| --- | --- | --- |
| One Double Dragon alone | Two flexible units | No |
| One Double Dragon + Basic Grass | Flexible two plus Grass | Yes |
| One Double Dragon + Basic Fire | Flexible two plus Fire | Yes |
| One Basic Grass + one Basic Fire | Grass + Fire | No |

This makes a second attachment channel necessary to restore Apex Dragon from zero in one ordinary turn. Under the present model the two attachments are the once-per-turn manual attachment and one Supporter-based acceleration.

## Four named deterministic routes

Each line is conditional on having an active surviving Regidrago VSTAR with zero attached Energy, an unused manual attachment, an available Supporter channel, and live card effects:

| Line | Conditions and actions |
| --- | --- |
| Crispin + DDE from hand | Crispin searches two *different* Basic Energy types in deck, attaches one to Regidrago, places the other in hand; manually attach held Double Dragon Energy |
| Raihan + DDE from deck | At least one of your Pokémon was KO'd on the opponent's preceding turn; Raihan attaches a Basic Energy from discard to Regidrago, then searches a Double Dragon Energy into hand; manually attach it |
| Crispin + Legacy Star + DDE from discard | Use Crispin to attach a Basic, then unspent Regidrago VSTAR power Legacy Star to recover discarded DDE into hand; manually attach DDE |
| Raihan + Legacy Star + DDE from discard | With prior-turn own KO, Raihan attaches discarded Basic and performs its deck search, then unspent Legacy Star recovers DDE from discard; manually attach DDE |

The first and third routes require both Grass and Fire Basic Energy available in deck for the chosen two-card Crispin line. The second and fourth require a **previous-turn own Pokémon KO** and discarded Basic Energy. Legacy Star is a once-per-game VSTAR Power; it discards seven cards from the top of the player's deck before recovering up to two from discard, so its availability, deck remaining and timing must be respected. The listed Legacy sequences execute the relevant Supporter search/attachment **before** Legacy Star's top-seven discard.

Raihan's any-card deck search follows its successful discard-to-board Basic Energy attachment. For the last line the deck must contain at least one searchable card, although the search output can be strategically incidental. A VSTAR Power used earlier in the game cannot be used again.

These are **availability witnesses**. Whether the player can reach the necessary DDE, Crispin/Raihan and Basic Energy zones at the right time is a separate problem. If the opponent has not knocked out one of Regidrago's Pokémon on the immediately preceding turn, the Raihan route is illegal even when Raihan is in hand.

## Published Aichi list observations

All nine published CL2026 Aichi Open League Regidrago lists carry Double Dragon Energy, three or four copies apiece (34 copies total). Eight lists carry Crispin (nine copies total). **All nine carry Raihan (11 copies total)** and Basic Grass and Fire Energy, although in-game zone distribution varies.

The per-list source URLs and counts are preserved in [the CL Aichi fixture](../regidrago_budew_promotion_baselines/aichi9_counts.json), originally obtained from https://limitlesstcg.com/tournaments/566/cards.

Card-text source IDs: Regidrago VSTAR `swsh12-136`, Kyurem `sv6pt5-47`, Crispin `sv7-133`, Raihan `swsh7-152`, Double Dragon Energy `xy6-97`. The repo rulebook establishes separate normal Energy attachment (one per turn) and additional attachments by card effects.

## Reproduction and limits

`tools/regidrago_post_trifrost_recharge.py` enumerates four named conditional action routes. The regressor `results/regidrago_post_trifrost_recharge/reproduce.py` validates source print text, exact Energy allocation, route prerequisites, ability use, Raihan prior KO condition, and observed nine-list counts.

Run `python results/regidrago_post_trifrost_recharge/reproduce.py` for full witnesses and negative checks.

This model deliberately excludes other possible Energy acceleration, hand searches, prize randomness, Item lock, draw probabilities, attached-Energy transfer, inter-turn Pokémon changes and actual Regidrago survivability. It does not assign success probability or claim the four routes are exhaustive for the full format.

## Implication

A Trifrost snipe costs Regidrago more than its next attack opportunity: it can create a **follow-up Supporter or VSTAR-Power dependency**. Crispin demands appropriately typed Basic Energy still in the deck. Raihan demands a recent KO on Regidrago's side and discarded Basic Energy, which may be absent after an opponent turn focused on recovery rather than Knock Outs. Legacy Star can repair a discarded Double Dragon Energy but expends a once-per-game resource.

Consequently, comparing the Trifrost and Budew bonus-turn branches should account for post-snipe attacker recovery, not simply whether one Mimikyu is Knocked Out.
