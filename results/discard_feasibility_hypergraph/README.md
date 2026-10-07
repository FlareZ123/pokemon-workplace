# Discard feasibility hypergraph

## Motivation

Discard costs are joint actions. Ultra Ball, Computer Search, Secret Box,
Guzma & Hala, and similar effects ask for a set of cards at once.

Per-card discardability scores are useful summaries, yet they can lose the
correlation structure that determines whether an acceptable payment still
exists after the game state changes.

This result formalizes the payment surface as a uniform hypergraph:

- vertices are cards currently available to discard;
- each hyperedge is one jointly acceptable payment;
- the hyperedge size is the discard cost;
- protected or UDP cards delete every incident hyperedge;
- the action remains realistic exactly when at least one hyperedge survives.

## Counterexample

Two six-card discard families are constructed over A, B, C, D, E, F.

Cycle family:

AB, BC, CD, DE, EF, FA

Two-triangle family:

AB, BC, CA, DE, EF, FD

They have the same basic scalar summaries:

- six cards;
- discard cost two;
- six feasible payments;
- every card belongs to two of the six payments, so normalized participation is
  1/3 for every card;
- no card belongs to every feasible payment.

Their response to later protection differs.

If A, C, and E become protected, every cycle payment is blocked. The
two-triangle family still has DF available.

The minimum number of protected cards needed to block every payment is three
for the cycle and four for the two-triangle family.

Across all 20 ways to protect exactly three of the six cards:

- cycle family remains payable in 18/20 states = 90%;
- two-triangle family remains payable in 20/20 states = 100%.

The two systems therefore have equal card marginals and equal option count at
the initial state while possessing different future AMR under UDP changes.

## Implication for DCI

A scalar DCI can remain useful as a local heuristic. Per-card scores alone do
not encode which cards are jointly substitutable.

A stronger representation can keep a feasible discard family underneath the
scalar summaries. Useful derived quantities include:

- current payment count;
- forced-card intersection;
- minimum protection cut;
- robustness to protecting k cards;
- minimum scarcity or strategic cost over surviving payments;
- continuation value of the best surviving payment.

The Aichi Vileplume starting-Active research gives a concrete deck-level
instance. Non-Jirachi Active choices preserve the same immediate endpoints
while changing Guzma & Hala's feasible payment family and scarcity profile.

## Reproduction

- tool: tools/discard_feasibility_hypergraph.py
- workflow: .github/workflows/validate-discard-feasibility-hypergraph.yml
