# Peonia -> Arc Phone positional policy

## Question

How much can preserved Prize-position information matter in a concrete two-Trainer line?

This result isolates one exact-composition state:

- six face-down Prize cards;
- exactly one singleton `TARGET`;
- five filler cards;
- the player knows the exact composition;
- the target's initial physical position is unknown.

Peonia samples one, two, or three physical Prize slots. If Peonia misses the target, known filler cards are placed back into the selected slots without shuffling the Prize cards. Arc Phone then chooses one physical face-down Prize card to exchange with the known top-deck card.

Implementation: `tools/peonia_arc_position.py`

Regression: `results/peonia_arc_position/reproduce.py`

## Card and rules evidence

The bundled Peonia print `swsh6-149` says:

`Put up to 3 Prize cards into your hand. Then, for each Prize card you put into your hand in this way, put a card from your hand face down as a Prize card.`

There is no Prize shuffle instruction in that text.

The bundled Arc Phone print `swsh11-152` lets the player switch the top card of their deck with one chosen face-down Prize card.

Advanced Player's Rulebook E-35 separately defines a face-down shuffle as randomization that removes order information. Peonia does not invoke that transition.

An official Pokémon Asia Indonesia Q&A for Peonia gives the stronger implementation detail: the hand cards returned as Prize cards do not need to be shuffled, and the player may place the selected hand cards in any desired order.

Official Q&A source:

https://asia.pokemon-card.com/id/rules/search/?keyword=N&pageNo=68

The English Pokémon Asia card pages also preserve the same Peonia and Arc Phone effect texts:

https://asia.pokemon-card.com/sg/card-search/detail/1564/

https://asia.pokemon-card.com/sg/card-search/detail/2749/

## Exact result

Let:

- `P` be the number of face-down Prize cards;
- `n` be the number Peonia chooses;
- one target be uniformly distributed among the `P` physical positions.

Peonia finds the target with probability:

`n / P`.

If Peonia misses and the replacements stay in those selected slots, the target is known to be among the `P - n` untouched positions.

Arc Phone can then choose any one untouched position, giving conditional probability:

`1 / (P - n)`.

The combined probability that the target is either taken by Peonia or selected by Arc Phone is:

`n/P + ((P-n)/P)(1/(P-n)) = (n+1)/P`.

For the ordinary six-Prize state:

| Peonia selections | Preserved positions | Shuffle-after-miss counterfactual | Position-information gain |
| ---: | ---: | ---: | ---: |
| 1 | 33.333333% | 30.555556% | 2.777778 pp |
| 2 | 50.000000% | 44.444444% | 5.555556 pp |
| 3 | 66.666667% | 58.333333% | 8.333333 pp |

With three Peonia selections, the exact preserved-position value is:

`2/3 = 66.666666667%`.

## Why the shuffle counterfactual is lower

Suppose a face-down Prize shuffle occurred after Peonia missed.

The target would again be uniformly distributed among all six positions.

Arc Phone's conditional target-slot probability would fall from:

`1/3`

to:

`1/6`.

The combined line would become:

`1/2 + (1/2)(1/6) = 7/12 = 58.333333333%`.

The 8.333333333-point difference is entirely positional information value. The exact composition remains one target plus five fillers in both versions.

## Independent validation

The reproducer validates each Peonia count in two independent ways.

First, it runs the `PrizePositionBelief` state transition model.

Second, it exhaustively labels the singleton target's initial physical position from 0 through 5.

For the preserved-position case, a fixed optimal Arc policy chooses one untouched position after a Peonia miss. Exactly `n + 1` of the six possible target locations then succeed.

For the shuffled counterfactual, the regression separately enumerates every post-shuffle target position for every Peonia-miss state.

Both calculations match the closed forms exactly for one, two, and three Peonia selections.

## Interpretation

The result provides a concrete policy-level consequence of the position-state counterexample.

A simulator that stores exact Prize composition and discards which physical positions Peonia replaced will undervalue the next Arc Phone decision in this isolated line.

The useful state is therefore richer than:

`TARGET is Prized`.

It includes which face-down positions have been ruled out or deliberately assigned known cards.

## Scope

The measured objective is whether the target is either:

- moved directly to hand by Peonia; or
- selected by Arc Phone and moved to the top of the deck.

Arc Phone does not itself draw the outgoing Prize card. A complete access policy must still model how and when the top card is drawn or otherwise accessed.

This result also assumes both Trainers are already available and usable. It does not model Supporter access, Item lock, Supporter contention, hand cost, deck-slot cost, or the strategic value of the replacement cards Peonia moves into the Prize zone.

## Next work

The most direct extension is to add a top-deck access deadline and compare the position-aware policy with alternative uses of the Supporter and Item channels.

A broader state-integration task is to combine:

- face-up versus face-down Prize eligibility;
- identity-to-position belief;
- observer-specific knowledge;
- exact physical Prize truth.

Those dimensions now have separate validated kernels in the repository.
