# Aichi 2026 Regidrago: conditioned Grass/Fire stock, with causal caveat

**Evidence:** Exact conditional combinatorics over a published 60-card deck, with a 2,424-case independent physical-card oracle. The two columns compare **different information states**. They cannot be interpreted as two actions available in one identical hand.

## Source state and printed action

The published tenth-place Aichi Regidrago deck contains four Double Dragon Energy, four Basic Grass, two Basic Fire, one Kyurem, and one Crispin. Regidrago VSTAR's Apex Dragon costs Grass/Grass/Fire; DDE and either one Basic Grass or Fire meets the cost. Copied Kyurem's Trifrost discards all attached Energy. Crispin searches up to two differently typed Basic Energy cards from deck and can attach one of them if two are found.

**The calculation's conditions differ:** in one scenario, one DDE and one Grass have become known outside the unknown pool, leaving 3 Grass/2 Fire among 58 cards; in another, one DDE and one Fire have become known outside, leaving 4 Grass/1 Fire among 58. Six Prize cards and an optional specified number of other cards outside the searchable deck are uniformly sampled from those remaining 58. The player is *not* assumed to be holding both Grass and Fire and choosing between them.

## Exact conditional probability of both types remaining in deck

| Additional unknown cards outside deck, beyond six Prizes | Known Grass outside | Known Fire outside | Composition-conditioned gap |
| ---: | ---: | ---: | ---: |
| 0 | 99.0279% | 89.6518% | 9.3761 pp |
| 3 | 97.5527% | 84.4558% | 13.0968 pp |
| 7 | 94.3825% | 77.4458% | 16.9367 pp |
| 10 | 91.0209% | 72.0801% | 18.9408 pp |
| 15 | 83.4296% | 62.8265% | 20.6030 pp |

Exact Prizes-only probabilities are `13039/13167` and `342329/381843`. With 13 unknown cards outside deck, the exact values are `10921/11571` and `35845/46284`. The first conditional population has at least as much dual-type supply as the second for all 59 possible unknown exclusion counts, with 56 strictly different.

For `N=58`, `g` unknown Grass, `f` unknown Fire, and `m` random outside cards, the calculation is exact inclusion-exclusion:

`P(both types in deck) = 1 - C(N-g,m-g)/C(N,m) - C(N-f,m-f)/C(N,m) + C(N-g-f,m-g-f)/C(N,m)`,

with impossible binomial choices interpreted as zero.

## Matched causal comparison changes the interpretation

**When both Basic Grass and Basic Fire are already available in the same player's hand, both are already absent from the deck.** Attaching Grass or Fire and later discarding it with Trifrost leaves the deck and Prize identities unchanged. Thus the impact of that hand-matched choice on Crispin's *immediate two-type deck stock* is **exactly zero**. The player's remaining hand and discard pile do differ. Subsequent Super Rod, retrieval, manual attachments and other plays can therefore give the choices different continuation values.

The [paired causal test](../aichi_regidrago_crispin_paired_causal/) explicitly checks this invariant and finds the same **84.716276%** dual-type deck-stock probability for either choice, conditional on a naturally observed first-eight hand containing Regidrago V, DDE, Grass and Fire. This corrects an earlier claim that choosing Grass in a shared hand increased deck stock by the composition-conditioned gap above.

These tables describe distinct state-conditioned risks, which can matter when only one Basic type was originally available. They are **not action-selection advantages**, observed in-game state frequencies, or match win-rate changes. They neither price the discarded resource nor include other possible Crispin routes.

## Reproduction

Run `python -m results.tests.aichi_regidrago_crispin_post_trifrost.reproduce` from the repository root. It uses `tools/aichi_regidrago_crispin_energy_supply.py`, the source list at `results/regidrago_aichi_top10_playable/yoshioka_regidrago_2026.json`, and the exact printed card texts. An independent physical-card subset enumerator validates 2,424 miniature configurations. Windows CI exercises this and the paired comparison.

Tournament source: https://limitlesstcg.com/decks/list/26816 .
