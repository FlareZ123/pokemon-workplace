# Board attachment conservation

## Question

Can the exchangeable-copy identity ledger and per-Pokémon board kernel share one
conservation law for Pokémon Tools across play, evolution, and Knock Out?

Implementation: `tools/board_attachment_conservation.py`  
Regression: `results/board_attachment_conservation/reproduce.py`

## Rule-derived contract

The Advanced Player's Rulebook requires one Tool at a time on a Pokémon, keeps
that Tool attached through evolution and movement, and discards the Pokémon plus
all attached cards on Knock Out.

## Result

`BoardMaterialState` binds `IdentityLedger` to `BoardState` and validates
that every materialized attached instance matches board topology.

The regression shows:

1. a Tool moves from an exchangeable hand count to a physical attached instance;
2. a second Tool on the same Pokémon is rejected;
3. evolution preserves the exact Tool instance and does not change copy totals;
4. Knock Out removes the complete board object, moves the Tool to discard, and
   dematerializes it into the exchangeable discard count;
5. the same conservation path works for a terminal lone-Active Knock Out.

`board_object_kernel.knock_out()` supplies the mechanical removal transition
and returns the full removed Pokémon object, including Energy and Tool
attachments. If a Bench remains, a promotion is required. If no Pokémon remain,
the next board state is `None`.

## Implication

The materialization boundary is explicit:

`hand count -> physical attached instance -> discard count`

Evolution is topology-preserving inside that interval. Knock Out is a natural
dematerialization boundary for the attachment in this model.

## Limits

The Pokémon card and its full evolution stack are still not conserved by this
adapter because `BoardPokemon` stores only the current top-card name.
Devolution, simultaneous Knock Outs, Knock Out triggers, Prize taking, win/loss,
and card-specific Tool removal remain outside scope.
