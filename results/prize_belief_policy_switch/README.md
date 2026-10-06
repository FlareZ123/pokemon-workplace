# Belief-driven line switching before K1

## Question

Can ordinary observations change the preferred strategic line before the player performs a full deck search?

Yes. A pre-search policy can rationally change as the Prize posterior moves.

This result uses the exact Prize belief model together with the K0/K1 line evaluator.

Reproducer: `results/prize_belief_policy_switch/reproduce.py`

## Decision example

Consider two abstract strategic choices.

Line A has normalized utility `1.0` when singleton A is unprized. Its utility is zero when A is Prized.

Line B has utility `0.86` in every modeled Prize state.

The example isolates information effects. The utility values are illustrative rather than claims about any specific Pokémon cards.

Let `U` be the number of still-unseen cards that contain all six modeled Prize cards. Condition on singleton A remaining unseen.

Its Prize posterior is:

`6 / U`

so the pre-search expected utility of line A is:

`E[A | U] = 1 - 6/U`

Line B remains at:

`E[B] = 0.86`

The K0 player should choose A while:

`1 - 6/U >= 0.86`

Solving gives the threshold:

`U >= 42.857142857`

Since `U` is an integer, A remains preferred at `U = 43`. B becomes preferred at `U = 42`.

## Finding 1: repeated misses can flip the preferred K0 line

Immediately after a seven-card accepted opening, the modeled unseen population is 53.

If each later observation is a non-target card and singleton A remains unseen, `U` shrinks one card at a time.

| Additional non-target observations | Unseen population U | Expected utility of A | Preferred K0 line |
| ---: | ---: | ---: | --- |
| 0 | 53 | 88.679245283% | A |
| 5 | 48 | 87.500000000% | A |
| 10 | 43 | 86.046511628% | A |
| 11 | 42 | 85.714285714% | B |
| 13 | 40 | 85.000000000% | B |

No full deck search is required for this switch.

The evidence comes from repeated observations that keep A in the unseen population while other possible non-Prize locations disappear.

## Finding 2: K0 should be treated as a policy over beliefs

A binary K0 flag identifies that exact Prize composition remains unknown. It does not specify the posterior that should drive decisions.

In this example, two K0 states lead to different rational actions:

- at `U = 53`, choose A;
- at `U = 42`, choose B.

The difference comes from observation history.

A game-state optimizer therefore needs enough Prize-belief state to recompute expected line value when relevant cards remain unseen.

## Finding 3: the value of exact K1 information also moves with the posterior

After a full deck search, the player can choose A when it is live and fall back to B when A is Prized.

For this two-line example:

`V_K1 = (1 - 6/U) * 1.0 + (6/U) * 0.86`

The K0 value is the larger of the two pre-search expected utilities.

Representative values from the reproducer:

| Additional misses | K0 value | K1 value | Value of Prize information |
| ---: | ---: | ---: | ---: |
| 0 | 88.679245% | 98.415094% | 9.735849 pp |
| 5 | 87.500000% | 98.250000% | 10.750000 pp |
| 10 | 86.046512% | 98.046512% | 12.000000 pp |
| 11 | 86.000000% | 98.000000% | 12.000000 pp |
| 13 | 86.000000% | 97.900000% | 11.900000 pp |

The value of a first full search depends on the current belief state and on the fallback line.

Near the policy threshold, exact information is especially valuable because uncertainty determines which line should be chosen.

## General threshold

Let:

- the singleton-dependent line have live utility `a`;
- the robust line have utility `b`;
- `a > b`;
- `P` Prize cards remain modeled;
- `U` cards remain unseen;
- the singleton remains unseen.

The singleton line has expected utility:

`a * (1 - P/U)`

It is preferred when:

`a * (1 - P/U) >= b`

which gives:

`U >= P / (1 - b/a)`

This threshold expresses how line value and Prize uncertainty interact.

A higher fallback utility causes an earlier switch. A larger number of Prize cards also makes the singleton line less attractive for the same unseen population.

## Strategic interpretation

This model creates a continuous bridge between initial uncertainty and exact K1 knowledge.

A practical decision engine can update in three steps:

1. condition the Prize belief on newly visible information;
2. recompute expected utility for each currently feasible line;
3. choose an action using the updated values.

A full deck search then replaces the posterior with the exact Prize state.

This representation can interact with AMR, DCI, connector contention, and ALS timing. If a line requires a costly commitment, the decision should use the belief available at the commitment point.

## Validation

The reproducer computes the analytic threshold directly.

It evaluates the same states with `evaluate_prize_information()` and verifies that the singleton line value equals `1 - 6/U`.

It also asserts that the preferred K0 line is A at `U = 43` and B at `U = 42`.

## Limitations

The robust line's utility of 0.86 is an illustrative constant.

Actual game utilities depend on matchup, board state, damage, Prize trade, tempo, future resources, locks, and many other variables.

The example conditions on singleton A remaining unseen. If A becomes visible, its Prize status is resolved immediately and the decision state changes.

The model also assumes no additional deck-order information beyond ordinary visible non-Prize cards.

## Next useful work

A stronger policy model can let several uncertain resource groups influence line value simultaneously.

That extension should combine:

- posterior Prize distributions;
- typed line feasibility;
- state-dependent utilities;
- irreversible resource commitments;
- the timing of the first full deck search.

The result would support belief-aware line selection throughout the early game rather than only at the K0 and K1 endpoints.
