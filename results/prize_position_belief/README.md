# Prize position knowledge and action value

## Question

Is exact knowledge of Prize-card composition sufficient for every Prize-sensitive decision?

No. Some legal effects act on a physical face-down Prize position. Two information states can agree exactly on which strategic card groups are Prized and still assign different values to the same action because the identity-to-position mapping differs.

Implementation: `tools/prize_position_belief.py`

Regression: `results/prize_position_belief/reproduce.py`

## Mechanics represented

The bundled card and rule sources establish several distinct positional transitions.

- **Arc Phone** (`swsh11-152`) looks at the top card of the deck and may switch it with one chosen face-down Prize card. The chosen physical Prize position therefore matters.
- **Peonia** (`swsh6-149`) can move up to three Prize cards to hand and then places the same number of hand cards face down as Prize cards. Its card text contains no Prize shuffle.
- **Gladion** (`sm4-95`) looks at all face-down Prize cards, takes one, then explicitly shuffles Gladion into the remaining Prize cards.
- Advanced Player's Rulebook E-35 defines a face-down shuffle as randomization that leaves neither player with information about the order of those cards.

The official Pokémon Asia Peonia Q&A also states that the hand cards placed as new Prize cards do not need to be shuffled and may be placed in any desired order. This makes position knowledge a legal information state rather than a purely hypothetical representation.

## Representation

`PrizePositionBelief` is a grouped belief over physical Prize slots.

Each support state is an ordered tuple such as:

`("TARGET", None, None, None, None, None)`

where `None` is the implicit filler group.

The kernel can:

- construct exact composition with unknown position mapping;
- construct a fully known position mapping;
- project positional beliefs back to grouped composition;
- condition on observing one physical position;
- randomize positions while preserving composition;
- compute a singleton target's position entropy;
- compute the best hit probability when an action may choose one Prize position.

This is intentionally a small information kernel. Physical card movement remains the responsibility of the existing identity and conservation layers.

## Counterexample: identical composition, different action value

Consider six face-down Prize cards whose exact grouped composition is known to be:

- one `TARGET`;
- five filler cards.

Compare two observer states.

### State U: composition known, target position unknown

The target is uniformly distributed across six physical Prize slots.

- composition entropy: 0 bits;
- target-position entropy: `log2(6) = 2.584962501` bits;
- best probability of choosing the target slot: `1/6 = 16.666666667%`.

### State K: same composition, target position known

The target is known to occupy one particular Prize slot.

- composition entropy: 0 bits;
- target-position entropy: 0 bits;
- best probability of choosing the target slot: `1 = 100%`.

Both states project to exactly the same composition belief.

Their best physical-slot action values differ by **83.333333333 percentage points**.

This is a state-sufficiency counterexample. A composition-only Prize belief cannot be a sufficient state representation for policies that can choose specific Prize positions.

## Face-down shuffling destroys position information without changing composition

Apply an E-35-style face-down shuffle to State K.

The resulting state still has one `TARGET` and five fillers with certainty. Composition entropy remains 0 bits.

The target position becomes uniform across all six slots:

- target-position entropy rises from 0 to `2.584962501` bits;
- best chosen-slot hit probability falls from 100% to `16.666666667%`.

This is an information transition whose effect is invisible to a composition-only kernel.

Gladion gives a concrete card-text example of this geometry. The player sees the face-down Prize identities before taking one, then shuffles the known incoming Gladion card with the remaining Prize cards. Exact composition can remain known while useful position mapping is erased.

## Partial position information has measurable value

Starting from State U, suppose the observer learns that one particular slot contains filler.

The target remains uniformly distributed over the other five slots.

The best chosen-slot hit probability rises from:

`1/6 = 16.666666667%`

to:

`1/5 = 20%`.

Position knowledge therefore has graded value. It is not limited to the two extremes of fully known and fully unknown.

## Peonia to Arc Phone policy implication

Peonia provides a concrete way to preserve which physical slots were replaced.

Assume:

- six Prize cards contain one target;
- their exact composition is known;
- target position is initially unknown;
- Peonia chooses three physical Prize cards;
- the three replacement cards are placed back into those same chosen positions without a shuffle;
- if Peonia did not take the target, Arc Phone may then choose one of the three untouched positions.

The target is taken by Peonia with probability `3/6 = 1/2`.

Conditional on missing it, the target is known to be among the three untouched positions, so Arc Phone can select a target-containing slot with probability `1/3`.

The probability that the target is either taken by Peonia or selected by Arc Phone is therefore:

`1/2 + (1/2)(1/3) = 2/3 = 66.666666667%`.

If the six Prize positions were randomized after the Peonia miss, the Arc Phone step would instead be `1/6`, giving:

`1/2 + (1/2)(1/6) = 7/12 = 58.333333333%`.

Preserving position information is worth **8.333333333 percentage points** in this isolated policy.

Arc Phone moves the selected Prize card to the top of the deck in this line. A complete material-access policy would still need to model the later draw or other top-deck access.

## Strategic implication

Prize information has at least two separable dimensions:

1. **composition knowledge**: which identities or strategic groups are in the Prize zone;
2. **position knowledge**: which physical face-down slot contains each identity or group.

Effects can preserve one dimension while changing the other.

A planner that collapses both into a single K0/K1 composition flag can misvalue position-sensitive effects even when its composition posterior is exact.

## Validation

The regression checks:

- the bundled Peonia text and absence of a shuffle instruction;
- the bundled Arc Phone switch wording;
- the bundled Gladion shuffle wording;
- the E-35 rulebook statement that face-down shuffling randomizes order information;
- equality of composition distributions between known-position and unknown-position states;
- zero composition entropy in both states;
- the exact `log2(6)` target-position entropy under unknown order;
- `1/6`, `1`, and `1/6` chosen-slot hit probabilities before knowledge, with knowledge, and after shuffling;
- the `1/5` improvement after ruling out one filler slot.

## Limitations

The current kernel uses strategic card groups rather than physical instance IDs.

It represents one observer at a time. Observer-indexed belief storage exists elsewhere in the repository and can wrap this richer belief type in future work.

All positions in this first result are face down. Face-up status, position-specific visibility to different players, and Town Map-style public states require another state dimension.

The Peonia and Arc Phone calculation isolates position information. It does not include access to those Trainers, Supporter or Item contention, turn timing, top-deck draw access, Item lock, or deck-slot cost.

## Next work

A useful continuation is to compose this positional kernel with the Prize effect catalog so transition atoms such as `shuffle_prizes`, `swap_prize_topdeck`, `prize_to_hand`, and `hand_to_prize` update the correct information dimensions.

A second continuation is a position-aware Prize-taking transition that preserves exact physical truth while updating different observers according to what each player can see.
