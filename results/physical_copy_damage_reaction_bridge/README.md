# Physical copied-attack damage reactions and simultaneous Knock Outs

## Question

Can a copied attack's post-damage counter reactions resolve directly on each
player's conserved, stack-bearing board, before the simultaneous Knock Out phase?

**Yes, for reaction bodies that place damage counters on the attacking Active.**
The lightweight board-object reaction engine and the physical copied-attack
damage bridge previously stopped at separate representations.

Implementation: `tools/physical_copy_damage_reaction_bridge.py`  
Regression: `results/physical_copy_damage_reaction_bridge/reproduce.py`

## Mechanics and scope

The Advanced Player's Rulebook's attack order is damage, outside-damage
effects, effects activated upon damage, and then Knock Outs (A-01, E-03).
A defender can react **even if it is Knocked Out**. Both the defending
Pokémon's physical cards and the attacking Pokémon must remain in play
through that reaction.

The adapter accepts the completed physical replay's unique named damage
result. It applies the existing `DamageReaction` counter families (fixed,
mirrored final damage, and live-count scaled) to the attacking Active on its
own `StackBoardMaterialState`. Both physical ledgers remain unchanged.
After the reactions, it computes each side's Knock Out candidates. Separate
`PendingKnockOutBatch` objects retain the physical stacks and attached cards.

## Executable witness

The copied-attack trace is:

`Haughty Order -> Timeless-GX -> outer shuffle`

The 150-damage body hits a 130-HP defender carrying Spiky Energy. The
regression supplies two eligible post-damage reactions:

- Strong Bash-like reflection: 15 damage counters on the attacker.
- Spiky Energy-like reflection: 2 more damage counters.

The 170-HP attacking Active reaches 17 counters, and the defending Active
reaches 15. Both become simultaneous Knock Out candidates. The attacker's
Tool and the defender's Energy remain physically attached in the pending KO
window. The existing cross-player batch resolver then orders replacement
choices, disposes both stacks and attachments, and preserves every card-class
total.

The regression also checks prevented damage. Its final damage is zero, so no
reaction triggers and neither side enters the KO phase. With a 160-HP
attacker and only the 15-counter reflection, only the defender is Knocked Out.

## Interpretation

This bridge closes the modeled gap between damage, reactions, and physical
Knock Out preparation. It lets later layers reuse unchanged physical card
identities to resolve triggered recovery, simultaneous disposal, Prize taking,
terminal checks, and promotion.

## Limits

Reaction eligibility is an explicit input. This adapter does not infer
the prior-turn Strong Bash status, Spiky Energy attachment eligibility, target
position, protection effects, or other card-specific gates. It currently
supports the three existing damage-counter reaction families; additional
bodies (Energy movement, Special Conditions, hand effects) require separate
effect handlers. The present test does not execute Prize-taking or terminal
game-resolution phases and should not be interpreted as full game simulation.
