# Belief-aware line evaluation and the value of re-inspection

## Question

Can the line-value framework operate after partial observations or knowledge-destroying Prize mutations, rather than only at the initial prior and fully known endpoints?

Yes. The current Prize belief can be supplied directly to a line evaluator.

Implementation: `tools/prize_belief_decision.py`

Reproducer: `results/prize_belief_decision/reproduce.py`

## Decision quantities

For each candidate line, the evaluator calculates its expected utility under the current `PrizeBelief`.

The best value available when the player must commit immediately is:

`V_fixed = max_l E[u_l(s)]`

The value if exact Prize composition is learned before choosing is:

`V_exact = E[max_l u_l(s)]`

The current value of exact information is:

`V_exact - V_fixed`

This is the same value-of-information structure used in the initial K0/K1 result, now applied to an arbitrary posterior.

## Finding: information can regain value after previously exact knowledge is degraded

Start with an exactly known six-Prize composition:

`{A, B, C, D, E, F}`

A known incoming card X is switched with one face-down Prize position while the outgoing identity is unknown.

The grouped posterior has six equally likely states, corresponding to which one of A through F left the Prize zone.

Now consider two strategic lines:

- line A works if singleton A is unprized;
- line B works if singleton B is unprized.

Under the six-state posterior:

- A is the outgoing card in 1/6 of states;
- B is the outgoing card in 1/6 of states;
- another card is outgoing in 4/6 of states.

If the player must choose a line immediately under uncertainty:

| Choice | Expected availability |
| --- | ---: |
| Commit to line A | 16.666666667% |
| Commit to line B | 16.666666667% |
| Best commit-now value | 16.666666667% |

If the player re-acquires exact Prize composition before choosing, they can select the correct live line in the A-outgoing or B-outgoing states:

`V_exact = 33.333333333%`

The value of re-inspection is therefore:

`16.666666667 percentage points`

This occurs even though the player had exact Prize knowledge earlier in the game.

## Re-inspection removes its own future value in a resolved state

Suppose re-inspection reveals the actual resulting composition:

`{B, C, D, E, F, X}`

A is known to be unprized.

The A line is now available with certainty in this Prize-only abstraction.

The best fixed value becomes 100%, and the remaining value of another exact inspection is zero.

The information value is therefore state-dependent and recurrent:

- exact knowledge can have zero immediate marginal value;
- a hidden Prize mutation can make exact information valuable again;
- re-inspection can collapse that value back to zero.

## General implication for planning

An information-aware planner should evaluate the current posterior at the point of each commitment.

It should not assign a permanent bonus merely because the player searched the deck earlier.

For each decision deadline, the planner can compare:

1. best action under the current belief;
2. best action after an available information-gathering action;
3. the cost and timing of that information action.

This allows direct comparison of options such as:

- commit now;
- use an Item search first;
- inspect all Prizes first;
- delay the commitment to a later turn;
- accept uncertainty because the information action is too expensive.

## Interaction with action timing

The exact-information action catalog shows that information can be acquired through Items, Supporters, Abilities, attacks, Energy effects, Tools, and direct Prize-inspection effects.

The belief-aware evaluator supplies the benefit side of the tradeoff.

The typed action model supplies the cost and timing side.

Combining them creates a standard value-of-information decision:

`net information value = policy improvement - action opportunity cost`

The opportunity cost can include a Supporter use, attack for the turn, Bench slot, discard cost, Energy commitment, one-per-game power, or connector consumption.

## Validation

The reproducer constructs the six-state posterior using the grouped belief kernel.

It verifies:

- each state has probability `1/6`;
- fixed A-line value is `1/6`;
- fixed B-line value is `1/6`;
- exact-information value is `2/6`;
- the value of re-inspection is `1/6`;
- after an actual state is re-inspected, the live line has value 1 and further perfect information has zero value in that resolved state.

## Limitations

Line utilities remain abstract and Prize-only.

The example treats moving a singleton out of the Prize zone as making it available. A full game model still has to track where the outgoing card actually went and whether the line can access it before its deadline.

Arc Phone, for example, moves the outgoing Prize card to the top of the deck. That is strategically different from putting it directly in the hand.

This result isolates composition information. Zone access and timing remain separate layers.

## Next useful work

The strongest extension is to make line requirements typed by zone and deadline.

A line should be able to require conditions such as:

- card unprized;
- card in hand by the current attack window;
- card searchable before the Supporter action is spent;
- Bench slot still open;
- discard resource still available.

Then the belief state can be evaluated against actual reachable lines rather than Prize-only availability.
