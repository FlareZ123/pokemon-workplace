# Attack and retreat lock geometry in paper Expanded

## Question

How common are direct attack-denial and retreat-denial effects in the legal paper Expanded card pool, and what does their source geometry imply for counterplay?

This extends the resource-denial catalog in results/lock_interaction_matrix/ with two combat-control dimensions that were deliberately excluded there.

## Result

Against the bundled 2026-09-16 snapshot plus the repository's current official-ban overlay, the conservative parser finds:

| Quantity | Count |
| --- | ---: |
| Legal source prints | 340 |
| Conservative gameplay variants | 256 |
| Distinct effect signatures | 243 |
| Retreat-denial signatures | 189 |
| Attack-denial signatures | 54 |
| Stochastic signatures | 12 |

Source geometry is strongly concentrated in attacks:

| Source / activation | Signatures |
| --- | ---: |
| Attack-applied | 231 |
| Active-dependent Ability | 6 |
| Passive Ability | 3 |
| Bench-dependent Ability | 1 |
| Stadium | 1 |
| One-shot rule effect | 1 |

Thus 231 of 243 signatures, or about **95.06%**, are attack-applied effects on the opposing Pokémon.

## Strategic consequence: retreat lock and switching are different channels

The Advanced Player's Rulebook states that an effect saying a Pokémon can't retreat blocks the normal once-per-turn retreat. It also states that the affected Pokémon can still be switched to the Bench by another effect. For attack-applied retreat lock, the effect disappears when that Pokémon moves to the Bench, leaves play, evolves, or devolves.

Attack denial has a parallel rule. An attack-applied can't-attack or can't-use-attacks effect disappears when the affected Pokémon moves to the Bench, leaves play, evolves, or devolves.

This makes retreat lock a narrower constraint than inability to leave the Active Spot. A simulator that treats those states as equivalent overvalues many lock lines. Switching access is a separate escape edge that can remove the restriction entirely.

Because about 95% of the cataloged attack/retreat restrictions are attack-applied, this distinction affects most of this control family.

## Representation implication

A useful state model should separate normal retreat availability, effect-based switching availability, attack availability, current Active identity, temporary attack effects attached to that Pokémon, and evolution or devolution access that can clear those effects.

A single immobilized flag is too coarse. Snorlax's Block prevents normal retreat while its Ability remains active. A one-turn Sand Tomb effect can instead be cleared by switching the target.

## Method

tools/combat_lock_catalog.py scans legal Black & White onward card text using the same legality overlay as the existing baseline. It recognizes opponent-facing can't-retreat, can't-attack, and can't-use-attacks clauses while excluding self-restrictions such as this Pokémon can't attack during your next turn.

The parser handles common Defending Pokémon wording, direct references to the opponent's Pokémon, pronoun follow-ups such as It can't retreat, and switch attacks that apply the restriction to the new Active Pokémon.

results/attack_retreat_lock_geometry/reproduce.py asserts the fixed snapshot counts and activation breakdown.

A coverage audit inspected legal texts containing the relevant can't phrases that were not captured. The remaining cases were self-restrictions, including recoil-style attack clauses, Pokémon Doll cards that cannot retreat themselves, and conditional self-attack restrictions such as Slaking ex's Born to Slack.

## Limitations

This catalog focuses on explicit inability to attack or retreat. It excludes Paralyzed or Asleep as indirect denial, Energy denial that makes attacks impossible, increased Retreat Cost, forced-attack effects, prevention effects, and other switching restrictions.

It also does not estimate practical access to Switch effects, gust, evolution, Scoop Up effects, or other escape routes. Those belong in a game-state model rather than this text inventory.

## Next step

The next useful synthesis is to combine resource locks and combat locks into a typed state-transition graph. Edges should represent normal retreat, switch effects, evolution/devolution, Tool and Stadium changes, and source removal. Locks should disable only the edges their rules actually remove.
