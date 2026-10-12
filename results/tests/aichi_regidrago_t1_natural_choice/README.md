# Aichi Regidrago: opening-time opportunity to choose Grass or Fire

**Evidence class:** exact finite-deck probability conditional on accepting a valid opening seven, cross-checked by 945 independently enumerated physically distinct miniature deck and next-draw cases.

## Why this matters

The published [2026 Aichi tenth-place Regidrago VSTAR 60](https://limitlesstcg.com/decks/list/26816) contains four Regidrago V, four Double Dragon Energy, four Grass Energy, and two Fire Energy. Its 20 Pokémon comprise **15 Basic Pokémon**, including four Regidrago V. If a Regidrago V is available and the hand contains Double Dragon Energy plus **both Basic Grass and Basic Fire**, there is a physically available choice of which Basic to attach before a later Apex Dragon / copied Kyurem Trifrost line.

The related [Crispin stock study](../aichi_regidrago_crispin_post_trifrost/) quantified the future deck-supply benefit of preserving the scarcer Fire copy in one conditioned continuation. This test measures a small source-limited *opportunity frequency* in natural opening cards, without assuming the main attack can legally launch.

## Exact setup and numbers

Take a uniformly shuffled 60-card published list. Require at least one Basic in the **seven opening cards**, as required for a valid opener. Put six Prizes face down. Observe one natural draw on the first turn. Because the six random Prizes are marginalized rather than inspected, the eighth exposed card is uniform among the 53 cards initially outside the opening seven. We enumerate physical eight-card multisets with the number of placements for the final draw that leave a Basic in the first seven.

| Event among first eight observed cards | Exact probability conditional on legal seven | Percentage |
| --- | --- | ---: |
| Regidrago V, DDE and **at least one** of Grass/Fire | `470817817/4515961725` | **10.425638%** |
| Regidrago V, DDE and Grass | `2085436/27369465` | **7.619%** |
| Regidrago V, DDE and Fire | `7551937/180638469` | **4.181%** |
| Regidrago V, DDE, Grass **and** Fire together | `20692516/1505320575` | **1.374625%** |
| Both Basic types among qualifying Regidrago + DDE + at-least-one-Basic natural hands | `62077548/470817817` | **13.185046%** |

The accepted-opening probability before conditioning is `172135/195054` (88.2499205%). The shared-physical-card inclusion/exclusion identity is checked exactly: P(either) = P(Grass) + P(Fire) - P(both).

A small eight-card natural view is an **extremely restrictive channel** for this deck: it omits Dedenne-GX, Squawkabilly ex, Professor's Research, Quick Ball, Mysterious Treasure, and every other search/draw action. Those cards can vastly change realistic selection opportunities. Neither seeing Regidrago V nor holding the Energy guarantees Regidrago VSTAR, appropriate timing, an attack, an opposing target, or use of Trifrost.

## Reproduce

Source: `tools/aichi_regidrago_t1_natural_choice.py`.

Independent direct oracle: [reproduce.py](reproduce.py). Across 945 miniature physical deck configurations, it enumerates every valid first-seven physical card subset and every possible eighth card, separately from the weighted hypergeometric calculation. Use `python -m results.tests.aichi_regidrago_t1_natural_choice.reproduce`.

**Interpretation:** The choice discussed in the Crispin study is tactically meaningful in its conditioned state. It occurs in only **1.374625% of valid natural first-eight exposures** when all four named physical resources must already be visible. That figure is a *strict natural-source subset*, with no quantified upper bound on game-wide frequency, and no demonstrated effect on wins.
