# Prize cards reduce the conditional Grand Tree-to-Gothitelle source ceiling

## Question

The source-bootstrap frontier identifies a hypothetical one-turn line that
starts with one evolved Gothitelle and three eligible Gothita, then uses
Grand Tree to produce up to three additional Gothitelle under per-entry
same-physical-Stadium return semantics.

How often could the three remaining Gothorita and three remaining Gothitelle
all avoid the six Prize cards, if the other specified cards are already
known not to be Prized and the remaining population is exchangeable?

## Sampling model

An illustrative 60-card four-copy Gothita/Gothorita/Gothitelle deck has
eight known non-Prize physical cards in the modeled position:

* one established Gothitelle evolution stack: Gothita, Gothorita,
  Gothitelle (three cards);
* three distinct ready Gothita (three cards);
* Grand Tree already in play and Brooklet Hill in hand (two cards).

That leaves 52 unknown physical cards, including three Gothorita and three
Gothitelle still needed by Grand Tree. Six Prize cards are drawn uniformly
from those 52 unseen cards. The other 46 are treated as filler for this
particular target supply question. All still-unprized critical evolution
cards are assumed to remain directly searchable in the deck rather than
stuck in hand or discard.

Let X be the number of remaining Gothorita Prized and Y the number of
remaining Gothitelle Prized. Then the joint exact distribution is

`P(X=x, Y=y) = C(3,x) C(3,y) C(46,6-x-y) / C(52,6)`.

The number of additional Gothitelle directly assemblable in the current
model is `K = min(3, 3-X, 3-Y)`. This projects physical joint Prize
placement through the action-capable source-bootstrap limit of three,
without assuming the two Prize counts are independent.

## Exact result

| Additional Gothitelle K | Probability |
|---|---:|
| 0 | 0.180991% |
| 1 | 6.197233% |
| 2 | 47.612444% |
| 3 | **46.009332%** |

The expected number of directly available additional Gothitelle is
**2.394501172** under the stated conditional model.

The chance of complete three-source assembly from directly searchable
cards is exactly

`C(46,6) / C(52,6) = 0.4600933171959455...`.

A product of the separate correct one-group zero-Prize marginals instead
gives about `0.4718011507`, overstating full assembly by **1.170783
percentage points**. The fixed number of Prize cards couples the two
groups, so their events cannot be multiplied as independent probabilities.

These numbers are combinatorial probabilities, rather than a Monte Carlo
simulation. The underlying source-bootstrap maximum of three comes from
the separate exact Stadium action search.

## Implementation and validation

* `tools/gothitelle_bootstrap_prize_availability.py`: exact rational
  two-group hypergeometric Prize distribution, expected completed source
  count, and independence-ablation diagnostic.
* `results/gothitelle_bootstrap_prize_availability/reproduce.py`: composes
  the existing Grand Tree source-bootstrap planner to derive its action
  cap and then checks exact fractions against independent brute-force
  labeled subset enumeration for small card populations.

Run:
`python results/gothitelle_bootstrap_prize_availability/reproduce.py`

## Interpretive limits

The entire sequence remains conditional on the **unresolved official
same-physical-Stadium re-entry ruling**. A per-physical-copy use-history
interpretation with only one Grand Tree would restrict the considered
one-turn continuation to one Stadium effect use.

A state formed by selecting opening hands, taking mulligans, drawing,
searching, recovering Prized cards, and building a Gothitelle before
Grand Tree is used may have a different Prize posterior. This model
specifies an exchangeable prior conditional only on the eight already
known non-Prize cards. It ignores more detailed K0/K1 information and
does not claim tournament frequency.

Even with all six critical evolution cards unprized, the real deck
must be able to leave them searchable in the deck, pay any required
resource costs, avoid locks, and legally activate Grand Tree on its
targets. An absent or incorrectly located evolution card can reduce
the achievable source count further.

For related mechanisms see
[dynamic Gothitelle bootstrap](../stadium_gothitelle_bootstrap/),
[Prize zone recovery](../prize_zone_recovery/), and
[Grand Tree physical evolution chain](../grand_tree_materialized_chain/).
