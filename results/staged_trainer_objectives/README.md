# Staged Trainer objectives: acquisition choice changes with execution deadline

## Question

Can one planner choose among search actions while preserving both pre-acquisition costs and post-acquisition execution windows?

Yes.

This result adds `tools/staged_trainer_objectives.py`. It enumerates available Trainer acquisition actions, consumes shared discard and current-turn Trainer quotas, conserves the physical searchable-card pool, adds selected targets to hand, then calls the acquired-Trainer execution scheduler for deadline-sensitive objectives.

Regression: `results/staged_trainer_objectives/reproduce.py`

## Why physical search conservation matters

Green's Exploration and Computer Search can both point at one Boss's Orders in deck.

They are alternative routes to the same physical target. The staged planner receives `searchable_cards={"boss": 1}`, so once either route acquires the singleton, the other route cannot create another copy.

This closes a cross-stage double-counting hole: connector availability, hand acquisition, and downstream execution all share the same physical card pool.

## Acquisition-only objective

With one current Supporter use and two discardable cards:

- Green -> Boss costs no modeled discard and consumes the Supporter use;
- Computer Search -> Boss costs two discardable cards and preserves the Supporter use.

If the objective ends when Boss's Orders reaches hand, both routes complete it.

The planner's tie break prefers lower discard expenditure, so it chooses Green.

## Same-turn execution objective

Change only the objective to require Boss's Orders to execute this turn.

Green still acquires the target, but its own Supporter use leaves no ordinary Supporter slot for Boss's Orders.

Computer Search preserves that slot.

The planner therefore switches to Computer Search and spends two discardable cards.

With only one discardable card, the Computer Search route is unavailable and the same-turn execution objective becomes infeasible even though Green can still acquire the target.

## Quota and deadline reversals

If the current turn has two Supporter uses, Green can acquire Boss's Orders and leave one use for execution. The planner switches back to Green because it completes the objective without discard expenditure.

If the Boss's Orders deadline is next turn, one ordinary current Supporter use plus one next-turn use also makes Green optimal. Green acquires now, then Boss's Orders executes in the next window.

Connector choice therefore depends on the execution deadline as well as access.

## Multi-axis staged objective

A second concrete state compares two trusted two-output actions:

- Green -> Boss's Orders + Quick Ball;
- Secret Box -> Boss's Orders + Quick Ball.

The objectives require Quick Ball to be acquired and Boss's Orders to execute this turn.

With three discardable cards, Secret Box completes both units because it is an Item and preserves the Supporter execution window.

Green completes the Quick Ball acquisition unit but misses the same-turn Boss's Orders execution unit.

With only two discardable cards, Secret Box is unavailable, so the maximum objective completion falls from two units to one.

This composes output multiplicity, discard gating, target conservation, and action-window execution in one policy state.

## Methodological implication

The objective endpoint belongs in the optimization problem.

For the same game state:

- an acquisition objective can prefer a Supporter connector with lower payment cost;
- a same-turn execution objective can prefer an Item connector with higher payment cost;
- an extra Supporter quota or later deadline can reverse the choice again.

A route should therefore be scored against the requested completion stage rather than against target access alone.

## Limits

Acquisition action profiles are trusted inputs. This module does not parse card text or execute the acquisition card's full physical transaction. Existing compiler and transaction layers should be used to generate or validate those profiles.

Discardability is still a scalar pool here. Exact discard identities remain in the dedicated discard-witness layer.

Only current-turn acquisition actions are modeled; downstream execution can span the explicit future windows supplied by the caller.

## Next useful work

The strongest next extension is an adapter from exact Trainer search transactions or compiled typed search profiles into `TrainerAcquisitionAction` objects, so staged objectives can be generated from card semantics instead of hand-authored trusted actions.
