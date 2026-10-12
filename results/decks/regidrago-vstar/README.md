# Regidrago VSTAR | Aichi 2026 10th place

**Evidence:** Haruku Yoshioka, Aichi Open League 10th place, 2026-05-10. Published Regidrago VSTAR toolbox using discard-pile Dragon payloads.

**Status:** Published 60-card paper Expanded tournament reference. Representative English print IDs are sourced from the [fully print-checked project baseline](../../competitive_deck_baselines/README.md), and may not be the actual Japanese printing. The source validator is [regidrago_reproduce.py](../../competitive_deck_baselines/regidrago_reproduce.py). Construction checked against the project's October 12, 2026 Expanded English snapshot; regional status and later changes remain to be independently checked.

### Pokémon (20)

| Qty | Card | English print ID |
| ---: | --- | --- |
| 4 | Regidrago V | `swsh12-135` |
| 3 | Regidrago VSTAR | `swsh12-136` |
| 2 | Budew | `sv8pt5-4` |
| 1 | Dragapult ex | `sv6-130` |
| 1 | Dialga-GX | `sm5-100` |
| 1 | Koraidon ex | `sv5-120` |
| 1 | Kyurem | `sv6pt5-47` |
| 1 | Hisuian Goodra VSTAR | `swsh11-136` |
| 1 | Dedenne-GX | `sm10-57` |
| 1 | Squawkabilly ex | `sv2-169` |
| 1 | Tapu Lele-GX | `sm2-60` |
| 1 | Latias ex | `sv8-76` |
| 1 | Marshadow | `sm10-81` |
| 1 | Wobbuffet | `xy4-36` |

### Trainer (30)

| Qty | Card | English print ID |
| ---: | --- | --- |
| 2 | Professor's Research | `sv8pt5-122` |
| 2 | Guzma | `sm3-115` |
| 1 | Iono | `sv2-185` |
| 1 | Carmine | `sv6-145` |
| 1 | Lillie's Determination | `me1-119` |
| 1 | Marnie | `swsh1-169` |
| 1 | Raihan | `swsh7-152` |
| 1 | Crispin | `sv7-133` |
| 1 | Faba | `sm8-173` |
| 3 | Quick Ball | `swsh1-179` |
| 3 | Mysterious Treasure | `sm6-113` |
| 3 | Battle VIP Pass | `swsh8-225` |
| 3 | VS Seeker | `xy6-110` |
| 1 | Hisuian Heavy Ball | `swsh10-146` |
| 1 | Battle Compressor Team Flare Gear | `xy4-92` |
| 1 | Super Rod | `sv2-188` |
| 1 | Prime Catcher | `sv5-157` |
| 2 | Muscle Band | `xy1-121` |
| 1 | Parallel City | `xy8-145` |

### Energy (10)

| Qty | Card | English print ID |
| ---: | --- | --- |
| 4 | Double Dragon Energy | `xy6-97` |
| 4 | Grass Energy | `bw1-105` |
| 2 | Fire Energy | `bw1-106` |

**Count verified:** 60 cards.

The restricted K0 first-Item study models joint Regidrago V access plus discarded Dragapult ex as 13.257301% at D=0. This is not attack readiness or a match win rate.

**Energy-hand causal correction:** The [initial Crispin deck-supply study](../../tests/aichi_regidrago_crispin_post_trifrost/) compares **different conditioned card allocations**: a known Grass versus a known Fire removed from an otherwise unknown 58-card pool. Its 99.0279% versus 89.6518% two-type stock figures with six Prizes describe *different initial information states*. The [matched-hand counterfactual](../../tests/aichi_regidrago_crispin_paired_causal/) shows that when the same hand already contains both Basic Grass and Fire, choosing either for Regidrago's copied Trifrost leaves the future searchable deck stock **unchanged** (84.7163% dual-type stock in the exact naturally conditioned cohort, with zero causal gap). The [natural first-eight exposure model](../../tests/aichi_regidrago_t1_natural_choice/) finds Regidrago V + DDE + both Basics together in 1.3746% of accepted natural opening views. Remaining hand/discard identities still differ and can matter for later actions. No win-rate claim or 60-card swap follows.

**Source-checked conditional continuation:** [Trifrost -> Super Rod -> Crispin](../../tests/aichi_regidrago_super_rod_bridge/) exhibits a matched-state exception. If both Fire Energy are held and no Fire is in deck or discard, intentionally **discarding one Fire** through copied Trifrost allows Super Rod to return it to the deck next turn; Crispin can then attach Grass and a second held DDE can be manually attached to restore Apex Dragon. Spending Grass in that exact state leaves no Fire available to Super Rod, blocking this narrow next-turn route. Another Item that discards Fire or an earlier Fire already in discard removes the blockade. This is a deterministic constrained line, with no estimated frequency or match-win inference.

**Unresolved:** All decks still require legal and capable opponent policies, actual complete-game simulation or match observations, a representative field, and matchup-aware resource preservation before being ranked by expected win percentage.
