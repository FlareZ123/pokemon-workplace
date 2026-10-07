# Lock-gated physical evolution transaction

## Question

Can ordinary evolution consume the exact same live lock state used for other
actions and then advance every state owner that evolution changes?

Implementation: `tools/lock_gated_evolution_transaction.py`

Regression: `results/lock_gated_evolution_transaction/reproduce.py`

## Transaction order

The transaction performs five stages:

1. verify that the physical `StackCard` and exact card-action metadata refer to
   the same print;
2. query board-derived action permission for a Pokémon played from hand in
   `evolve` mode, including continuous restrictions, ordinary temporal windows,
   and physically target-bound attack windows;
3. if permitted, execute the existing ledger-conserving ordinary evolution;
4. advance any Defending-Pokémon target bindings on the evolving player's board,
   so evolution permanently clears those attack effects;
5. advance the causal Ability-lock state from the resulting exact top-print
   board.

The existing evolution-stack module remains the owner of physical cards,
attachments, damage, and same-turn evolution eligibility. The lock layers own
permission and suppression.

## Regression witnesses

A normal evolution succeeds and updates the board object's exact print ID.

A Dialga Time Freeze window bound to the evolving object blocks that evolution
before the physical stack or ledger changes.

A Tool-attached Trubbish can evolve into the exact Garbodor print carrying
Garbotoxin. The transaction preserves the Tool, advances causal Ability-lock
state, and the new Garbotoxin suppression disables an opposing Vileplume's
Irritating Pollen. A subsequent Item action that was illegal before the
evolution becomes legal after the transaction.

## Finding

Evolution is a state-boundary event for both action permission and continuous
Ability topology. Evaluating only the pre-evolution legality or only the physical
stack transition is insufficient.

Exact top-print identity is essential here: without it, the post-evolution
Ability graph can retain the Basic's nonexistent effects or miss the newly
evolved source.
