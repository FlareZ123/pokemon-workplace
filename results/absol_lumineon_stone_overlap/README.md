# Forest Seal Stone compresses the Lumineon V Supporter-search advantage

## Question and exact-print source

The source-validated [2026 Aichi eighth-place Mega Absol ex/Garbodor list](../competitive_deck_baselines/absol_garbodor_kobayashi_2026.json) contains **Tapu Lele-GX Wonder Tag, Crobat V Dark Asset, and Forest Seal Stone Star Alchemy**. A preceding [Lumineon V Supporter-search study](../absol_lumineon_supporter_frontier/) found that changing Crobat V into Lumineon V raises a restricted first-turn chance of reaching singleton **Crispin**, once Tapu Lele's duplicate search function is accounted for.

Forest Seal Stone complicates the comparison: **both Crobat V and Lumineon V host Star Alchemy**. Even the Crobat configuration may search directly for Crispin if its Tool line is available. To quantify the overlap, this new solver includes the shared one-Pokémon-V Tool pathway in the same physical hand/Prize worlds.

All three 60s are validated conservatively for paper Expanded on October 12, 2026:
- Original published 2 Mega Absol / 2 Temple / 1 Crobat V.
- +1 Mega / −1 Temple, retaining Crobat V.
- +1 Mega / −1 Temple, replacing Crobat V with Lumineon V `swsh9-40`.

Each list also retains Tapu Lele-GX `sm2-60`, singleton Crispin `sv7-133`, Adventure Bag `sm8-167`, Forest Seal Stone `swsh12-156` and exact named search Items.

## Exact probability of obtaining Crispin by the first natural draw plus one restricted source

All probabilities condition on a **valid seven-card Basic opening**, six actual Prize cards and the first natural draw. An Action using a paid source must be realistically possible under the specified Energy-only discard policy. The endpoint is Crispin *in hand*, not its play or any match outcome.

| Restricted event | Published Crobat | +Mega / −Temple Crobat | +Mega / −Temple Lumineon |
| --- | ---: | ---: | ---: |
| Target via direct possession / Wonder Tag / Luminous Sign / one paid Item | 42.661639% | 43.400979% | 52.536630% |
| Held V host + held Stone or held Bag into unprized Stone | 2.901574% | 2.781709% | 2.781709% |
| Prized V host + Heavy Ball + already held Stone | 0.109758% | 0.111882% | 0.111882% |
| In-deck V host + paid Quick / Ultra / Communication + held Stone | 2.064930% | 2.137781% | 2.137781% |
| Union of all Stone routes (with internal overlap removed) | 5.076262% | 5.031372% | 5.031372% |
| **Union: named routes or Stone** | **45.014080%** | **45.656523%** | **53.160233%** |

The printed source line is important: **Adventure Bag is an Item**, so its use to obtain Stone can occupy the entire allowed one-Item source for this study. A second search Item would require a two-Item chain excluded from the stated objective. If Stone itself is already held, one paid Quick/Ultra/Communication can instead fetch a live in-deck Pokémon V host. Hisuian Heavy Ball likewise can retrieve a Prized V host for the held Stone line.

The raw named-route Lumineon advantage over the third-Mega Crobat list is **9.135651 percentage points**. After making Star Alchemy access available to both V hosts and removing shared success overlap, the incremental advantage contracts to **7.503710 points**. This is a **1.631941-point reduction** in the claimed narrow material-access gain from counting the Stone overlap properly. The Forest Seal Stone *standalone* route has the same **5.031372%** probability in the two third-Mega variants because all its relevant physical counts remain the same.

## Exact implementation and independent verification

`tools/mega_absol_lumineon_stone_overlap.py` extends the earlier 12-category solver with distinct `stone` and `bag` categories, enumerating the physical Basic-valid seven-hand state, first drawn card, and **joint Prize multiplicities of Crispin, Tapu Lele-GX, the V host, and Forest Seal Stone**. Each integer combinatorial mass is integrated in a normalized exact `Fraction`. A linked check recovers the previous Supporter-only result when Stone routes are stripped away.

`results/absol_lumineon_stone_overlap/reproduce.py` separately enumerates every **individually labeled physical card** across opening hands, Prize packets and next draws in three 12-card toy decks, under two policies (Crobat and Lumineon), independently of the weighted combinatorial solver. All six toy oracles compare all six event ratios exactly. The test also revalidates all three full 60s with the paper Expanded snapshot deck proof.

Reproduce on Windows: `python -m results.absol_lumineon_stone_overlap.reproduce`.

## Limits and strategic implications

The probabilities reflect **one immediately playable named Item source** plus an optional Tool attachment and the printed hand-entry Ability or VSTAR Power. More involved Item lines, ordinary Supporter use, Crobat's Dark Asset draws, multiple Pokémon power targets, Bench-slot contention, Garbotoxin suppressing Abilities, opponent Item/Tool locks, natural late-game draws, actual Energy opportunity costs, and matchup-specific usefulness of Crispin remain outside this model.

The result demonstrates an access-model version of **connector domination**: when a broad universal search line already exists, adding a targeted overlapping search Ability yields less marginal improvement than its standalone access suggests. It is not proof that Lumineon V is competitively preferable. Crobat's Dark Asset can find a variety of non-Supporter resources, and the published tournament deck is still the empirical baseline.

The next useful analysis is a deadline-sensitive multi-target continuation that values actual cards found, competing use of the unique VSTAR Power, bench occupation and self-imposed Garbotoxin timing before declaring a slot swap favorable.
