# Rotom Phone makes the Arc Phone/Peonia repack line more realistic

## Interaction and precise scope

Rotom Phone `swsh35-64` is an Expanded-legal Item whose printed rule instructs looking at the **top five cards**, choosing one, shuffling the other four into the deck, and putting the chosen card on top. Arc Phone `swsh11-152` can then exchange this known top card with a chosen Prize. Peonia `swsh6-149` subsequently retrieves that card from the now-known Prize slot.

This investigation extends [the raw opening-frequency model](../peonia_arc_opening_incidence/) to quantify the chance of naturally having these resources simultaneously. Unlike a one-card raw topdeck check, Rotom Phone allows the target to occur anywhere among five inspected deck cards. The relevant event may still be rare, and neither line is a win-rate estimate.

## Controlled 60-card opening experiment

Deck categories, all disjoint: twelve Basic starter Pokémon B, four Arc Phone A, two Peonia P, a single critical non-Basic target T, zero to four Rotom Phone R, and `41-R` disposable other cards F. These are abstract group counts rather than a finished decklist. A seven-card opening is accepted only if it contains B, then six random Prizes are set and one normal first-turn draw is made. The player goes second, so the Supporter may be played.

After the draw the hand must have at least one A, P and expendable F. Success occurs if T is the immediate next deck-top card, **or** if R is also in hand and T is among the second through fifth deck-top cards. In the latter event, Rotom puts T on top, Arc sends it to a known Prize position and Peonia recovers it. The first case is counted exactly once regardless of whether Rotom is held.

| Rotom Phone copies replacing F | Raw Arc+Peonia success after valid opener | Gain over zero Rotom |
| ---: | ---: | ---: |
| 0 | 0.160368% | baseline |
| 1 | 0.224254% | +0.063886 percentage points |
| 2 | 0.282873% | +0.122505 pp |
| 3 | 0.336539% | +0.176171 pp |
| 4 | **0.385550%** | **+0.225182 pp** |

At four Rotom copies the success-event incidence increases by a factor of approximately **2.4**, after accounting for the extra Item's inclusion in the same limited opening hand and the fact that Rotom replaces disposable F.

## Eight total top-five Items across two different names

The paper Expanded card pool also includes **Pokédex** `xy12-82`, an Expanded-legal Item that looks at the top five cards and puts them back in any order. For the immediate goal of placing a target `T` among those five onto deck top, Pokédex provides the same reachable top-card outcome as Rotom Phone. Their treatment of the other four cards differs, so this equivalence is restricted to the target-staging event.

A 60-card construction can include **four Rotom Phone and four Pokédex** because they have different names and each respects its four-copy limit. Replacing eight F with this combined top-five arranging family gives the exact raw opening incidence

`105799951/19578739752 = 0.540382%`

per accepted Basic opener, compared with `0.385550%` for four Rotom alone and `0.160368%` for zero top-five arrangers. This is a **3.37-fold increase** over the no-arranger benchmark under the same optimistic filler assumptions, while still a small absolute raw event rate. The general function `with_top_five(arrangers=8)` treats the two different card names as one action-equivalent class for this endpoint; the narrower `with_rotom(rotoms=4)` remains available.

## Exact probability calculation

The baseline contribution is the no-Rotom top-one event computed using the original grouped model, now treating Rotom as another protected/discrete class when considering F payment. The additional event requires one Rotom in hand as well as A, P, B and F, with target T absent from the eight cards seen before using Items. Group counts have multivariate-hypergeometric mass conditioned on the Basic being present in the **first seven**. The extra chance T occupies one of the next four deck positions beyond the immediate top is exactly `4/52`, conditional on the observed hand. Add this contribution to the baseline's `1/52` next-card event without double-counting.

Exact rational values for zero through four Rotom copies are asserted by `tools/rotom_arc_peonia_incidence.py`. Two independent, exhaustive **labeled physical-card oracles** enumerate accepted openings, Prize selection, compulsory draw, and every remaining deck ordering for ten- and eleven-card test populations, matching the analytic probabilities `7/150` and `305/8568`.

## Interpretation and limitations

The gain measures the *opportunity for this particular sequence*. It says little about whether adding Rotom is beneficial in an actual deck, because Rotom occupies slots that could improve mainline acceleration, disruption, or recovery. The all-F payment assumption is especially permissive: an apparent filler card can be UDP in a real match. Natural opener incidence omits ball search, other draws, mulligan bonus draws, Item lock, target alternative locations, and Peonia's Supporter contention.

An exact probability change from 0.160368% to 0.385550% in a toy deck should not be marketed as a 2.4x improvement in actual setup or win rate. It demonstrates a **source-conditioned complementarity** that a simple graph-counting model might miss: Rotom can stage a desired top-five card, Arc materializes it in a Prize slot with known identity, and Peonia transfers it to hand while preserving an independent action channel.

Source: bundled English card pool; reproduce: `python -m tools.rotom_arc_peonia_incidence` (GitHub Actions validation workflow).
