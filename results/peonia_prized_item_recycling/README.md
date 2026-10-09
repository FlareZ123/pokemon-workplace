# Peonia recovery of Prized Item action capacity

## Research question

When the first deck search has established which cards are Prized but the physical Prize positions remain unknown, can otherwise inaccessible Item cards *inside* the Prize cards improve retrieval of a different critical Prized singleton?

**Yes, conditionally.** Peonia can retrieve Items which then fund another probe of the remaining unknown physical Prize positions. The position-specific exclusion information survives Peonia because the chosen replacement cards are placed in known positions and no shuffle is instructed.

## Source text and controlled model

The bundled English card database identifies:
- Peonia `swsh6-149`: put up to three Prize cards into hand; then put one hand card face down as a Prize for each card taken.
- Arc Phone `swsh11-152`: look at deck top, optionally switch it with one face-down Prize.
- Trekking Shoes `swsh10-156`: inspect deck top; take it or discard it and draw the next card.

The model uses exactly those distinct observation and material-transition phases. Only the one-target retrieval objective is scored. Prize positions are exchangeable at the start; the entire Prize *composition* is already known (K1). The rest of the unknown deck is an inert `F` group. Hand initially contains Peonia, one Arc Phone (`A`), one Trekking Shoes (`S`) and one expendable `F`. Peonia is unused. A target singleton `T` lies in the hidden Prizes. Five Prizes means an illustrative midgame snapshot; six Prizes is separately checked. The other card zones can be padded with inert cards to 60 physical cards, without changing the restricted model.

The exact Bellman model allows Peonia first or at any later time, selecting one to three physical Prize slots and deciding *after observing the selected cards* which hand cards to replace them with. It enumerates replacement assignment, optional Arc swaps, Shoes take/discard-and-draw, and Items retrieved through those effects. Every branch conditions on what the player actually observes. No player is given the hidden identity of an uninspected Prize slot.

## Reproducible exact results

With a 46-card inert deck tail, the returned values are exact rational probabilities:

| Prize cards (unordered, five slots) | Peonia first | Unrestricted timing |
| --- | ---: | ---: |
| T + four F | 4/5 = 80% | 4/5 |
| T + A + three F | 19/20 = 95% | 19/20 |
| T + A + S + two F | 1 = 100% | 1 |

Six-Prize cross-checks:

| Prize cards | Peonia first | Unrestricted timing |
| --- | ---: | ---: |
| T + five F | 2/3 = 66.666667% | 2/3 |
| T + A + four F | 23/30 = 76.666667% | 23/30 |
| T + A + S + three F | 19/24 = 79.166667% | 19/24 |

Replacing inert Prized cards with live Items improves the conditional target-retrieval probability despite leaving the initially accessible hand unchanged.

## Short independent explanation of the five-slot results

**No additional Prized Item.** Peonia initially checks three of five physical slots. It finds T with probability 3/5; if it misses, the one available Arc and Shoes can inspect and rescue T from one of the other two equally likely positions. Thus `3/5 + (2/5)(1/2) = 4/5`.

**One additional Prized Arc.** Failure now requires both T and A to occupy the two uninspected slots, which has probability 1/10. When this happens, the one held Arc can probe one of those two; it finds T with probability 1/2. If Peonia recovers A, the second Arc can probe the other slot. Failure probability is `(1/10)(1/2) = 1/20`, giving `19/20`.

**One Prized Arc and one Prized Shoes.** If Peonia misses T, its two uninspected slots must contain T and one of A, S or F. If an Item is among those two, the initially held Arc can exchange that Item onto deck top; a Shoes draw recovers it, giving the needed additional action. If the other card is F, Peonia has already recovered both A and S, allowing two Arc probes. Accordingly every hidden allocation admits a successful adaptive line, giving 100%.

## Disposable-hand-card threshold

The recovery benefit is conditional on Peonia being able to preserve the Item package after replacing the taken Prize cards. Removing the **one expendable filler card** from the initial hand (now Peonia, A1, S1 only) changes the five-Prize optima:

| Prize cards | No spare filler | One spare filler |
| --- | ---: | ---: |
| T + four F | 4/5 = 80% | 4/5 = 80% |
| T + A + three F | 4/5 = 80% | 19/20 = 95% |
| T + A + S + two F | 4/5 = 80% | 1 = 100% |

The extra copy in the Prizes is valuable only if the hand has enough replaceable cards to keep it **along with** the held Arc/Shoes needed to exploit it. When Peonia selects an Arc and two fillers, having one spare filler permits returning three filler cards to the Prizes, retaining two Arc and one Shoes; without the spare filler, at least one useful card must be returned. Thus the 15- and 20-percentage-point gains vanish when the spare payment resource is removed. This is a concrete complementarity between state-dependent discardability and recovered Item action capacity. The exact optimizer also considers selecting fewer than three Prizes and trading other cards back, so the zero-filler results are optimized rather than a restricted forced-payment policy.

## Evidence and limits

Implementation: `tools/peonia_timing_policy.py`; exact Fraction reproduction and analytic event checks: `results/peonia_prized_item_recycling/reproduce.py`. The code also checks that Peonia is playable with an empty deck, exposing a previously detected early-termination bug.

The unrestricted-timing solver equals Peonia-first on **these six fixtures**; this is not a general Peonia-first dominance theorem. These are idealized conditional access probabilities, not estimates of deck quality, matchup success, win rate, or standard opening consistency. The model does not include opponent effects, Stadium and Supporter competition, conventional deck search, or strategic value of the other cards returned as Prize payments. The `F` group abstracts distinct inert physical cards; it is not a claim that 46 identical non-Energy cards form a legal 60-card deck.

## Future work

Test asymmetric Prize target values and finite hand-payment constraints, then connect this exact posterior to the existing compressed exchangeable-deck-tail solver. The main research question is when Peonia should be withheld until after one or more Arc or Shoes actions have moved valuable Items between the deck and Prizes; equality in this restricted sweep is only preliminary evidence.
