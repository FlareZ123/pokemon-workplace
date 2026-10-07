# Copied extra-turn effects and the declared-attack boundary

## Question

If a copied attack body creates an extra turn, when should that scheduling effect reach the turn engine?

After the full declared attack resolution completes, including any outer text that resumes after the copied body.

Implementation: `tools/attack_copy_turn_boundary_bridge.py`  
Regression: `results/attack_copy_turn_boundary_bridge/reproduce.py`

## Concrete witness

Team Rocket's Persian ex **Haughty Order** has three semantic phases:

`reveal top 10 -> execute selected attack body -> shuffle revealed cards`

Dialga-GX **Timeless-GX** says to take another turn after the current one and skip the between-turns step.

If Haughty Order finds Timeless-GX, the extra-turn effect is created while the inner body is executing. The outer Haughty Order frame still has mandatory cleanup afterward. Starting the extra turn immediately from inside the copied body would therefore cut off unresolved outer attack text.

The copy kernel now represents Timeless-GX-like scheduling as a pending `TurnBoundaryEffect`. Nested resolution records that directive, returns through the outer frame, completes its post-copy continuation, and only then lets the bridge close the one declared attack action.

## Regression

The executable witness records this event order:

`reveal_top_10 -> take_another_turn -> shuffle_revealed`

Only after that sequence finishes does `close_declared_attack()` consume the canonical turn budget's single attack action.

The existing canonical turn scheduler then observes the pending extra-turn directive:

- Player 1 remains the current player;
- Player 1 receives a fresh turn-action budget;
- Pokémon Checkup is skipped at that boundary;
- Player 2's budget remains untouched.

A control case where Haughty Order copies an ordinary attack has no pending directive and hands the next turn to Player 2 with Pokémon Checkup occurring.

## Architectural implication

Attack-body effects and turn-boundary scheduling are different execution layers.

A copied body may request a future scheduling consequence, but the turn engine should apply it after the declared attack's execution stack has unwound. This preserves post-copy cleanup and ensures nested copied bodies still consume one attack action at the turn level.

The representation also keeps the existing identity distinction intact: Haughty Order remains the declared attack even though Timeless-GX supplies the extra-turn body effect.

## Limitations

This bridge models the scheduling consequence after attack resolution. It does not yet integrate Knock Out processing, game-resolution checks, or other end-of-attack effects that may occur between the copied body and the turn handoff.

The mapping from Timeless-GX's historical wording "skip the between-turns step" to the scheduler's `skip_pokemon_checkup` flag follows the repository's current turn-boundary abstraction. A future full engine should preserve any finer timing distinctions required by authoritative rulings.
