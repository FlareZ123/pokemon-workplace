# Materialization-to-board binding

## Question

Does the general exchangeable-to-instance identity ledger bind correctly to the live per-Pokémon board model after physical instance identity was separated from database print identity?

Regression: `results/materialization_board_binding/reproduce.py`

## Result

Yes, after the board-binding helper was updated to use physical `instance_id`.

The regression begins with two exchangeable Double Colorless Energy copies in hand. It materializes them as `dce-a` and `dce-b`, attaches both ledger instances to one board object, and constructs the corresponding board Energy attachments.

Both physical copies deliberately share the same database print ID. The binding validator succeeds because topology is keyed by physical instance ID.

The ledger's conservation assertion also confirms that two exchangeable copies before materialization remain exactly two total copies afterward.

A board using an unrelated physical instance ID is rejected.

## Why this matters

The repository now has distinct roles for:

- database print identity;
- exchangeable card-class multiplicity;
- physical instance identity;
- Pokémon board-object identity.

Conflating any two of these can create false uniqueness, duplicate cards, or attachment bindings that cannot be reconciled with the zone model.

This regression is also a cross-agent integration check between `identity_materialization.py` and `board_object_kernel.py`.

## Scope

The test covers Energy attachments. Tool attachments use the same binding helper and should receive their own concrete regression when Tool materialization is added to a transition model.
