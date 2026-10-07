# Grouped Prize belief transition kernel

## Question

What representation can support uncertain Prize priors, partial observations, exact inspection, knowledge-destroying swaps, and re-inspection in one state type?

A probability distribution over grouped Prize compositions is sufficient for many line-level questions.

Implementation: `tools/prize_belief_kernel.py`

Reproducer: `results/prize_belief_kernel/reproduce.py`

## Representation

Choose strategically relevant groups such as:

- one critical singleton;
- copies of an attacker;
- copies of a rescue card;
- a shared connector.

A state vector records how many cards from each group are currently in the Prize set.

Cards outside the modeled groups share one implicit filler category.

The belief is a probability distribution over those state vectors.

This representation intentionally discards physical deck order and individual identities within a group. It preserves the information needed for many availability and line-choice calculations.

## Transition 1: randomized Prize prior or redeal

`PrizeBelief.from_hypergeometric()` creates the exact multivariate-hypergeometric distribution for drawing the current Prize set uniformly from a known pool.

For a singleton A in a 53-card unknown pool with six Prize cards:

| A copies Prized | Probability |
| ---: | ---: |
| 0 | 88.679245283% |
| 1 | 11.320754717% |

This reproduces the initial pre-search posterior used in the earlier belief-state result.

The same constructor also represents a full Prize redeal such as Rotom Dex after the combined pool composition and size are known.

## Transition 2: partial Prize observation

`observe_random_position()` conditions the belief on revealing the group identity at one physical Prize position.

For the singleton example, observing A at the selected Prize position collapses the grouped posterior to:

`{A: 1}: probability 1`

The observation does not remove the card.

This is the Bayesian update needed for one-Prize inspection effects such as attacks that look at one face-down Prize card.

With several modeled groups or multiple copies, a one-card observation can narrow the distribution without making it exact.

## Transition 3: exact composition

`PrizeBelief.from_exact()` represents a complete all-Prize inspection or a composition inferred from full deck inspection.

The belief contains one state with probability one and has zero entropy.

This is the generalized exact-information state that replaces a one-way K1 flag.

## Transition 4: known incoming card, unknown outgoing Prize identity

`replace_unknown_position_with_known()` models an Arc Phone-like composition update.

Assume the current Prize composition is exactly known while the card-to-position mapping is unknown.

Start with six physically distinct singleton groups:

`{A, B, C, D, E, F}`

and a known incoming card X.

Switch X with one chosen face-down Prize position without learning the outgoing identity.

The grouped belief becomes six equiprobable states:

- X replaces A;
- X replaces B;
- X replaces C;
- X replaces D;
- X replaces E;
- X replaces F.

The distribution has:

`log2(6) = 2.584962501 bits`

of entropy.

This reproduces the non-monotonic knowledge example with an explicit probability state.

## Transition 5: re-inspection

If a later full deck search or all-Prize inspection reveals which of those six states actually occurred, the belief collapses to a point mass again.

The information timeline can therefore be represented naturally as:

`prior -> partial -> exact -> uncertain -> exact`

No special-case K0/K1 state machine is necessary.

## Why grouped states are useful

A full physical-card posterior can be enormous.

Most strategic questions only need coarser facts, such as:

- whether at least one attacker copy is unprized;
- how many rescue copies are Prized;
- whether a shared singleton connector is present;
- whether a specific payload is accessible.

Grouping cards by strategic role can reduce the belief state dramatically while preserving the variables that determine line feasibility.

The grouping should be chosen for the research question. Cards that are strategically distinct should remain separate groups.

## Probability conservation

Every stochastic transition in the current kernel preserves total probability mass.

The reproducer asserts normalization after:

- the initial hypergeometric prior;
- a one-position observation;
- an unknown-position replacement;
- a fresh redeal.

This makes the kernel suitable as a lower-level component in a larger game-state simulator.

## Relationship to line evaluation

The existing `prize_information_value.py` tool evaluates strategic lines against grouped Prize states.

The belief kernel supplies exactly that kind of state distribution.

A direct next integration can replace the earlier hard-coded hypergeometric enumeration with an arbitrary `PrizeBelief`.

That would allow expected line values to be recomputed after:

- opening observations;
- partial Prize reveals;
- Arc Phone-like swaps;
- Rotom Dex-like redeals;
- exact re-inspection.

The line evaluator would then operate on the current information state rather than assuming either an initial prior or complete information.

## Limitations

The current kernel models Prize composition only.

It does not track:

- identity-to-position mapping;
- deck order;
- card zones outside the Prize set;
- the physical cards represented by filler;
- Prize-taking actions that remove a card;
- unknown incoming cards drawn from a separately modeled deck distribution;
- opponent knowledge;
- action timing or costs.

The random-position model assumes that the selected physical Prize position is exchangeable with respect to identity. If a previous effect revealed position information, that assumption must be refined.

The entropy measure is descriptive. Strategic value depends on how the uncertainty changes available lines and utilities.

## Next useful work

The immediate extension is to connect `PrizeBelief` to the line evaluator.

For each belief state, a planner should compute:

- which typed lines are feasible;
- the best current action under uncertainty;
- expected value of acquiring more information;
- expected value after stochastic Prize mutations.

That would turn the current collection of exact calculations into a reusable belief-aware decision layer.
