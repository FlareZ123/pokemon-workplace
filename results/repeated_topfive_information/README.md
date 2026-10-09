# Repeated Rotom probes: identical one-step connectors diverge across turns

## Research question

Rotom Phone and Pokédex both let the player put a desired card from the top five onto deck top, making them interchangeable for a **single** search-window event. What changes when the hand holds several copies and the player can sequence them before Arc Phone -> Peonia?

The critical difference is printed text:

- Rotom Phone `swsh35-64` chooses a top-five card and **shuffles the other four back into the deck** before placing the choice on top.
- Pokédex `xy12-82` puts the five inspected cards back in any order and performs **no shuffle**.

Both cards are paper Expanded legal. This result pins their exact print texts alongside Arc Phone and Peonia through code tests.

## Exact repeated-observation law

Condition on one unique target T uniformly located in a shuffled deck of `L >= 5` cards, with all other cards treated as strategically irrelevant for this event. The player holds `r` Rotom Phone and `d` Pokédex and can spend them before Arc Phone stages T as a known Prize for Peonia.

The first top-five inspection finds T with probability `5/L`. On a Rotom miss, choosing one known non-T card for the top and shuffling the other four into the tail makes T uniformly random in the other `L-1` locations. Each fresh subsequent look sees that chosen non-T top plus four cards randomly drawn from the other `L-1`. Therefore each additional inspection after a missed Rotom succeeds with conditional probability `4/(L-1)`.

For the pure T-acquisition objective, an optimal observation order uses Rotom Phones before a final Pokédex. The number of useful top-five inspections is:

- `q=0` when neither card is held;
- `q=1` when only Pokédex copies are held;
- `q=r` when r Rotom copies are held and no Pokédex;
- `q=r+1` when r Rotom and at least one Pokédex are held.

For `q>=1`, the conditional target-observation probability is exactly

`P_q = 1 - [(L-5)/L] * [(L-5)/(L-1)]^(q-1)`.

With q=0, Arc Phone alone sees the target only when it is top, probability `1/L`.

An independent exact physical-position transition oracle explicitly enumerates T's position after each shuffle, without evaluating this formula, and agrees over **75 combinations** of `L=5,6,7,12,46`, Rotom copies 0..4 and Pokédex copies 0..2.

## Exact 60-card raw opener incidence

The same opening model as [Rotom–Arc–Peonia incidence](../rotom_arc_peonia_incidence/) is used: twelve Basics, four Arc, two Peonia, singleton T, a variable set of Rotom/Pokédex, and all remaining cards expendable filler. Accept a seven-card opener with a Basic, set six random Prizes, make the normal turn draw, then require A, Peonia and expendable payment in hand. Target T may be in the Prizes, and contributes to this particular sequence only when it is in the shuffled 46-card live deck.

| Rotom | Pokédex | One-probe event | Repeated optimal probe event |
| ---: | ---: | ---: | ---: |
| 4 | 0 | 0.385550% | **0.412585%** |
| 0 | 4 | 0.385550% | **0.385550%** |
| 1 | 3 | 0.385550% | **0.398837%** |
| 2 | 2 | 0.385550% | **0.407924%** |
| 3 | 1 | 0.385550% | **0.412585%** |
| 4 | 4 | 0.540382% | **0.628041%** |

Multiple live Rotom copies have genuine sequential value that a one-step connector equivalence class misses. A single Pokédex in a hand with Rotom can add an inspection after the final Rotom reshuffle, but additional Pokédex without an intervening shuffle do not inspect further unknown cards.

## Validation, scope, and interpretation

The full physical opening/Prize/hand population is combined with the conditional exact observation law by rational multivariate-hypergeometric summation. Exact output values, the 75 independent physical-position oracle tests and card text legality assertions are in `tools/repeated_topfive_information.py`; dedicated GitHub Actions validates the result.

This remains a narrow, mostly optimistic **raw event probability**. The action policy is optimal only for finding the unique T among the live deck's top-five windows and assumes all held Rotom/Pokédex may be spent, no competing Item use, one spare Peonia replacement payment, no Item lock, and no external draws. It does not optimize prize-origin recovery by other means or the subsequent game. In particular, using a Rotom Phone may compromise the player's ability to exploit other topdeck-order information, and the true value of preserving one copy for later could exceed these immediate-access gains.

The earlier single-probe Rotom/Pokédex group model remains exactly valid for its more restrictive event; the new model identifies the extra probability supplied by **repeated physical execution capacity**.
