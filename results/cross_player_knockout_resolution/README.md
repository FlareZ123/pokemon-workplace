# Cross-player Knock Out promotion order

## Question

How should a state engine represent the promotion decisions after both players'
Active Pokémon are Knocked Out at the same time?

Implementation: `tools/cross_player_knockout_resolution.py`  
Regression: `results/cross_player_knockout_resolution/reproduce.py`

## Rule-derived ordering

The Advanced Player's Rulebook states that if both players' Active Pokémon are
Knocked Out at the same time, the player whose turn would be next promotes a new
Active Pokémon first.

This is an information-order rule as well as a board-state rule. The second
player can observe the first promotion before committing their own choice.

## Representation

`CrossPlayerKnockOutContext` holds one already-prepared Knock Out batch for
each player, the identity of the player whose turn would be next, and any
promotion choices already committed.

`promotion_order()` includes only players whose Active Pokémon belongs to the
Knock Out batch and who still have a surviving Pokémon available.

When both players need to promote, the next player is first.

`choose_promotion()` records exactly one legal decision at a time. It rejects:

- a promotion by the player who is not next in the required order;
- a Pokémon from the opponent's board;
- a Pokémon that is itself in the Knock Out batch.

Only after all required promotions are committed can
`resolve_cross_player_knock_out()` dispose both batches through the existing
conservation layer.

## Regression

Both players start with one Active and one Benched Pokémon. Both Active Pokémon
are prepared as Knocked Out simultaneously. Player B is declared the player
whose turn would be next.

The model derives promotion order:

`B -> A`

Player A attempting to choose first is rejected. After B chooses its surviving
Bench Pokémon, A chooses its own survivor. Resolution then:

- discards each Knocked Out Active physical card;
- promotes the chosen survivor on each side;
- preserves the surviving physical card bindings;
- conserves each player's independent card-class totals.

## Finding

A simultaneous board event can still contain sequential decisions.

Collapsing both promotions into an unordered pair loses a real information
boundary. A future policy model should therefore expose the first promotion
before requesting or evaluating the second player's action.

## Scope

The adapter assumes both players' Knock Out batches and the identity of the next
player are already known.

It does not model:

- how the next player is determined across attack versus Pokémon Checkup timing;
- Prize taking;
- win/loss resolution;
- card effects triggered by seeing or making a promotion;
- opponent-hidden information beyond the ordering of visible choices.
