# Stadium-removal channels: action class changes Bench-refresh realism

## Question

How many explicit Stadium-removal effects exist in legal paper Expanded, and which action classes can provide removal before a same-turn Bench refresh continues?

## Conservative census

`tools/stadium_removal_catalog.py` scans the legal Black & White-onward card pool using the repository legality overlay. It keeps effects that explicitly discard a Stadium or put a Stadium into the Lost Zone. It excludes ordinary Stadium persistence text, discard-from-hand costs, and Stadium cards themselves because playing a new Stadium already uses the general replacement rule.

Against the bundled snapshot, the scanner finds:

- **121** legal print-effect instances;
- **71** conservative effect-text variants;
- **66** unique card names.

Unique names by action class:

| Action class | Unique names |
| --- | ---: |
| Item | 6 |
| Supporter | 4 |
| Ability | 5 |
| Attack | 51 |

The six Item names are Blowtorch, Dangerous Drill, Field Blower, Lost Vacuum, Megaton Blower, and Paint Roller.

The four Supporters are Bonnie, Faba, Flannery, and Worker.

The five Ability sources are Chien-Pao, Gothitelle, Haxorus, Marshadow, and Pumpkaboo. Chien-Pao and Pumpkaboo are the two cataloged Ability names whose Stadium removal specifically requires playing the Pokémon from hand onto the Bench.

The remaining 51 names remove Stadiums through attacks.

## Timing is the dominant structural split

Every attack-based removal consumes the attack window and ends the turn. Those 51 names can remove a problematic Stadium for a later turn state while they cannot create additional same-turn Bench-entry capacity after the attack.

Items, Supporters, and already-established Abilities can remove a Stadium before the attack and leave a later Bench action possible, subject to their own costs and locks.

This makes the raw count misleading for Bench refresh. Most named removal sources live in the one timing class that cannot enable same-turn post-removal support chaining.

## Item channels

The six Item names are especially relevant because they preserve the Supporter window.

Their costs differ materially:

- Field Blower directly chooses Stadiums and Tools in play;
- Lost Vacuum requires putting another hand card into the Lost Zone;
- Dangerous Drill requires discarding a Darkness Pokémon from hand;
- Blowtorch requires discarding a Basic Fire Energy from hand;
- Megaton Blower is an ACE SPEC;
- Paint Roller discards a Stadium and then draws a card.

Item lock removes all six action edges at once.

## Supporter channels

Bonnie, Faba, Flannery, and Worker all consume the one ordinary Supporter play for the turn.

Their semantics differ. Worker directly draws three and discards a Stadium. Faba can put a Stadium into the Lost Zone. Flannery combines Stadium removal with opposing Special Energy removal. Bonnie has its own Stadium-presence condition and Zygarde-GX purpose.

For a Bench refresh, the opportunity cost is therefore a Supporter window that could otherwise be used for draw, gust, Prize rescue, or setup.

## Ability channels

The five Ability names divide further by activation geometry.

Pumpkaboo and Chien-Pao need a free Bench slot because their removal triggers when they are played from hand onto the Bench. This makes them self-gated from a full five-slot contracted board.

Marshadow's Resetting Hole requires Marshadow already to be on the Bench and discards itself after removing the Stadium. Gothitelle and Haxorus require their own evolved board presence.

An "Ability removal available" boolean therefore loses the most important board predicates.

## Relation to refresh lines

The generic Parallel City or Collapsed Stadium refresh and the Eternatus VMAX Path to the Peak refresh both require a release action after contraction.

This catalog explains why Field Blower is a particularly clean witness:

- it is pre-attack;
- it needs no Bench slot;
- it does not consume the Supporter window;
- it can target the player's own Stadium.

The same state may make other nominal Stadium outs unrealistic because their action class is locked, their cost is unpaid, their source is absent, or their entry requires the capacity being restored.

## Validation

`results/stadium_removal_channels/reproduce.py` checks the fixed snapshot counts and representative action classes. It also asserts that Pumpkaboo and Chien-Pao are the two detected Bench-entry Ability names, that Field Blower and Lost Vacuum are Items, Worker is a Supporter, and the attack family is marked turn-ending.

## Limits

The catalog is a conservative text scanner rather than a full semantic parser. It does not score access probability, cost payability, target restrictions, attack Energy, or source positioning.

It also omits the generic rule that playing a different Stadium replaces the Stadium in play. That channel is handled separately because it consumes the once-per-turn Stadium play and has different sequencing constraints.
