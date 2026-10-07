# Copied extra turns after Knock Out and game resolution

## Question

If a copied attack creates a pending extra turn and the same attack also creates
a game-ending Knock Out, can the turn scheduler start that extra turn?

No. The Knock Out, Prize window, terminal check, and any required replacement
Active choices all precede turn-boundary scheduling.

Implementation: `tools/attack_copy_terminal_bridge.py`  
Regression: `results/attack_copy_terminal_bridge/reproduce.py`

## Phase order

Earlier attack-copy results establish that a copied Timeless-GX-like body can
record a future extra-turn consequence while the declared attack still has outer
text to finish.

The physical and game-resolution results add the remaining mandatory phases:

1. finish the declared attack and outer continuation;
2. resolve damage reactions;
3. identify the complete Knock Out set;
4. resolve Knock Out triggers and physical disposal;
5. take Prize cards and finish the E-31 before-hand Prize window;
6. evaluate Prize/no-Pokémon terminal conditions;
7. if the game continues, make every required replacement Active choice;
8. only then close the attack into the turn scheduler.

A pending extra turn is therefore a deferred consequence, not a terminal-state
override.

## Adapter

`close_copy_attack_after_game_resolution()` consumes the existing
`PrizeWindowResolution`.

If that resolution is terminal, it returns the game result and never calls the
turn scheduler.

If the game continues, it requires
`promotion_pending_conservation.finalize_promotions()` to succeed. An unresolved
replacement Active therefore also blocks the turn handoff.

Only a continuing, promotion-complete match reaches the existing
`close_declared_attack()` scheduler bridge.

## Regression

The executable copy line is Haughty Order -> Timeless-GX, so an extra-turn
directive is already pending.

### Last Pokémon Knock Out

Player 2 loses their only Pokémon to the attack. Player 1 still has a Pokémon
and has five Prize cards remaining, so the no-Pokémon condition alone ends the
game.

The post-Prize-window resolver returns Player 1 win / Player 2 loss. The
attack-copy terminal bridge preserves that terminal result and returns no turn
closure. Timeless-GX never starts an extra turn.

### Surviving Bench Pokémon

A control gives Player 2 one surviving Benched Pokémon.

The Prize/no-Pokémon resolver says the game continues, but the bridge still
refuses to schedule the extra turn while Player 2 has no Active selected.

After Player 2 promotes the survivor, the same bridge can finalize both physical
boards, close the declared attack, and feed Timeless-GX's pending directive to
the canonical turn scheduler. Player 1 then receives the extra turn and
Pokémon Checkup is skipped at that boundary.

## Finding

Game resolution and promotion are stronger phase barriers than turn-boundary
effects created by attack text.

For copied extra-turn attacks, an execution engine should preserve the directive
while later mandatory phases run, then discard it naturally when the game is
terminal or consume it only after the match is again in a valid continuing
board state.

## Prize-window note

This adapter deliberately starts from `PrizeWindowResolution`, rather than from
raw Prize counts immediately after disposal.

That matters because the repository's official Jirachi Prism Star witness shows
that an E-31 Prize effect can put a Pokémon into play before the no-Pokémon loss
condition is evaluated. A scheduler gate placed earlier than that window would
still be too early.

## Limits

The regression supplies remaining Prize counts after upstream Prize-taking
semantics. It does not choose physical Prize cards or compute Prize values.

The bridge also does not own Knock Out triggers, disposal, E-31 effects, or
promotion policy. It only establishes when a copied attack's pending turn
directive is allowed to leave those existing layers.
