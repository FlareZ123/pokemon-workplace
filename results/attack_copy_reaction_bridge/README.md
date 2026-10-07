# Copied attacks, damage reactions, and the final Knock Out barrier

## Question

Can a copied attack that schedules an extra turn reach the turn scheduler as
soon as its damage and outer continuation are complete?

Only if the post-damage reaction phase also leaves no Knock Outs pending.

Implementation: `tools/attack_copy_reaction_bridge.py`  
Regression: `results/attack_copy_reaction_bridge/reproduce.py`

## Why another phase is required

The Advanced Player's Rulebook places effects that activate when a Pokémon is
damaged after attack damage and outside-damage effects, but before the final
Knock Out check.

The repository's damage-reaction kernel supplies concrete witnesses:

- Strong Bash-like effects can mirror the final damage back to the attacker as
  damage counters;
- Spiky Energy-like effects can place fixed counters on the attacker;
- those reactions still resolve even when the damaged defender will itself be
  Knocked Out.

The copy pipeline therefore needs this order:

`copy body and outer continuation -> damage reactions -> Knock Out phase -> turn boundary`

## Adapter

`resolve_copy_damage_reactions()` consumes the completed board-event replay
from `attack_copy_damage_bridge`, selects the unique damage result associated
with the executed copied-body event, and applies the existing step-6 reaction
kernel.

This returns Knock Out candidates on both sides of the game.

`close_copy_attack_after_reactions_if_no_knockouts()` then refuses to hand the
declared attack to the turn scheduler if either side has a pending Knock Out.

The adapter is intentionally narrow. It composes existing semantic layers rather
than reimplementing damage or reaction rules.

## Timeless-GX plus reflected damage witness

The regression uses Haughty Order -> Timeless-GX.

Timeless-GX contributes:

- 150 damage;
- a pending extra-turn directive.

The defending Pokémon is modeled with a live Strong Bash-like reaction from the
previous turn.

In the first case:

- the defender has 130 HP;
- the Haughty Order attacker has 150 HP;
- Timeless-GX deals 150 to the defender;
- the outer Haughty Order cleanup finishes;
- the defender's reaction mirrors 15 damage counters onto the attacker;
- both Pokémon are now Knock Out candidates.

The extra-turn directive already exists, but turn closure is rejected. The KO
phase must resolve both sides before any extra turn can begin.

This is a concrete cross-layer counterexample to the shortcut:

`copied extra-turn body resolved -> start extra turn`

The missing reaction and Knock Out phases can materially change the board before
that handoff.

## Surviving control

A second case uses:

- a 200 HP defender;
- a 160 HP attacker.

The same 150 damage triggers the same 15 reflected counters, but both Pokémon
survive. With no Knock Out candidates remaining, the existing canonical turn
scheduler accepts the pending Timeless-GX directive and starts the same player's
extra turn while skipping Pokémon Checkup.

A prevented-damage control also verifies that zero final damage does not satisfy
the damaged-by-attack condition and therefore creates no reflected counters.

## Architectural implication

Turn-boundary effects are deferred consequences.

They can be discovered deep inside copied-body execution, but they should not be
consumed until every mandatory attack-resolution phase that can still mutate the
board has completed.

For the modeled subset, that gives:

1. nested copy selection and body execution;
2. outer copy continuation;
3. damage and effects outside damage;
4. damaged-by-attack reactions;
5. final Knock Out candidate detection and downstream KO resolution;
6. turn closure and any pending extra-turn scheduling.

This preserves the distinction between attack semantics, reaction semantics,
Knock Out state, and turn scheduling.

## Limits

The adapter currently requires the caller to provide the applicable reaction
objects. It does not derive Strong Bash, Spiky Energy, or other reaction
eligibility from live board attachments and prior-turn effects.

It also stops at Knock Out candidates. Physical disposal, KO-trigger routing,
Prize taking, promotion, and win/loss resolution remain owned by the existing
Knock Out phase infrastructure.
