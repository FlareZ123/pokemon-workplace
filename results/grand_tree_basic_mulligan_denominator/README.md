# More alternative Basic starters can dilute a narrow conditional setup statistic

## Question

Deck researchers sometimes compare consistency metrics *conditional on
a legal opening hand*. Changing the number of Basic Pokémon changes
which seven-card hands count as legal. Can a metric of one specific
Gothita-based Prize-repair line decrease solely because extra
otherwise-inert Basic Pokémon make more hands valid?

Yes. This is an exact sample-selection effect, with a useful
invariance test that distinguishes a real change in opening
card combinations from a changed conditioning denominator.

## Controlled deck population

Start from the same 60-card Grand Tree rescue line:

* four Gothita Basic;
* one singleton each of Gothorita, Gothitelle,
  Grand Tree ACE SPEC, Pokémon Communication;
* two Gladion and two Arven;
* all remaining 48 physical cards are initially inert filler.

Among those otherwise-inert filler cards, vary the number of
**other** Basic Pokémon between 0 and 16, without changing
the number of Gothita, Trainers or other required cards.
These extra Basics have distinct legal names and no modeled
search or game effect. They can satisfy the *general* legal
starting-hand requirement but cannot replace the Gothita
required by the selected Grand Tree line.

The specific success certificate remains exactly as in
[the unified Arven model](../grand_tree_arven_union_access/):
opening contains Gothita, Gladion, and Grand Tree; the sole
Gothorita is Prized; Gothitelle remains searchable; and
Communication is already in hand, naturally drawn or
obtained by going-second first-turn Arven.

Every qualifying hand already contains a legal Basic Gothita,
so reclassifying other filler as different Basic Pokémon
does **not change the numerator** of that event in the
unconditioned 60-card shuffle. However, it increases the
number of seven-card hands accepted under the Basic rule.

## Exact invariant

With `x` extra other Basic Pokémon,

`P(valid opening) =
1 - C(56-x,7)/C(60,7)`.

The conditional event probability is

`P(event | valid) =
P(event in one 60-card shuffle) / P(valid opening)`.

The event numerator remains unchanged when replacing
inert filler by other Basic Pokémon because the event
itself always includes a Gothita.

Therefore, the product

`P(event | valid) * P(valid)`

is **exactly invariant** to the number of extra Basic
starters, while the conditional event statistic decreases.

## Quantitative result

Two Gladion, two Arven, four Gothita and one Grand Tree;
all comparisons use the same physical population size.

| Other Basic starters | Legal opening | Certificate going first, conditional | Certificate going second, conditional |
|---:|---:|---:|---:|
| 0 | 39.950% | 0.016658% | 0.038448% |
| 2 | 54.144% | 0.012291% | 0.028369% |
| 4 | 65.359% | 0.010182% | 0.023501% |
| 8 | 80.935% | 0.008222% | 0.018978% |
| 12 | 90.078% | 0.007388% | 0.017052% |
| 16 | 95.173% | 0.006992% | 0.016139% |

Legal-opening probability more than doubles between
zero and sixteen alternative Basics. The *conditional*
going-second event frequency falls by more than half,
although the number of raw shuffled hands already
containing the required Gothita and resource cards
is mathematically unchanged.

This is **not a deck-building recommendation** to remove
Basic Pokémon. In reality, additional Basics can reduce
mulligans, avoid losing with no bench, and provide
search or tactical value. The experiment isolates a
conditioning effect on a strictly defined event.

## Implementation and validation

Extended `tools/grand_tree_arven_union_access.py` with
`extra_basics`, a number of otherwise-inert filler
cards reclassified as other legal Basic Pokémon.
The numerator's hypergeometric category selection
is unchanged, and the accepted-opening denominator
uses the correct expanded Basic population.

The earlier independent physical oracle in
`results/grand_tree_arven_union_access/reproduce.py`
now distinguishes Gothita Basic from other Basic
identities, accepting either as a legal opening
while continuing to require Gothita for the target line.

`python results/grand_tree_basic_mulligan_denominator/reproduce.py`

The reproducer compares exact rational formulas to
labeled opening/Prize/turn-draw universes for multiple
small decks and extra-Basic populations. It checks the
invariant raw-shuffle event probability across each
population and confirms the expected monotone direction.

## Implications and limits

When comparing decks with different Basic counts,
always specify whether setup consistency is measured
per freshly shuffled seven-card hand, per accepted
opening hand, per played game with mulligans, or per
full game after opponent bonus draws. These are distinct
sample spaces.

The raw-shuffle invariance is exact only because the
additional Basic cards have no modeled effect outside
opening acceptance, and the target certificate
already includes a Gothita. If the other Basics have
Abilities, attack roles, alternate access paths, or
opponent-dependent outcomes, the event itself may change.

This model does not simulate actual mulligan resolution,
the number of extra cards an opponent chooses to draw,
the probability of a real deck's later setup, or
game success. It contributes a methodological control
for conditional opening-rate comparisons, not a
metagame ranking.
