# Cross-player simultaneous Active zone-exit resolution

## Question

How should a state engine resolve an effect that removes both players' Active
Pokémon at the same time, then requires sequential replacement-Active choices?

Expanded-legal Spidops `sv2-18` supplies a concrete witness. Its Entangling
Trap attack says:

`Shuffle each player's Active Pokémon and all attached cards into their deck. (You choose a new Active Pokémon first.)`

Implementation: `tools/cross_player_zone_exit_resolution.py`  
Regression: `results/cross_player_zone_exit_resolution/reproduce.py`

## Why Knock Out promotion ordering is insufficient

The existing Knock Out result derives its two-player order from the rulebook:
when both Active Pokémon are Knocked Out at the same time, the player whose turn
would be next promotes first.

Entangling Trap has a different ordering authority. The card text explicitly
gives the attacking player the first replacement choice.

Both mechanics create a temporary state with no Active on either side, while the
decision order is different. A generic simulator therefore cannot derive
replacement order only from the final board geometry.

## Physical transition

The adapter reuses:

- `StackBoardMaterialState` as the conserved physical state;
- `stack_zone_exit_conservation.leave_play_before_promotion()` to remove each
  Active object and route its complete physical evolution stack plus attachments;
- `PromotionPendingState` to represent surviving former Bench Pokémon while no
  replacement Active has been chosen.

For Entangling Trap, both the Pokémon stack and attachments use destination
`deck`.

The attacker regression uses an evolved Tarountula -> Spidops stack with a
physical Grass Energy attached. Both Pokémon cards and the Energy move into the
deck before a replacement Active is selected.

## Simultaneity boundary

`prepare_simultaneous_active_exit()` removes both current Active objects before
either player chooses a replacement.

This prevents a sequential engine from creating an intermediate state where one
player has already promoted while the other player's old Active is still
present.

After the exits, both players can simultaneously have:

- surviving former Bench Pokémon;
- no Active Pokémon;
- conserved physical card ledgers.

That state uses the same promotion-pending representation developed for the
post-Knock-Out Prize window, while the phase protocol is different.

## Effect-defined choice order

`CrossPlayerZoneExitContext.first_player_id` records the authority supplied by
the resolving effect.

When both sides need a replacement:

1. the effect-designated first player chooses;
2. the first choice becomes visible in the context;
3. the other player chooses.

The regression sets Player A as the attacker. Player B is rejected when it tries
to choose first. After A commits a replacement, B can observe A's new Active and
then commit its own choice.

For Entangling Trap the order is therefore:

`attacking player -> other player`

This differs from the simultaneous-Knock-Out rule:

`player whose turn would be next -> other player`

The difference is strategically relevant whenever the second choice can respond
to the first visible replacement.

## Terminal-state gate

A simultaneous exit can also leave a player with no Pokémon in play.

The adapter therefore begins in an `AFTER_EXIT` stage. An external game-state
resolver must decide whether play continues before promotion opens.

`advance_after_exit(..., game_continues=False)` enters `TERMINAL` and blocks
replacement choices.

This preserves the repository's broader phase-separation principle: a state
transition should not silently perform a later decision when an intervening
terminal condition may already have ended the game.

## Regression coverage

The deterministic regression validates:

- simultaneous removal of both Active objects;
- complete Tarountula -> Spidops stack routing to deck;
- attached Grass Energy routing to deck;
- preservation of both players' surviving Bench objects;
- no replacement choice before the post-exit gate opens;
- attacker-first promotion ordering;
- rejection of an out-of-order opponent choice;
- visibility of the first committed promotion before the second;
- final ordinary-board reconstruction after both choices;
- per-player physical-card conservation;
- a terminal branch where one player has no surviving Pokémon.

## Finding

Replacement-Active ordering is a transition-specific authority.

The same visible condition, both players temporarily lacking an Active, can
require different sequential decision protocols depending on why the Active
Pokémon left play.

A larger match engine should therefore carry the ordering source through the
transition rather than infer it from board geometry alone.

## Scope

The module receives already-resolved destinations and an explicit
`first_player_id`.

It does not yet compile the parenthetical ordering instruction from card text,
evaluate attack legality, or determine the terminal game result itself.

The next useful compiler seam is the small family of effects that explicitly
specify replacement-choice order, including Entangling Trap and related
simultaneous Active-removal wording.

## Validation

Run:

`python results/cross_player_zone_exit_resolution/reproduce.py`
