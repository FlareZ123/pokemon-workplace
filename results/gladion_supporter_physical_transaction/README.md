# Gladion physical transaction with Supporter bandwidth

## Question

The repository already has a physical Gladion kernel that moves one selected face-down Prize card to hand and shuffles the played Gladion into the remaining Prize cards.

Can that literal zone transition share the same finite Supporter action budget used by other turn-state machinery?

Yes.

Implementation: `tools/gladion_supporter_physical_transaction.py`  
Regression: `results/gladion_supporter_physical_transaction/reproduce.py`

## Transaction

The wrapper validates the current player channels and consumes one `TurnAction.SUPPORTER` from the canonical `TurnActionBudget` before calling `resolve_gladion_physical()`.

For every physical shuffle outcome it preserves:

- the selected Prize instance moving to hand;
- the played Gladion instance moving from hand to Prize;
- all remaining Prize instances becoming face down;
- the existing deck-top instance;
- per-card-class physical totals;
- the updated Supporter budget.

A Supporter lock or an exhausted Supporter quota rejects the action before the physical Prize transition is returned.

## Regression

The witness begins with:

- materialized Gladion in hand;
- two materialized face-down Prize cards;
- one materialized deck-top card;
- an unused ordinary Supporter window.

Selecting the first Prize produces two equally likely post-shuffle orderings.

In both:

- the selected Prize card is in hand;
- Gladion is in Prize;
- the other original Prize remains in Prize;
- the deck top is unchanged;
- the Supporter budget is spent;
- card totals are conserved.

The regression separately verifies Supporter lock and an already-used ordinary Supporter quota both reject the transition.

## Why this bridge matters

Literal Gladion destination and Supporter contention belong to the same executable line.

A Prize-rescue planner that preserves the unusual hand-to-Prize movement while forgetting the one-Supporter window can still admit impossible same-turn combinations.

Conversely, a turn-budget planner that treats Gladion like an ordinary discarded Supporter loses the physical Prize state needed by later Prize manipulation.

This wrapper keeps both constraints without duplicating the underlying Gladion kernel.

## Limits

The wrapper assumes the caller has already selected a legal face-down Prize position using the information available to the actor.

It does not itself model:

- how the player learned Prize identities;
- observer beliefs about the selected card;
- strategic choice among several Prize positions;
- later ordinary Prize-taking.

Those remain separate information and policy layers.

## Next useful work

Use this transaction at the end of the Raichu target-Prized Computer Search continuation. That closes the full physical chain from Quick Ball and Dark Asset through K1 inference to literal singleton Prize recovery.
