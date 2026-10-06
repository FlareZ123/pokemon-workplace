# Prize belief states before the first full deck search

## Question

Does K0 mean the player has no useful information about their Prize cards?

K0 remains uncertain, while visible cards already constrain the Prize distribution. A stronger state representation keeps an exact posterior over possible Prize configurations until a full deck search collapses that uncertainty to K1.

Implementation: `tools/prize_belief.py`

Reproducer: `results/prize_belief_states/reproduce.py`

## Rules and state basis

The ordinary setup sequence draws the opening hand before the six Prize cards are set. Those opening cards are therefore known to be outside the initial Prizes.

Later ordinary draws also reveal cards that are outside the remaining face-down Prizes.

Before a full deck search, the player may still be uncertain about which unseen cards are Prized. Under a randomized deck and with no additional deck-order information, conditioning on visible non-Prize cards leaves the Prize set uniformly distributed among the remaining unseen card identities.

The K0/K1 abstraction in `resources/human_concepts.md` is useful as a coarse distinction. This result refines K0 into a belief state.

## Exact posterior

Let:

- `N` be deck size;
- `P` be the number of face-down Prize cards still modeled;
- `V` be the number of visible cards known to be outside those Prize cards;
- `U = N - V` be the remaining unseen population;
- `g` be the total number of copies in a card group;
- `v` be the number of those group copies already visible outside the Prizes;
- `R = g - v` be the remaining unseen copies from that group.

Then the number `X` of group copies in the Prizes has the hypergeometric posterior:

`P(X=x) = C(R,x) C(U-R,P-x) / C(U,P)`

This is an exact conditional distribution under the stated information assumptions.

## Finding 1: an unseen singleton becomes slightly more likely to be Prized after non-target draws

For an unseen singleton, `R = 1`, so:

`P(singleton Prized) = P / U`

In a 60-card game with 6 Prizes:

| Observation state | Visible known non-Prize cards | Singleton Prize posterior |
| --- | ---: | ---: |
| Accepted opening only | 7 | 11.320754717% |
| 1 additional non-target draw | 8 | 11.538461538% |
| 5 additional non-target draws | 12 | 12.500000000% |
| 10 additional non-target draws | 17 | 13.953488372% |

Each additional observed card that is not the singleton removes one possible non-Prize location from the unseen population.

The singleton can still be in the remaining deck or in the Prizes. As the unseen population shrinks while the six Prize slots remain, the Prize posterior rises.

## Finding 2: seeing the singleton collapses its Prize probability immediately

If the singleton itself becomes visible in the opening hand, through an ordinary draw, or in another zone known to be outside the face-down Prizes, then its Prize probability is exactly zero.

This is partial information acquired before K1.

A binary state flag such as `has_searched_deck = false` therefore does not fully describe Prize knowledge. Two pre-search states can have very different beliefs because different cards have already been observed.

## Finding 3: multi-copy line failure also drifts as misses accumulate

Consider a two-copy resource group where a line needs at least one copy to be unprized.

If neither copy has been seen after the accepted opening, the exact probability that both are Prized is:

`1.088534107%`

After five additional non-target draws, with both copies still unseen, that probability becomes:

`1.329787234%`

The line has not mechanically failed at K0. Its Prize-risk posterior has increased.

This matters for risk-sensitive sequencing. A player may rationally become more willing to choose an alternative line as repeated non-target observations make a critical unseen package more likely to be trapped in the Prizes.

## Stronger representation

A useful game-state model can separate three layers of knowledge:

1. visible facts, including cards known to be outside the Prizes;
2. a posterior distribution over unseen Prize configurations;
3. exact K1 Prize knowledge after a full deck search.

The first two layers exist before K1.

For many calculations, the posterior can be represented compactly through the current unseen population and group counts instead of enumerating every physical deck order.

## Relationship to initial-opening conditioning

Earlier repository work shows that mulligan and optional-starter policy can change the Prize prior before the exact accepted hand is observed.

Once the player knows the actual accepted opening hand, those seven specific cards are known non-Prize cards. Under a fully randomized remaining order, the initial Prize set is then uniformly distributed among the other 53 card identities.

Subsequent ordinary draws provide additional non-Prize observations and update the posterior again.

This creates a natural sequence:

`setup policy prior -> exact accepted hand posterior -> draw-by-draw posterior -> K1 exact Prize state`

A simulator can preserve each transition instead of jumping directly from an unconditional deck prior to K1.

## Strategic consequence

The first full deck search has two information effects.

First, it reveals the exact Prize configuration and removes the residual posterior uncertainty.

Second, its value depends on what the player already knows.

If a key singleton is already visible, a search provides no new Prize-status information about that card. If several critical cards remain unseen after many non-target draws, the search can resolve a more strategically important uncertainty.

This suggests that the value of reaching K1 is state-dependent.

## Validation

The reproducer checks the singleton posterior against the closed form `P/U` at several visible-card counts.

It also checks the two-copy all-Prized probability against direct hypergeometric formulas.

An independent small-state validation enumerates every two-card Prize subset from a seven-card unseen population and compares the labeled enumeration with the grouped posterior from `group_prize_distribution()`.

The distributions match to floating-point precision.

## Limitations

The posterior assumes no additional information about the order or contents of the unseen deck.

Effects that inspect or rearrange the top of the deck can create extra information that this simple state does not encode.

Cards already taken from the Prizes require explicit origin tracking. They should not be counted as ordinary visible non-Prize observations for reconstructing the original Prize partition.

Searches, revealed deck cards, known top-deck cards, recovery effects, and opponent-induced deck manipulation can also require a richer belief state.

The model describes Prize uncertainty. It does not determine whether an unprized card is reachable in time, affordable to search, or strategically usable.

## Next useful work

The next extension should combine the belief state with line choice.

Instead of comparing one generic K0 policy with K1, the optimizer should recompute expected line value after each new observation:

`belief update -> evaluate candidate lines -> act -> observe -> update again`

That would quantify when accumulated pre-search evidence is strong enough to change the preferred line before exact K1 information is available.
