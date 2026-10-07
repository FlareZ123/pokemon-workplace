# A Prized Supporter can be accessible and still miss its execution window

## Question

Does same-turn hand access to a Prized Supporter imply that a line can actually use that Supporter before the turn ends?

No. The action that recovers the card can consume the same once-per-turn channel needed to execute it.

This result connects the physical Prize-position work to the repository's canonical turn-action budget.

Implementation: `tools/prize_supporter_execution.py`

Regression: `results/prize_supporter_execution/reproduce.py`

## Concrete recovery lines

Assume one strategically required Supporter is known to be among six face-down Prize cards and its physical position is initially unknown.

Compare two same-turn routes.

### Direct Item route

`Arc Phone -> Trekking Shoes`

Arc Phone probes one chosen face-down Prize position. Trekking Shoes observes the outgoing top card and can put it into hand.

With no prior position exclusions, target hand access is:

`1/6 = 16.666667%`.

Neither card consumes the Supporter channel.

### Peonia route

`Peonia -> Arc Phone -> Trekking Shoes`

Peonia can check three Prize positions. If it misses, preserved position information leaves the target among the three untouched positions, and Arc Phone can probe one of those.

The existing positional result gives same-turn hand access:

`2/3 = 66.666667%`.

Peonia itself is a Supporter.

## Ordinary one-Supporter turn

The basic action budget permits one Supporter play.

The two routes therefore have different execution values:

| Route | Target reaches hand | Target Supporter can be played this turn |
| --- | ---: | ---: |
| Arc Phone -> Trekking Shoes | 1/6 | 1/6 |
| Peonia -> Arc Phone -> Trekking Shoes | 2/3 | 0 |

Optimizing hand access alone strongly favors Peonia.

For a same-turn objective that requires playing the recovered Supporter, the Peonia line has zero completion probability because its own Supporter play has already consumed the ordinary channel.

The direct Item line is less likely to find the target, yet every successful recovery remains executable.

## Gladion makes the separation even sharper

Gladion looks at the face-down Prize cards and puts one of them into hand.

Conditioned on the required Supporter being Prized and Gladion being playable, target hand access is therefore 100%.

Gladion is itself a Supporter.

Under the ordinary one-Supporter rule:

| Route | Target reaches hand | Target Supporter can be played this turn |
| --- | ---: | ---: |
| Gladion | 1 | 0 |

This is an extreme access-versus-execution counterexample. Perfect recovery does not complete a same-turn line when the recovery action consumes the payload's action channel.

## The turn boundary reverses the ordinary ranking

If the recovered Supporter is required on the next turn instead of the current turn, the ordinary Supporter budget resets before execution.

Assuming the recovered card remains in hand and the same quota ceiling applies next turn:

| Route | Execute this turn | Execute next turn |
| --- | ---: | ---: |
| Arc Phone -> Trekking Shoes | 1/6 | 1/6 |
| Peonia -> Arc Phone -> Trekking Shoes | 0 | 2/3 |
| Gladion | 0 | 1 |

The current-turn objective favors the direct Item route over either Supporter-based recovery line.

The next-turn objective favors Gladion because its perfect recovery survives the turn boundary and the ordinary Supporter usage count resets.

This is a temporal connector-dominance reversal caused only by the execution deadline.

## Dual Brains changes the line value

The bundled Expanded-legal Magnezone `bw8-46` has Dual Brains:

`During your turn, you may play 2 Supporter cards.`

The repository's action-quota layer represents this as a Supporter limit of two.

With Dual Brains active:

| Route | Target reaches hand | Target Supporter can be played this turn |
| --- | ---: | ---: |
| Arc Phone -> Trekking Shoes | 1/6 | 1/6 |
| Peonia -> Arc Phone -> Trekking Shoes | 2/3 | 2/3 |
| Gladion | 1 | 1 |

The same physical Prize policy now converts its entire hand-access probability into same-turn execution probability.

Board state has changed the value of the recovery line without changing the Prize posterior or the search cards.

## Ability lock changes the same-turn recovery ranking

The regression derives the extra Supporter quota from a physical `bw8-46` Magnezone object.

With Dual Brains live, the same-turn execution ranking is:

`Gladion = 1 > Peonia line = 2/3 > Arc Phone line = 1/6`.

The same board is then evaluated with the existing Neutralizing Gas lock profile. The lock layer marks the Dual Brains object as suppressed, and board-derived Supporter capacity returns from two to one.

The ranking becomes:

`Arc Phone line = 1/6 > Peonia line = Gladion = 0`.

The Prize posterior is unchanged. Ability state changes the downstream execution capacity and changes which recovery line is best.

## Evidence

The regression verifies the bundled card texts for:

- Peonia `swsh6-149`;
- Arc Phone `swsh11-152`;
- Trekking Shoes `swsh10-156`;
- Magnezone `bw8-46` with Dual Brains;
- Gladion `sm4-95`.

It also verifies the Advanced Player's Rulebook text that Items may be used any number of times during a turn and Supporters ordinarily may be used only once.

The execution bridge uses `TurnActionBudget` and the existing `DUAL_BRAINS` quota grant rather than reimplementing Supporter counting.

## Strategic implication

Access and executable access are different objectives.

A search or recovery line can improve the probability that a card reaches hand while simultaneously consuming the action channel required to use it.

This is a concrete form of Supporter contention and connector domination:

- Peonia is a strong Prize-access connector;
- the recovered card can be the exact resource the line needs;
- using Peonia excludes ordinary same-turn use of that recovered Supporter.

The relevant state therefore includes:

- hidden-zone access probability;
- target card class;
- current action quota;
- quota-modifying effects;
- the deadline by which the target must be executed.

## Relation to acquisition deadlines

The preceding Prize-position deadline result models when a target must be acquired.

This result shows why acquisition deadlines are only one layer.

A Supporter can meet its hand-access deadline and still fail an execution deadline because the Supporter channel is no longer available.

For real ALS modeling, the planner should distinguish at least:

`hidden target -> acquired -> executable -> executed`.

## Limits

The direct route assumes Arc Phone and Trekking Shoes are already available and usable.

The Peonia route conditions on the three-card Peonia selection and the follow-up Items being available. The model does not price deck slots, search access to those Trainers, Item lock, Ability lock on Dual Brains, hand disruption, or alternative uses of the Supporter channel.

The required Prized card is modeled by card class as a Supporter rather than by one specific named tactical effect.

## Next work

A stronger action-deadline kernel can attach an execution requirement to each acquired target class and compose it with turn budgets directly.

A concrete extension should compare mixed targets, such as a Prized Item and a Prized Supporter, where the same positional observation can leave one target immediately executable and the other blocked by contention.
