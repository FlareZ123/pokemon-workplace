# Physical two-Pokémon acquisition through multiple paid search Items

This study composes three requirements that are easy to miss when
estimating initial engine consistency: each search Item has one output,
its discard payment must be available, and the desired Pokémon may
be Prized.

## Physical setup

An abstract 60-card deck contains:

- twelve ordinary Basic starter cards;
- one non-starting target Pokémon A and one non-starting target Pokémon B;
- S physically distinct, one-use Item search sources;
- D designated safely disposable hand cards;
- neutral filler for the remaining slots.

The two target Pokémon are distinct singletons. Each Item source
functions like an abstract Ultra Ball: discard two other safe cards
from the hand, then search the deck for one of the missing Pokémon.
Multiple Item copies can be played during the same turn, provided
every payment can be made. Only the designated D-class cards are
allowed as discard payment for this lower-bound-safe strategy.

An accepted opening has seven cards and an ordinary Basic. Six cards
are randomly Prized. The model optionally adds m bonus cards
following opponent mulligans. The objective is to hold *both*
target Pokémon after executing the available search Items, all within
one usable Item window.

## Exact conditions

Given the combined observed opening and bonus hand, let

    t = 2 - count(A in hand) - count(B in hand)

be the number of missing targets. Access requires at least t physical
search Items and 2t safely disposable hand cards. Every missing target
must also remain in the deck rather than in Prizes.

For M unseen cards of which P are Prize cards, and t known distinct
missing singleton targets, the chance they are *all* searchable is

    C(M-t,P) / C(M,P).

The observation-class distribution is conditioned exactly on at least
one ordinary Basic in the opening. The probability engine sums over
the multivariate-hypergeometric observed counts, weighted by the
legal opening factor, and applies the target-Prize survival factor.
This is an analytic exact state enumeration.

## Controlled 60-card ablation

With S=3 search copies, D=12 safely disposable cards and eight
opponent bonus draws:

| Model constraints | Probability of both target Pokémon available |
| --- | ---: |
| Physical source count only, ignoring payments and Prizes | 35.43273449% |
| Also require two safe discards for each search | 25.29033647% |
| Also require missing targets to be unprized, with payments ignored | 30.42436144% |
| Both discard payments and actual Prize availability | 22.39363458% |

Taking the fully optimistic value as baseline, payment restrictions
remove 10.14239802 percentage points, and Prize restrictions alone
remove 5.00837305 points. Their combined loss is 13.03909991 points.
These penalties overlap by 2.11167116 points, so simply summing
separate failure rates overstates the total loss.

The fully constrained probability depends sensitively on S, D and m:

| Search Items S | Safe discards D | Bonus draws m | Fully constrained completion |
| ---: | ---: | ---: | ---: |
| 2 | 4 | 0 | 1.11496541% |
| 2 | 4 | 8 | 8.52418120% |
| 2 | 12 | 0 | 1.78675915% |
| 2 | 12 | 8 | 17.45345521% |
| 3 | 8 | 8 | 16.70046305% |
| 3 | 12 | 0 | 2.14160943% |
| 3 | 12 | 8 | 22.39363458% |

The comparison with eight bonus cards is a sensitivity experiment
conditional on that many being allowed and drawn, not an assertion
that eight opponent mulligans are common.

## Reproduction and limits

[tools/opponent_bonus_two_target_item.py](../../tools/opponent_bonus_two_target_item.py)
computes exact conditional fractions, including separate payment
and Prize ablations.

[The reproducer](two_target_item_reproduce.py) independently enumerates
opening hands, physical Prize subsets and bonus subsets for two small
decks. It checks all four ablations against the analytical kernel
as exact rational values. The shared GitHub Actions workflow tests
the reproducibility cases and the 60-card sensitivity.

This is still an intentionally bounded model. Cards outside the
designated safe-discard class are never discarded, even if a real
player would rationally burn an otherwise protected card. Search
sources are assumed playable Items with no lock, although actual
Expanded games may have Item lock, Tool/Supporter gates,
hand disruption, Bench constraints and turn timing. Targets are
assumed to be legal for the one-output search card's search
domain, and the target in hand may need to be played or evolved
before the turn can succeed. Multiple used search cards and searched
Pokémon can also change which other hand cards remain safe to pay;
the model conservatively requires dedicated fodder, preventing
those cross-resource payment interactions.

The result provides an exact **lower-cost feasibility scenario** for
a strictly specified payment policy and demonstrates how apparently
available connectors can fail at two independent physical layers.
It is not a first-turn attack probability or an optimized decklist.
