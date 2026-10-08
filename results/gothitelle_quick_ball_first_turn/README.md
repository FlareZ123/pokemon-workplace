# First-turn Quick Ball improves Gothitelle's turn-two setup window

## Question

How much can a single first-turn Quick Ball search improve the
unassisted [turn-two Gothitelle/Rare Candy readiness](../gothitelle_natural_setup_window/) model, once mandatory discard payment and random Prize cards are modeled?

This extends the previous exact timeline by permitting **one Quick Ball**
to find Gothita *on the first turn* when it was not already naturally
available. The player can then bench Gothita early enough for a second-turn
Rare Candy evolution.

- Exact engine: [`tools/gothitelle_quick_ball_first_turn.py`](../../tools/gothitelle_quick_ball_first_turn.py)
- Independent labeled test: [`reproduce.py`](reproduce.py)
- [Successful CI run 37774474875](https://github.com/FlareZ123/pokemon-workplace/actions/runs/37774474875)

## Rules and decision policy

Quick Ball `swsh1-179` is Expanded-legal in the local baseline.
Its text requires discarding one other hand card and searches the deck for
a Basic Pokémon.

The rule-respecting policy is:

1. Draw a legal seven-card opener, set six random Prizes, then draw the
   player's first-turn card.
2. If Gothita is in the observed first eight cards, put it into play.
3. Otherwise, if Quick Ball and at least one separately approved discard
   card are in hand and a Gothita remains unprized in the deck, pay the
   one-card cost, search Gothita, and put it into play.
4. On the second personal turn, draw one card naturally. If Gothitelle
   and Rare Candy are now in hand, evolve the previously established
   Gothita directly into Gothitelle.

The model tracks the first-turn Quick Ball search's effect on the
**physical deck size** before the second-turn draw. A Gothita already
randomly Prized cannot be searched. The card used to pay Quick Ball's
cost becomes unavailable for further actions.

There is no extra draw, another search action, additional Supporter,
opponent attack, Item lock, or Bench interference. The first-turn
Gothita is assumed to survive for evolution.

## Exact illustrative population

The hypothetical 60-card deck contains:

| Category | Copies |
| --- | ---: |
| Gothita | 3 |
| Gothitelle | 2 |
| Rare Candy | 4 |
| Other Basic Pokémon | 8 |
| Quick Ball | 4 |
| Approved other discard fodder | 12 |
| Other filler | 27 |

All listed categories are treated as disjoint. In particular, the model
does not automatically declare Gothitelle, Rare Candy, or Quick Ball
itself safe to discard.

## Results among legal opening hands

| Available approved discard cards | No Quick search | One first-turn Quick search allowed | Gain |
| ---: | ---: | ---: | ---: |
| 0 | 4.694346% | 4.694346% | 0.000000 pp |
| 4 | 4.694346% | 5.522035% | +0.827688 pp |
| **12** | **4.694346%** | **6.547707%** | **+1.853361 pp** |
| 20 | 4.694346% | 7.020503% | +2.326157 pp |

This exact result shows a substantial interaction between Basic search
access and realistic discard payment. Quick Ball's presence alone cannot
solve the missing Gothita if no acceptable card can pay its cost.

## Mathematical method

Opening seven-card category counts are evaluated using exact
multivariate hypergeometric combinations. The first-turn natural draw
is treated as uniform among the 53 cards not in the opener, after
marginalizing random Prize placement.

When Gothita is already observed, the second-turn draw is another
exchangeable draw from the remaining 52 unknown cards, reproducing
the natural-only baseline.

When a Quick Ball search is needed, the model conditions on the number
of Gothita that were randomly Prized. If at least one Gothita remains
in the deck, the search removes one physical Gothita and shuffles
before the turn-two natural draw. Conditional expected remaining
Gothitelle or Rare Candy counts are then divided by the correct
post-search deck size, accounting for their Prize dependence.

Every calculation uses exact integer combinations and
`fractions.Fraction`, with no Monte Carlo sampling.

### Prize-count distinction

For the no-search natural-draw baseline, changing the number of
randomly set-aside Prizes leaves the marginal opening/turn-two
probability unchanged, provided the same subsequent natural draws
remain possible.

The new Quick Ball branch genuinely depends on how many Gothita
are Prized, because a searched Pokémon must be in the **remaining
deck**. A richer small labeled example explicitly demonstrates that
changing the Prize count changes the search-enabled success
probability. An earlier tiny case happened to be numerically invariant
after two compensating effects; the regression was expanded rather
than assuming universal Prize dependence from a single example.

## Validation

The independent SFT enumerates complete labeled opening hands, random
Prize sets, first natural draws, optional Quick Ball searches, and
second natural draws for two small populations. It verifies exact
agreement with the category-count model, including the correct
removal of one Gothita before the final draw.

It checks that a richer case exhibits actual Prize sensitivity, and
tests monotonic gain as approved discard cards increase. The bundled
Quick Ball text and paper Expanded legality are verified.

GitHub Actions run `37774474875` passed.

## Strategic interpretation and limits

This model adds an actual early-game search policy to the previously
unassisted Stage 2 readiness estimate. It measures a narrowly
defined card-and-timing objective and cannot be treated as an optimized
deck setup rate.

A particularly important unmodeled opportunity is **discarding Sky
Field as Quick Ball's payment when searching Gothita**. If an opponent
later places Collapsed Stadium in play, that same early Quick Ball can
both establish Gothita and pre-position Sky Field in the discard pile
for Teleport Room after Rare Candy evolution. Modeling this dual-use
payment requires one joint two-turn state, with card identity and
discard timing conserved.

Other powerful search Items, Supporters, hand draws, first-turn Item
lock, opponent Knock Outs, and Bench pressure also remain outside
this exact model.
