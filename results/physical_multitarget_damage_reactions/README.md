# Physical copy attacks with multiple damage recipients

## Question

Can one copied attack body damage multiple opponent Pokémon while preserving
each damage recipient's exact identity for post-damage reactions?

**Yes, for distinct targets in the modeled subset.** This extends the existing
single-target copied-attack physical transition.

Implementation: `tools/attack_copy_physical_ko_bridge.py`,
`tools/physical_copy_damage_reaction_bridge.py`, and
`tools/physical_damage_reaction_sources.py`.

Regression: `results/physical_multitarget_damage_reactions/reproduce.py`.

## Representation

A `PhysicalBoardEventProgram` retains one primary damage target and may
supply additional target/context pairs. The physical copy replay emits an
ordered `PhysicalDamageRecord` for each target. Each record contains:

- the named copied-body event;
- its target index inside that event;
- the physically damaged Pokémon ID;
- the final six-step `DamageResult`.

Existing `damage_results` and `damage_targets` fields remain available for
compatibility, while the new typed records are authoritative for reaction
matching. If the caller requests a target that has no unique damage record
in the body, the reaction adapter rejects the ambiguous attribution.

Effect-based counter placements remain a distinct, later phase.

## Card-text witness

The source attack is Electivire ex `sv10-69` **Dual Bolt**, which deals
50 damage to two opponent Pokémon without applying Weakness and Resistance
on Benched Pokémon. Haughty Order copies the attack from the revealed
opponent Pokémon in the regression fixture.

The defender's Active and Benched Pokémon each physically carry a
Spiky Energy. The resulting board damage is 50 to each; the 40-HP Bench
target is Knocked Out, while the 120-HP Active survives.

The source-eligibility adapter returns:

- one two-counter Spiky Energy reaction from the damaged Active;
- zero reactions from the damaged Bench Pokémon, despite its Spiky Energy.

The attacking Active had 80 damage of 100 HP, so the two reflected
counters cause its Knock Out. The resulting cross-player batches contain
the attacker's Active and the defender's Bench Pokémon. The defender's
Active keeps its Spiky Energy attachment, while its knocked-out Bench
Pokémon and attached Spiky Energy go to discard. Physical class totals
are conserved and the attacker promotes its surviving Bench Pokémon.

## Safety boundary

A second regression creates two separate damage records for the same
Pokémon under one event name. The current source and reaction adapters
refuse to arbitrarily pick one. Any future same-target multi-hit handler
must carry an occurrence/index choice and enforce the appropriate
trigger multiplicity. The current model has a unique target-site rule,
rather than a general engine for all multi-hit attacks.

## Rules and limitations

The rulebook's A-01 and E-03 order damage before post-damage reactions
and the final Knock Out phase. Its B-08 treats damage to selected Bench
Pokémon as ordinary attack damage with the stated Weakness/Resistance
exception. Spiky Energy specifically requires its holder to be Active
and damaged by an opponent's Pokémon attack.

This is a semantic composition regression. It relies on an upstream
executor supplying the eligible physical targets, damage contexts, and
the fact that the attack comes from an opposing Pokémon. It does not
discover targets from free-form text or implement full simultaneous
post-damage reaction ordering.
