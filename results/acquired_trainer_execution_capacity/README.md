# Joint execution capacity after Trainer acquisition

## Question

After several Trainer cards have already reached the hand, can each payload be individually executable while the complete strategic line is still impossible?

Yes.

This result applies the same finite-capacity reasoning used for search connectors to the downstream execution stage.

Implementation: `tools/acquired_trainer_execution_capacity.py`  
Regression: `results/acquired_trainer_execution_capacity/reproduce.py`

## State model

An execution requirement identifies:

- the physical hand card class;
- Trainer action class;
- number of copies required;
- earliest permitted turn;
- deadline turn.

Each modeled turn supplies:

- Item, Tool, Supporter, and Stadium play permissions;
- remaining Supporter plays;
- remaining Stadium plays.

The solver allocates physical hand copies and quota units jointly. Items and Pokémon Tools use their play-permission channels without consuming a generic per-turn count in this model. Every executed payload consumes one physical copy from hand.

The result reports both:

- standalone feasibility for every requirement against the original state;
- exact joint feasibility after shared resources are allocated once.

## Same-turn Supporter collision

Two different Supporters are in hand. Each is required this turn.

With one Supporter use remaining:

- requirement A is individually feasible;
- requirement B is individually feasible;
- the pair is jointly infeasible;
- at most one of the two execution units can be completed.

With two Supporter uses remaining, the same pair becomes jointly feasible.

This is the downstream analogue of shared connector contention. Checking each payload against the same unmodified action budget double-spends the Supporter window.

## Deadline geometry

The same two acquired Supporters become jointly feasible when one is required this turn and the other is required exactly next turn, given one Supporter use in each window.

If both are restricted to next turn, the pair is jointly infeasible under the ordinary one-use next-turn window.

The turn boundary supplies a fresh quota, while deadlines determine whether that fresh capacity can actually be used.

## Physical-card reuse

A second regression gives the hand only one physical Boss's Orders while creating two strategic gust requirements in the same turn.

The modeled turn has two Supporter uses available.

Each gust requirement is individually feasible because each standalone check sees the same Boss's Orders.

The pair remains jointly infeasible because one physical card cannot execute twice.

Action quota alone therefore does not guarantee joint execution. Physical hand multiplicity is another shared capacity.

## Mixed action classes

One Supporter requirement and one Item requirement are jointly feasible in the same ordinary turn when both cards are in hand and both channels are open.

This confirms that execution contention is typed. The Supporter quota does not consume Item capacity.

## Locks and future windows

A Supporter that is locked in the current window but permitted next turn can still satisfy a deadline of next turn.

The same target would fail a current-turn deadline.

The solver receives per-turn permissions explicitly, so it does not assume that a lock persists or disappears across turns.

## Search-transaction integration

The regression composes the new scheduler with the previous exact Trainer-search transaction layer.

### Rosa -> Boss's Orders

Rosa retrieves Boss's Orders into hand and consumes the ordinary Supporter quota.

The resulting execution state is projected into a current-turn execution window.

A same-turn gust requirement is infeasible.

### Secret Box -> Boss's Orders

Secret Box pays its exact three-card discard and retrieves the same Boss's Orders.

Because the connector is an Item, the Supporter quota remains available.

The same-turn gust requirement is feasible.

This turns the earlier action-window observation into an exact deadline-capacity result.

## Strategic implication

The useful endpoint of a connector depends on the objective.

For acquisition-only objectives, moving the card to hand can complete the demand.

For tactical objectives such as a same-turn gust, the demand remains incomplete until an execution slot is allocated.

A realistic planner can therefore use a staged representation:

`searchable -> acquired -> schedulable before deadline -> executed`

Shared resources exist on both sides of acquisition:

- search connectors and discard costs before the card reaches hand;
- physical hand copies and action quotas after it reaches hand.

## Limits

This solver evaluates generic Trainer play capacity. It does not resolve card-specific effects, choose gust targets, check Stadium same-name restrictions, or validate Pokémon Tool attachment targets.

Item and Tool execution are treated as quota-unlimited after their generic play channels are open, consistent with the ordinary action model. Their card-specific legality still belongs in the action transaction.

Future windows are supplied explicitly. The solver does not predict whether a current lock source survives the opponent's turn.

## Next useful work

The next integration should let strategic demand declare its completion stage.

A demand such as `Boss's Orders acquired` should terminate at hand access.

A demand such as `gust executed this turn` should require both acquisition and a scheduled Supporter execution slot.

That distinction can then be inserted into bounded ALS planning without redefining search outputs themselves.
