# Natural opening incidence of Arc Phone -> Peonia deck-top repacking

## Question

A legally executable Arc Phone -> Peonia line can retrieve a known deck-top target without Trekking Shoes. How frequently does the required **raw hand and topdeck conjunction** arise in a simple 60-card composition, after a valid Basic Pokémon opening and the compulsory first-turn draw?

## Model and exact calculation

A 60-card paper Expanded deck contains these disjoint categories: one critical non-Basic singleton T, four Arc Phone A, two Peonia P, twelve Basic opening Pokémon B, and the remaining 41 cards F. At first every F is assumed a valid, strategically expendable replacement payment for Peonia. This optimistic F assumption is relaxed below. The active starter B is removed from the seven-card starting hand, leaving any F hand card available as a payment. All other gameplay effects are deliberately inactive; the player goes second so that using Peonia on the first turn is permitted.

A starting seven is accepted exactly when it contains at least one B. Six Prize cards are set randomly from the remaining deck, then the player takes the normal one-card turn draw. The rare event is:

1. The accepted opener plus normal draw contains at least one Arc Phone, at least one Peonia, and at least one expendable F.
2. The critical T is the next card on top of the deck, after the normal turn draw, rather than already in hand or among the six Prizes.

Then Arc can observe T, swap it into a known face-down Prize position and Peonia can retrieve it, paying an F to preserve T. This is a precise *raw incidence* estimate for this short line. It neither models draws/search that find A/P nor credits other win conditions.

### Exact method

Let H=7, N=60, and let (b,a,p,f,o) be counts of the five non-T categories in the H+1 cards seen by the end of the normal turn draw, including protected-other O when some F cards are reclassified as undiscardable. The event requires b,a,p,f>=1 and no T in those H+1 cards.

Each group-count vector has mass

`C(B,b)C(A,a)C(P,p)C(F,f)C(O,o) / C(N,H+1)`.

Because the first H cards, rather than just the first H+1, must contain a Basic, multiply that mass by H/(H+1) when b=1, otherwise by one. Sum over valid group counts, divide by `1-C(N-B,H)/C(N,H)` for the probability of a valid Basic opener, and divide by `N-H-1=52` for the probability that the remaining unique T occupies the exact **next** deck-top position. The 6-Prize placement is marginalized by symmetry; it does not alter the uniform target-location law for a particular remaining deck position.

The complete computation uses exact Python `Fraction`, with four independent labeled-card microdecks enumerating the actual opening subset, normal turn draw, and next-top location.

## Results

| Peonia-disposable F among 41 remaining cards | P(raw Arc-Peonia repack event \| valid Basic opener) |
| ---: | ---: |
| 1 | 0.015992% |
| 2 | 0.030677% |
| 4 | 0.056451% |
| 8 | 0.095698% |
| 12 | 0.122029% |
| 16 | 0.138948% |
| 24 | 0.155127% |
| 32 | 0.159614% |
| 41 | **0.160368%** |

The all-disposable scenario's probability is exactly `345378629/215366137272`. It consists of a conditional **8.3391423%** chance to have the necessary A/P/F access after the opening and normal draw, times **1/52** for T in the precise next deck-top position. The conditional chance that the *first seven cards* contain at least one Basic is `394669/487635 = 80.935331%`.

This makes the 14.2857-percentage-point counterexample from [Peonia deck-top repacking](../peonia_repackaged_top/) a **conditional tactical statement** with a small natural opening incidence under this restrictive raw-draw model. It remains potentially strategically useful in states where other effects arrange T on deck top, increase access to A/P, or reward the line in a decisive terminal state. Modeling those effects is further work.

## Validation and limitations

Reproduce: `tools/peonia_arc_opening_incidence.py`, executed by `python -m tools.peonia_arc_opening_incidence`. GitHub Actions workflow: `validate-peonia-arc-opening-incidence.yml`.

The 60-card categories are an *abstract legal-sized partition*, not a fully instantiated legal decklist: the 12 Basics must be distributed among legal prints and the protected/disposable categories must be implementable with legal cards. F as a safe Peonia payment is a generous assumption. The model omits opponent information, mulligan bonus cards, conventional search/draw, extra turn effects, taking Prizes, locks, and Supporter opportunity cost. It measures a narrow event, **not win rate**, not Peonia deck-inclusion value, and not the full probability of acquiring T through all possible routes. Also, the rare event may be unnecessary if T is already in hand or reachable through other means.

Follow-up: integrate a realistic source pool where searching A/P and reordering the deck top competes with the Peonia Supporter window, or evaluate the exact terminal resource value rather than mere access.
