# Copied attack damage and the Knock Out phase barrier

## Question

When a copied attack body deals damage or places damage counters, can its pending
extra-turn or ordinary turn-boundary directive be handed to the turn scheduler
as soon as nested copy resolution returns?

No. End-of-attack Knock Out processing is an intervening phase.

Implementation: `tools/attack_copy_damage_bridge.py`  
Regression: `results/attack_copy_damage_bridge/reproduce.py`

## Rule-derived ordering

The Advanced Player's Rulebook resolves an attack through damage, effects outside
damage, damage-triggered effects, and then a Knock Out check. The Knock Out
process resolves its trigger window, discards the Knocked Out Pokémon and
attached cards, takes Prize cards, and handles replacement Active choices.

The existing attack-copy work separately establishes that an inner copied body
can create a pending turn-boundary consequence while outer attack text still
has to resume.

Those two findings compose into this order:

`copy prelude -> selected body -> outer continuation -> Knock Out phase -> turn boundary`

A copied extra-turn effect therefore cannot skip over a zero-HP Active or start
the extra turn before the Knock Out phase has been resolved.

## Adapter

The copy kernel already records its executable event stream in exact nested
order. The new bridge replays selected event labels against the existing damage
and effect-counter kernels.

`BoardEventProgram` supplies the typed board consequence for one event:

- damage target;
- ordered `DamageContext`;
- any effect-based damage-counter placements.

`replay_copy_attack_board()` walks `resolution.state.events` in order, applies
those board programs, and performs one shared HP threshold check only after the
full declared-attack event stream has completed.

The bridge does not dispose Knocked Out Pokémon. Instead,
`close_copy_attack_if_no_knockouts()` refuses to hand the attack to the turn
scheduler when any Knock Out candidate remains. That makes the missing phase
boundary explicit rather than silently starting an extra turn from an
unresolved board.

## Timeless-GX witness

The regression uses the existing executable Haughty Order -> Timeless-GX copy
line.

The copy event order is:

`reveal top 10 -> Timeless-GX body -> shuffle revealed cards`

Against a 150 HP Active target, the body places 150 damage and the final replay
reports that Active as a Knock Out candidate. The extra-turn directive is
already pending inside the copy resolution, but the new closure gate rejects
turn scheduling until the downstream Knock Out phase is handled.

Against a 200 HP Active target, the same 150 damage produces no Knock Out. The
closure gate then allows the existing canonical scheduler to consume the
declared attack and start Player 1's extra turn while skipping Pokémon Checkup.

This distinguishes two states that the copy-only scheduler previously could not
tell apart.

## Phantom Dive witness

A second regression uses Haughty Order -> Phantom Dive against:

- a 200 HP Active;
- a 60 HP Benched Pokémon.

The copied body applies 200 normal damage to the Active and six effect counters
to the Bench target. Both reach the Knock Out threshold.

The event trace still records the outer `shuffle revealed cards` continuation
after those board changes. Only after that continuation does the bridge expose
the two simultaneous Knock Out candidates. Turn closure is blocked.

This preserves three separate facts at once:

1. the selected body can change board HP state;
2. outer copy text still resumes after the body;
3. simultaneous Knock Outs belong to the end-of-attack phase before turn
   scheduling.

## Architectural implication

Attack-copy execution, damage, Knock Out processing, and turn scheduling are
distinct state-machine layers with an explicit order.

A nested copy resolver can safely accumulate a future turn-boundary directive,
but the scheduler should consume it only after the declared attack has completed
its board effects and the Knock Out phase has cleared.

This is the same general pattern seen elsewhere in the repository: a pending
future consequence is not permission to bypass intervening mandatory state
transitions.

## Limits

The bridge currently receives event-to-board programs explicitly. It does not
compile attack damage or effect-counter text automatically.

It also does not yet execute:

- phase-6 effects that activate when a Pokémon is damaged;
- Knock Out trigger effects;
- physical batch disposal;
- Prize taking;
- promotion;
- win/loss resolution.

Those remain downstream of the new barrier. The existing
`damage_board_bridge`, `simultaneous_knockout_conservation`, and
`knockout_phase_resolution` results provide the next mechanical layers for a
future full end-of-attack pipeline.
