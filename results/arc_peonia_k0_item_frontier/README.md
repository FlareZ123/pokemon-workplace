# K0-like Arc Phone, Trekking Shoes, and Peonia target-access frontier

## Finding

A card's value depends strongly on whether a needed singleton is known to be Prized. When its location is instead uniformly uncertain between face-down Prizes and the hidden deck, **Trekking Shoes can be a better use of limited Item capacity** than Arc Phone, even though Arc Phone dominates some K1 positional rescue states.

This experiment gives an exact finite policy model for one valuable singleton T initially uniformly distributed across n face-down Prize positions and d hidden deck positions. All other hidden cards are inert filler F. One Peonia and enough expendable filler for its replacement payment are already available. The player can use a Arc Phone Items and s Trekking Shoes Items, with a and s each at most four, in any legal order.

At n=6, d=46 and a fixed four-Item budget:

| Arc Phone a | Trekking Shoes s | K0-like acquisition | Known-Prized K1 acquisition |
|---:|---:|---:|---:|
| 0 | 4 | 11/52 = 21.1538% | 3/6 = 50% |
| 1 | 3 | 10/52 = 19.2308% | 4/6 = 66.6667% |
| 2 | 2 | 9/52 = 17.3077% | 5/6 = 83.3333% |
| 3 | 1 | 8/52 = 15.3846% | 6/6 = 100% |
| 4 | 0 | 7/52 = 13.4615% | 6/6 = 100% |

The K1 column is proved and independently tested in [the Shoes-substitution result](../arc_peonia_shoes_tradeoff/); the K0 column is computed here. These are **conditional target-in-hand probabilities**, not tournament frequencies, turn-level feasibility, or win rates.

## Exact policy and position accounting

The repository card text anchors are Arc Phone \`swsh11-152\`, Trekking Shoes \`swsh10-156\`, and Peonia \`swsh6-149\`. Arc Phone observes the current deck top and can optionally exchange it with a face-down Prize. Trekking Shoes observes the top and can either put it into hand or discard it and draw the following card. Peonia chooses up to three Prize cards and returns as many hand cards facedown.

A full physical-world Bellman solver tracks a target's position among **every** Prize or deck slot. A Shoes take removes one deck position, while discard-and-draw removes two, correctly changing which card becomes top on the next action. Arc swaps physically move the singleton between a chosen Prize slot and deck top. The solver branches on the observation before selecting the optional action and can play Peonia at any point.

## Compact frontier formula and verified domain

Define C as the maximum number of equiprobable initial locations from which the singleton can be recovered. If a=0:

\`C = min(n,3)+min(d,2s)\`.

If a>=1:

\`C = min[n+d, 3+a+2s, min(n,a+2+1_{s>0}) + min(d,1+2s)]\`.

Then \`P(T acquired) = C/(n+d)\`.

The terms are physical ceilings on observation and acquisition:

- Peonia selects at most three positions.
- Every Arc Phone makes at most one top-card observation. Every Shoes makes at most two (look, followed by the optional discard-and-draw).
- An initially Prized T requires an Arc exchange to reach deck top; at most a previously hidden Prize positions can be probed outside Peonia's selected cards when Shoes is available. Without Shoes, a final unknown Prize swap cannot be identified except by another Arc.
- Deck positions can be advanced through at most two cards per Shoes. One additional deck-top observation can come from the Arc chain, without advancing the deck.
- There are only n+d original locations.

The formula agrees exactly with the adaptive physical-world oracle over **1,200 configurations** (n=1..6, d=1..8, a=0..4, s=0..4), plus **25 configurations** at n=6, d=46. This is an exhaustive finite-domain validation and an observation-based upper-bound derivation. It is not presented as an independently proven theorem for arbitrary unlimited n, d and Item counts.

## How the optimal plan shifts

When T is definitely Prized, spending Shoes after an Arc exchange can retrieve that exposed Prize from the deck top. Three Arc and one Shoes can account for all six Prize positions together with Peonia.

Under the 6-Prize/46-deck uniform prior, the target is far more likely to be in the deck. Four Shoes can reveal up to eight successive deck positions through their take-or-discard-and-draw choices, in addition to Peonia's three Prize positions. A chain of four Arc Phone instead covers all six Prizes and just the initial deck top. This produces the reversed four-Item ranking.

The model demonstrates a state-dependent **epistemic/physical resource allocation effect**. Knowing which zone contains T changes the optimal balance of Item roles. Actual decks face nonuniform target-location beliefs, different opportunity costs, card retrieval, Basic starter requirements, Supporter contention, discard costs, and opposing locks. Such constraints could reverse the relative choices again.

## Reproducibility

- Exact policy solver: \`tools/arc_peonia_k0_shoes.py\`.
- Run \`python tools/arc_peonia_k0_shoes.py\` for all 1,225 exact cases.
- The Windows GitHub Actions regression workflow also executes this model.

Next, optimize against nonuniform K0-to-K1 posterior probabilities and heterogeneous target values, and incorporate physical Item availability from accepted opening hands and Prizes.
