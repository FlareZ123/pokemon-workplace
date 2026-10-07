# Physical target binding for Defending-Pokémon attack restrictions

## Question

Time Freeze and Cross Slicer create restrictions that refer to the Defending
Pokémon. The earlier source-scoped temporal layer remembered the player and turn
window, while target identity remained a caller-supplied relation label. That
cannot by itself remove the effect when the affected Pokémon moves to the Bench
or evolves.

Implementation: `tools/target_bound_attack_restrictions.py`

Regression: `results/target_bound_attack_restrictions/reproduce.py`

## Rules basis

The Advanced Player's Rulebook describes attack-applied restrictions on the
Defending Pokémon as effects tied to that Pokémon and states for the explicit
attack/retreat families that the effect disappears when the Pokémon moves to the
Bench, leaves play, evolves, or devolves. The ordinary rulebook defines the
Defending Pokémon as the Pokémon that receives the attack. These mechanics make
physical target identity and transition history relevant.

## Representation

A `TargetBoundAttackRestrictionWindow` combines the existing player-relative
turn window with:

- the physical board-object ID of the Pokémon that received the attack;
- its card name at application time;
- a monotone `target_effect_live` flag.

The binding is created from the opponent's current Active Pokémon at attack
resolution. `advance_target_binding` is called at each board mutation. It
permanently clears the target effect if that object leaves the Active Spot,
leaves play, evolves, or devolves. A later return to the Active Spot does not
restore the old attack effect.

Action evaluation receives the actual target object ID. It derives the
`defending_pokemon` relation internally only when that target is the bound
object, removing the need for the caller to assert that semantic relation.

## Regression witnesses

Time Freeze blocks evolution of the original Defending Pokémon while leaving a
different target legal. Switching the affected Pokémon to the Bench clears the
effect, and switching the same physical object back Active does not resurrect
it. Evolving the affected Active Pokémon also clears it.

Cross Slicer blocks Energy from hand only when the attachment target is the
bound Defending Pokémon. Attachment to another Pokémon remains legal.

## Finding

Target-scoped attack locks need two owners at once: a player-relative duration
window and a physical target-effect lifetime. A turn window alone is too coarse.

This distinction should be reused for other attack effects referring to the
Defending Pokémon. Any simulator that skips intermediate board transitions
cannot reconstruct whether such an effect was cleared by a switch-out-and-back
sequence, so the target binding must advance at each mutation boundary.
