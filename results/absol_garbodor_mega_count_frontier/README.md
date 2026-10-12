# 2026 Aichi Mega Absol ex count: exact initial-access frontier

## Research question

What does a third Mega Absol ex change in Yusuke Kobayashi's [2026 Aichi eighth-place Mega Absol/Garbodor](../competitive_deck_baselines/#2026-aichi-open-league-8th-place-mega-absol-ex--garbodor) list, before accounting for Items, energy, abilities, or the opponent?

The tournament list contains **two Mega Absol ex** among ten Basic Pokémon, and 60 cards total. Its complete [exact-print source manifest](../competitive_deck_baselines/absol_garbodor_kobayashi_2026.json) is retained unchanged. This analysis evaluates two different one-card replacements in complete, conservatively eligible 60-card snapshot decklists.

## Exact results

Condition on a **valid seven-card opener**, defined as containing at least one Basic Pokémon. Six Prizes are subsequently drawn from the remaining 53 cards without inspection, and the first natural draw occurs from the remaining 47. Each random physical-card ordering is equally likely.

| Fully specified deck configuration | Basic Pokémon | Valid opening | Mega Absol held in seven given valid | Mega Absol held by first draw given valid | Every Mega Absol in initial Prizes given valid |
| --- | ---: | ---: | ---: | ---: | ---: |
| **Published**: 2 Mega Absol ex | 10 | 74.137076570% | 29.872897179% | 32.519202946% | 0.763357433% |
| **+1 Mega Absol / −1 Temple of Sinnoh** (`swsh10-155`) | 11 | 77.757885850% | 40.565605649% | 43.929816650% | 0.050742247% |
| **+1 Mega Absol / −1 Crobat V** (`swsh3-104`) | 10 | 74.137076570% | 42.546804911% | 45.798872557% | 0.049050794% |

All versions use `me1-86` Mega Absol ex. The published list has two Temple of Sinnoh, so the non-Basic substitution retains one. The second alternative removes its singleton Crobat V. Both counterfactuals satisfy source-aware four-copy and single-ACE-SPEC restrictions and are adjudicated as `eligible_snapshot` as of 2026-10-12.

The Crobat cut has a higher conditional initial Mega access than the Temple cut because it preserves the original total of ten Basics, making Mega Absol a larger share of Basic-valid openings. The Temple cut simultaneously raises the chance of a valid seven-card opener. This is a **conditioning effect** that can invert naive slot comparisons.

The raw initial all-Prized event does not mean Mega Absol is irrecoverable, since the deck contains Hisuian Heavy Ball and potentially relevant other recovery routes. The difference among rows is real as a physical placement probability, but it does not establish practical prize rescue timing.

## Exact method and independent oracle

Let `N = 60`, `h = 7`, `p = 6`, `b` be the count of Basic Pokémon and `m` the count of Mega Absol ex, all of which are Basic. There are `C(N,h) − C(N−b,h)` accepted seven-card hands. The probability of directly holding a Mega Absol in that hand is:

`[C(N,h) − C(N−m,h)] / [C(N,h) − C(N−b,h)]`

Given no Mega in a valid opening hand, the probability that the first natural draw is a Mega is `m/(N−h)`. For the initially all-Prized event, multiply the conditional probability of a valid opening with no Mega by `C(N−h−m,p−m)/C(N−h,p)`. This conditional probability uses a full physical six-card Prize packet.

Reproduce with:

`python -m results.absol_garbodor_mega_count_frontier.reproduce`

The script uses integer combinatorics and `fractions.Fraction`, crosschecks independently against exhaustive **labeled physical hands, Prize subsets, and subsequent draw cards** in three miniature deck configurations, reads the true 2026 Aichi 60-card source manifest, then applies the current repository deck-construction and print-legality adjudicator to each whole candidate list.

## Interpretation and limits

These are **first-exposure events**, not first-turn benching, attacking, damage output, or match wins. The model omits Quick Ball, Ultra Ball, Battle VIP Pass, Boost Shake, draw Supporters, costs and discard choices, the timing of Garbotoxin, Dark Patch acceleration, Energy requirements, mulligans and optional opponent extra draws. Crobat V's draw Ability and Temple of Sinnoh's disruption have high conditional and matchup value that the direct-hand metric cannot quantify. An actual optimization must evaluate those losses and the competing search paths before choosing the third Mega.

**Provenance:** the original 60-card list is transcribed from the [May 10, 2026 Aichi top-eight decklist publication](https://limitlesstcg.com/tournaments/566/decklists). Print IDs and legality use the repository's supplied card archive and adjudicator. The probabilities are mathematical derivations, validated by the script's independent labeled toy enumeration.
