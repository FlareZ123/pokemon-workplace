# Aichi 2026 high-finish archetype mixture: observed proxy and missing testing coverage

**Agent 23, 12 October 2026.** This is a source-grounded *top-finisher composition*, not the 926-player event's entering metagame distribution and not a prediction of future paper Expanded fields.

## Source and scope

The [Limitless CL Aichi Open League statistics](https://limitlesstcg.com/tournaments/566/statistics) list archetype classifications for the **32 ranked players shown in the [event results](https://limitlesstcg.com/tournaments/566)**. The event took place **10 May 2026** in Japan and reports **926 participants**. Therefore these 32 represent selected successful finishes; interpreting the counts as deck usage across all 926 entrants would create severe survivorship bias.

The set of 32 archetype classifications in [data.json](data.json) was transcribed from that statistics page, retaining printed Count and Points, with two clearly labeled *local research coverage* flags.

| Archived high-finisher archetype | Count among 32 | Share |
| --- | ---: | ---: |
| Regidrago | 11 | 34.38% |
| Mega Absol Box | 5 | 15.63% |
| Raichu Electrode Combo | 3 | 9.38% |
| Iron Thorns | 3 | 9.38% |
| Snorlax Stall | 2 | 6.25% |
| Shadow Rider Calyrex | 1 | 3.13% |
| Vileplume Control | 1 | 3.13% |
| Mew Genesect | 1 | 3.13% |
| Mega Lopunny | 1 | 3.13% |
| Raging Bolt | 1 | 3.13% |
| Lillie's Clefairy | 1 | 3.13% |
| Meloetta Donk | 1 | 3.13% |
| Dusknoir Chimecho | 1 | 3.13% |
| **Total** | **32** | **100% before displayed rounding** |

These categories are **archetypes**, not necessarily identical 60-card print lists. For example, Limitless's [card usage analysis](https://limitlesstcg.com/tournaments/566/cards) averages nine provided Regidrago lists even though its event statistics classify eleven top finishers as Regidrago. The same principle applies to other archetypes and Japanese-only versus English-print adaptations.

## Immediate research priorities

**Current manual full-deck Twinleaf matchup selector:** Vileplume, Shadow Rider, Regidrago and Mew/Genesect are available as distinct source-based core archetypes, with some extra counterfactual variants. Together those four archetypes account for **14 of the 32 (43.75%) archived high-finish classifications**. The unselectable 18 of 32 are still an important blind spot. This is input-support coverage, not proof that the bot meaningfully executes any particular list.

**Curated complete 60-card repository references:** the [deck index](../../decks/) already covers, at the archetype level, Regidrago, Mega Absol Box, Raichu Electrode, Iron Thorns, Snorlax Stall, Shadow Rider, Vileplume and Mew/Genesect. Those categories together cover **27 of 32 (84.375%)** classification mentions. Some lists are English-print experimental adaptations of Japanese references, and not every archived original list is represented. Five single-entry archetypes remain without curated references here: Mega Lopunny, Raging Bolt, Lillie's Clefairy, Meloetta Donk and Dusknoir Chimecho.

**Practical engineering order under this *specific observed top-finisher proxy*:** make the existing Mega Absol, Raichu/Electrode, Iron Thorns and Snorlax reference variants selectable and behaviorally audited in a bounded headless environment before spending large compute on marginal synthetic mirror matches. This would raise the potential archetype coverage from 14/32 to 27/32, subject to mapping and legality checks. It does not establish that a 2026 international paper Expanded event would have a similar entrant mixture.

## Reproducibility

[reproduce.cjs](reproduce.cjs) validates all thirteen distinct archetypes, the 32 counted finishes, source metadata, and the two separate coverage totals. It constructs a fixed-frequency probability field from 32 exact integer counts and passes it through the [field optimizer](../../../tools/uncertain_metagame_field.cjs). The 14/32 and 27/32 sums match independent direct category counting. The [scoped Node 20 Windows CI](../../../.github/workflows/twinleaf-evidence-integrity.yml) runs this source-data regression without compiling Twinleaf.

A valid use of the top-32 frequencies in an experiment is a **hypothetical stress-test field based on observed high finishes**, explicitly distinguished from a participant frequency estimate. Feed real matchup score intervals, including unknown [0,1] rows for unsupported opponents, into [uncertain opponent-mixture analysis](../uncertain_metagame_field/). Avoid announcing a numerical paper Expanded win probability from these frequencies and unvalidated bot output.

## Important uncertainty

The distribution of archetypes among all 926 entrants is not reported on the cited statistics page. Top-32 composition can reflect archetype strength, player selection, seed/matchup luck, skill, and tournament structure. The Japanese Expanded card pool and available English paper printings are also not identical by assumption. Future work should source full entrant metagame counts if legitimately available, then obtain reliable matchup-specific evidence under fully reviewed card semantics and stronger automated policies.
