# Bench-capacity restoration has bootstrap thresholds and ordering constraints

## Question

After an opponent restricts Bench capacity, are all Stadium-removal or expansion routes equally capable of reopening space?

No. The route can depend on the very Bench slack it is intended to create, and conditional expansion can make entry order decisive.

Implementation: `tools/bench_capacity_restoration_bootstrap.py`  
Regression: `results/bench_capacity_restoration_bootstrap/reproduce.py`

## Concrete legal effects

The model uses legal paper-Expanded effects from the bundled card pool:

- **Collapsed Stadium** `swsh9-137` / `swsh11-215`: both players are restricted to four Benched Pokémon.
- **Pumpkaboo** `swsh7-76` / Pumpkin Pit: when played from hand onto the Bench, it may discard a Stadium in play.
- **Chien-Pao** `sv8-56` / Snow Sink has the same relevant hand-to-Bench Stadium-discard geometry.
- **Sky Field** `xy6-89`: both players can have eight Benched Pokémon.
- **Area Zero Underdepths** `sv7-131`: a player with a Tera Pokémon in play can have up to eight Benched Pokémon.

## Finding 1: a release effect can require the resource it creates

Suppose Collapsed Stadium is in play and the affected player already has four Benched Pokémon.

Pumpkin Pit cannot restore capacity from that state. Pumpkaboo must first be legally played onto the Bench, but occupancy already equals capacity. Its Stadium-discard Ability therefore never reaches its trigger condition.

With only three Benched Pokémon, the line becomes legal:

`Bench Pumpkaboo -> Pumpkin Pit discards Collapsed Stadium -> capacity returns to 5 -> Bench required entrant`

One unit of pre-existing slack is therefore the bootstrap threshold for this release family.

This is a useful connector-realism pattern: a transition that creates resource `R` may itself require one unit of `R` before the transition can begin.

## Finding 2: direct Stadium replacement uses a different resource channel

From the same full four-of-four restricted Bench, Sky Field can be played directly. Stadium play does not require Bench slack.

The line is:

`play Sky Field -> capacity 8 -> Bench required entrant`

Direct Stadium replacement therefore reaches states that Bench-triggered Stadium removal cannot. Its payment is the Stadium play window rather than Bench capacity.

A graph that gives both cards an undifferentiated “remove/replace Stadium” edge loses this distinction.

## Finding 3: Area Zero creates an order-sensitive bootstrap

Start under Collapsed Stadium with four Benched Pokémon and no Tera Pokémon in play.

Playing Area Zero replaces Collapsed Stadium. Because the Tera condition is initially false, the player returns only to ordinary capacity five. That creates exactly one slot.

Two desired entrants are available: one Tera Pokémon and one ordinary Pokémon.

If the Tera enters first:

1. play Area Zero, capacity becomes 5;
2. Bench Tera entrant into the only open slot;
3. Area Zero's condition becomes true, capacity becomes 8;
4. Bench ordinary entrant.

Final occupancy is six under capacity eight.

If the ordinary Pokémon enters first:

1. play Area Zero, capacity becomes 5;
2. Bench ordinary entrant into the only open slot;
3. occupancy becomes five while the Tera condition is still false;
4. the Tera cannot be Benched, so the eight-slot expansion never activates.

The same two accessible cards and same Stadium produce success or failure solely from sequencing.

## Strategic interpretation

Capacity restoration should preserve:

- the action channel used to remove or replace the restriction;
- any resource needed before the restorative effect can trigger;
- current occupancy and capacity;
- conditional capacity sources;
- the exact order in which entrants change those conditions.

This is another case where theoretical access is weaker than executable access. “Can remove the Stadium” is insufficient if the remover requires an unavailable Bench slot. “Has Area Zero and a Tera” is insufficient if a different entrant consumes the only bridge slot first.

## Evidence class

The named card effects and legalities are direct card-pool facts. The plans are deterministic bounded state-transition results using the repository's action-budget and planner infrastructure.

## Limitations

The model isolates one Stadium and Bench sequence. It does not model search access, Prize cards, opponent interaction during the same turn, Ability lock on Pumpkin Pit/Snow Sink, Stadium lock, or reasons the player might strategically prefer a different entry order.

The Area Zero transition assumes the continuous capacity condition updates immediately when the Tera enters play, consistent with the card's persistent wording.

## Relation to prior work

`interturn_bench_slack_exposure` showed that opponent contraction can destroy reserved future slack. This result adds recoverability. It also extends the earlier transient Stadium-remover observations in `bench_capacity_geometry` by identifying the exact zero-slack deadlock and contrasting it with direct Stadium replacement.

## Next useful work

A natural extension is to turn these deterministic states into an access model: given counts of restorative Stadiums, Bench-triggered removers, and Tera starters, compute the probability that a restricted opening state can actually unlock its Bench under Prize and hand uncertainty.
