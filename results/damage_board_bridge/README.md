# Attack damage, effect counters, and KO candidate bridge

## Question

Can normal attack damage and effect-placed damage counters feed one shared Knock Out check while preserving their different rule semantics?

Yes. This result composes the ordered damage-calculation kernel with the existing board-object damage-counter state and delays Knock Out detection until the attack's final KO check.

Implementation: `tools/damage_board_bridge.py`  
Regression: `results/damage_board_bridge/reproduce.py`

## Rule structure preserved

The Advanced Player's Rulebook resolves an attack in distinct phases:

1. damage calculation;
2. effects outside damage;
3. effects that activate when a Pokemon is damaged;
4. checking for Knock Outs.

It also states that placing damage counters with an attack effect happens in the effects-outside-damage phase and is not damage. Weakness, Resistance, and damage-related effects therefore do not modify those counters. A Pokemon immune to effects of attacks can still be selected for such an effect, while the counters are not placed.

The bridge keeps those concepts separate:

- `apply_attack_damage(...)` invokes the ordered damage kernel and converts final damage into 10-damage counters;
- `apply_effect_counter_placement(...)` places effect counters directly and has its own effect-immunity gate;
- `resolve_attack_damage_phase(...)` performs the shared KO threshold check only after both kinds of state change.

## Phantom Dive witness

Dragapult ex `sv6-130` is Expanded-legal in the bundled database. Its Phantom Dive attack has 200 damage plus:

`Put 6 damage counters on your opponent's Benched Pokémon in any way you like.`

The regression uses a 200-HP Active target and a 60-HP Benched target.

In the baseline state:

- Phantom Dive places 20 damage counters on the Active through damage calculation;
- its effect places six counters on the Bench target;
- the final KO check emits both object IDs together.

This is a compact mechanical witness for a double-KO attack.

## Independent defensive axes

The same regression distinguishes two defenses that an untyped attack model could conflate.

If the Benched target prevents effects of attacks, the six effect counters are not placed, while the 200 normal damage still KOs the Active.

If the Active target prevents all damage, the Active takes zero while the six effect counters still reach the Bench target.

If the attack ignores effects on the Active target, the damage-prevention effect is bypassed, while the independently modeled Bench counter effect proceeds normally.

So "prevent damage" and "prevent effects" are separate state axes with different targets and different consequences.

## Why KO detection is delayed

A target can reach zero remaining HP during damage calculation while another Pokemon reaches zero remaining HP during a later attack effect. The rulebook's attack sequence checks Knock Outs after those effects.

A simulator that immediately disposes the first target as soon as damage is placed can therefore lose simultaneous-KO structure and feed the wrong state into Knock Out triggers, Prize taking, or promotion order.

The bridge returns KO candidates without disposing them. Existing simultaneous Knock Out and Prize-phase infrastructure can own the later phase boundary.

## Limits

The bridge receives HP as an explicit per-object mapping because `BoardPokemon` currently stores damage counters but does not yet own printed/effective HP.

It does not yet model:

- HP-changing effects;
- allocation of "in any way you like" counters across several targets;
- damage-triggered effects between damage/effects and the KO check;
- attack-effect immunity derivation from live Ability/Tool/Stadium state;
- disposal, Prize awards, or promotion.

Those boundaries should remain separate. A particularly useful next step is an exact counter allocator for attacks such as Phantom Dive, so a tactical planner can optimize KO outcomes across damaged Benched targets instead of treating six counters as one fixed target.
