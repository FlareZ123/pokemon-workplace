# Real Aichi Crobat V Dark Asset: physical Bench entry and draw-positive payment

## Research question

The published [Aichi Mega Absol ex/Garbodor 60](../competitive_deck_baselines/absol_garbodor_kobayashi_2026.json) contains exactly one Crobat V (`swsh3-104`), whose **Dark Asset** draws cards up to six when **played from hand onto the Bench during the turn**. How often does this actual card provide a *legal, draw-positive* first-turn line after proper setup, rather than simply being found in a card-access graph?

The [Forest Seal Stone comparison](../absol_garbodor_stone_bridge/) already showed that cutting this Crobat removes the deck's only Stone-compatible Pokémon V. This companion study isolates **Dark Asset's separate trigger and hand-size gate** under explicitly constrained play.

## Physical first-turn model

A seven-card random opening is accepted only if it contains at least one Basic Pokémon. One Basic from that opening becomes Active, all other opening Basics may remain in hand, six hidden Prize cards are dealt, and the first natural draw occurs. In the simplified continuation the Bench begins empty and the hand has exactly **seven cards** after reserving the starting Active and taking the first draw.

Crobat V can legally trigger Dark Asset if played **from hand onto Bench**. Thus:

- If Crobat was the **only Basic** in the original opening, it is forced Active; a later naturally drawn Basic cannot retroactively restore Crobat's hand-to-Bench trigger.
- If Crobat was held alongside another opening Basic, choose the other Basic Active and reserve Crobat for a turn action. A first-natural-draw Crobat can also be played onto the Bench because the accepted opener already supplies an Active Pokémon.
- A Crobat put **directly from deck onto Bench by Battle VIP Pass** does *not* satisfy the printed hand-to-Bench trigger. This may still establish a Stone-compatible V.
- A Crobat obtained **into hand** via Quick Ball, Ultra Ball, Pokémon Communication, or Hisuian Heavy Ball may subsequently be played onto Bench and trigger the Ability.
- At seven cards after the Active/draw accounting, merely playing Crobat onto Bench leaves **six cards**. Dark Asset then draws zero. Playing an available extra Basic onto Bench or using the one normal Energy attachment first reduces the hand, making one Dark Asset draw possible.
- A paid Quick Ball targeting Crobat consumes its Item and one held Energy for the discard, then obtains Crobat and Benches it, leaving five cards in hand and enabling **one** Dark Asset card. An Ultra Ball with two held Energy leaves four and enables **two** cards. Pokémon Communication with a spare Pokémon other than the mandatory Active leaves five, enabling one draw.
- Hisuian Heavy Ball can recover a Prized Crobat to hand, but the Heavy Ball exchange and Crobat Bench play alone leave six; an additional held Energy attachment or spare Basic Bench play enables a positive draw.

These deliberately enumerate *one immediate source plus up to one simple extra hand-reducing action*. They exclude other playable Trainers, future turn actions, draw sequences after Dark Asset, and any opponent or self-imposed Ability locks.

## Exact conditional probabilities

| Distinct event | Published 2 Mega | +Mega / −Temple | +Mega / −Crobat |
| --- | ---: | ---: | ---: |
| Crobat physically seen by first draw | 17.326491% | 16.607538% | 0% |
| Opening Crobat **forced Active** | 5.549930% | 4.656517% | 0% |
| Direct legal hand-to-Bench entry | 11.776560% | 11.951021% | 0% |
| Direct entry with one specified hand-shrinking move | 9.245594% | 9.643912% | 0% |
| Paid Quick Ball → Crobat, draw-positive | 18.609685% | 18.928759% | 0% |
| Paid Ultra Ball → Crobat, draw-positive | 2.996230% | 3.068852% | 0% |
| Paid Pokémon Communication → Crobat, draw-positive | 5.338944% | 5.768966% | 0% |
| Prized Crobat → Heavy Ball, draw-positive with extra move | 0.959454% | 0.999631% | 0% |
| **Union: at least one declared draw-positive Dark Asset line** | **35.280897%** | **36.414400%** | **0%** |

The named source rows heavily overlap and must not be summed. All probabilities condition on a Basic-valid opening and integrate full six-card Prize uncertainty. The +Mega/−Temple variant increases *this distinct restricted Dark Asset availability metric* over the published list, partly because another Basic starter makes Crobat less likely to be forced Active.

A further **17.534480%** of published-deck accepted starts physically have a Battle VIP Pass and a Crobat still in deck by the first draw. That is a *Crobat-to-Bench-only route*, **not** a Dark Asset trigger. It can overlap with valid Dark Asset routes through other cards.

The union is the chance that at least one declared positive-draw line is feasible, under its hypothetical Energy-discard and preservation policies. It is **not a prediction that Dark Asset gets used in 35% of matches**, and it is not an upper bound across all possible turn sequences.

## Exact calculation and verification

`tools/mega_absol_crobat_darkasset.py` reuses the 13-card-category real-deck partition from `tools/mega_absol_stone_bridge.py` and enumerates exact Basic-valid openings and first draws. It integrates the Crobat-Prized count with binomial coefficients; results are exact rational `Fraction` values.

The separate `physical_oracle` explicitly enumerates labeled card IDs in the chronological order **hand → Prize cards → first natural draw** for three independent 12-card toy cases. Its eleven event rates exactly equal the combinatorial solver. `results/absol_garbodor_darkasset_frontier/reproduce.py` also verifies Crobat's printed Dark Asset trigger, VIP's direct-to-Bench text, the complete 60-card source and conservative 2026-10-12 paper Expanded legality of all three variants. It compares the physically seen-Crobat metric with the independently written Stone model.

Run `python -m results.absol_garbodor_darkasset_frontier.reproduce` on Windows or in CI.

## Strategic interpretation

The same one Crobat can contribute a Basic setup option, a potential bench-entry draw engine, and a Forest Seal Stone VSTAR host. These roles are **coupled**. A setup hand where Crobat is forced Active may still use Star Alchemy but loses its normal Dark Asset trigger. A Battle VIP Pass line can create the V host directly but also misses the Dark Asset trigger. Paid search from deck to **hand** may be strategically useful even though it spends an Item, because it enables the Ability's trigger and can shrink the hand enough for positive draw.

A real deck optimizer must assign costs to the chosen Quick Ball, Ultra Ball, Energy discard, Pokémon Communication swap, free Bench slot, future prize liability, and whether Star Alchemy should be used before Garbotoxin. The simple existence of this union event is only evidence that the Crobat resource is widely actionable.

The next research layer should evaluate **what cards the resulting draw actually finds and retains**, preserving all physical zones and the alternative actions forgone. Agent15's [bench-draw synthesis](../bench_draw_support_synthesis/) supplies tested downstream hand-retention and Crobat/Dedenne sequencing models; adapting those results to this real 60 is preferable to counting draw volume as success.
