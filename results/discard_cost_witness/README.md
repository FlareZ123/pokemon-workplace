# Exact discard-cost witness

## Question

Is the scalar `discardable_cards` capacity used by connector-feasibility models sufficient to execute a discard cost against canonical hand state?

No.

It can answer whether a discard requirement is payable, while several different exact card selections can have the same scalar cost and leave different future hands.

Implementation: `tools/discard_cost_witness.py`  
Regression: `results/discard_cost_witness/reproduce.py`

## Counterexample

A hand contains Secret Box plus four candidate discard cards:

- Basic Fire Energy;
- Double Colorless Energy;
- Boss's Orders;
- a Stadium.

Secret Box requires three other cards to be discarded.

At the coarse resource level:

- discardable capacity = 4;
- discard cost = 3.

That is enough to say the cost is payable.

For state execution, however, there are four exact three-card selections. Each one leaves a different candidate card in hand.

Those resulting states can have different future value because Energy identity, gust access, Stadium access, and later discardability are mechanically and strategically distinct.

## Exact selection layer

`enumerate_discard_selections()` receives the current exchangeable `ZoneCountState`, candidate card classes, optional per-class maxima, and the required discard count. It returns exact card-class count vectors whose total equals the cost.

`apply_discard_selection()` moves those exact copies from hand to discard and verifies card-class conservation.

A stale selection is rejected if one of its chosen cards is no longer in hand when execution occurs.

## Relation to DCI and UDP

This layer does not assign universal DCI values.

Instead, it gives a deterministic execution representation after a policy has already decided which card classes are currently allowable or how many copies of each may be spent.

In the regression, setting Boss's Orders to `max_copies=0` reduces four legal three-card selections to one and guarantees Boss remains in hand. That is a simple frozen-state representation of strategic protection.

A future policy can derive these per-class limits from richer DCI, matchup, Prize, or line-of-play state.

## Representation consequence

The repository now has two analogous execution-witness requirements:

1. a search demand profile does not identify which target card was retrieved;
2. a scalar discard cost does not identify which hand cards paid that cost.

Both are useful projections for feasibility and optimization. Neither should be treated as a sufficient canonical execution record.

## Limits

The module handles only exact card-class selection and hand-to-discard movement.

It does not decide which discard selection is strategically best, model continuous DCI scores, choose among future lines, or execute the surrounding Trainer card action atomically.

The next stronger composition should combine the exact searched-target witness, exact discard-cost witness, the played Trainer card's own zone transition, lock legality, Supporter/Stadium action-budget consumption, and the resulting zone state.
