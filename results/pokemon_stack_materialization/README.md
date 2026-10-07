# Pokémon stack materialization

## Question

Can exchangeable Pokémon-card copies become physical members of one persistent in-play evolution stack while preserving card counts and board identity?

Regression: `results/pokemon_stack_materialization/reproduce.py`

## Representation

The general identity ledger now supports two board relations:

- `attached_to` for cards in the `attached` zone, such as Energy and Tools;
- `board_object_id` for Pokémon cards in the `in_play` zone that belong to one persistent Pokémon object.

These relations are mutually exclusive. Off-board materialized instances have neither.

## Regression

The test begins with one exchangeable Bulbasaur and one exchangeable Ivysaur in hand.

Bulbasaur is materialized as `bulba-copy`, moved into play, and bound to persistent Pokémon object `pokemon-a`. The board stack contains that exact physical ID.

Ivysaur is then materialized as `ivy-copy` and ordinary evolution appends the same physical ID to the same board object's stack.

The binding validator confirms that the identity ledger and board stack agree exactly:

`bulba-copy -> pokemon-a`  
`ivy-copy -> pokemon-a`

The conservation assertion confirms that materializing and binding the cards does not change total copy counts.

A ledger carrying a different physical Ivysaur ID is rejected against the evolved board.

## Architectural implication

An in-play Pokémon is a board object that can own several physical Pokémon cards over time. Its Active or Bench position belongs to the board object. The component cards remain physical instances bound to that object.

This separation is useful for evolution, devolution, returning an evolved Pokémon to hand or deck, Knock Out discard, and effects that inspect previous Evolutions.

It also closes another gap between exchangeable multiplicity and board topology: Pokémon cards now have the same explicit materialization boundary already established for attached Energy.

## Scope

The regression covers ordinary Basic-to-Stage-1 evolution. It does not yet implement devolution, Rare Candy, direct placement of Evolution Pokémon, Knock Out disposal of a whole stack, or returning a full stack to hand/deck.
