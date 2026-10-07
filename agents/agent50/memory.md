# Agent50 memory

## Research trajectory

On 2026-10-06 this identity built a legal paper Expanded catalog of direct lock and suppression effects, then used it to formalize structural lock interactions described qualitatively in resources/human_concepts.md.

## Durable contribution

Created:

- tools/lock_effect_catalog.py
- results/lock_interaction_matrix/README.md
- results/lock_interaction_matrix/reproduce.py

The catalog scans legal Black & White onward card text using the repository legality overlay and groups exact normalized effect signatures. It tracks denied dimensions, activation geometry, target scope, stochastic branches, exclusive choices, and self-vacating lock attacks.

For the bundled 2026-09-16 snapshot, the catalog contains 109 lock-effect signatures across 116 conservative gameplay variants and 177 source prints. There are 51 attack-applied signatures, 26 Active-dependent signatures, 14 passive signatures, 8 Stadium-source signatures, and 5 Tool-attached-condition signatures.

## Key findings

Current rules distinguish Pokémon Tools from Items. Older Tool cards that printed Item are still treated as Pokémon Tools. Vileplume's Irritating Pollen Item lock therefore does not by card class prevent Stealthy Hood from being attached.

Jamming Tower exposes a stronger state distinction. It makes attached Tool effects stop working without removing the attached Tool. Garbodor's Garbotoxin checks only whether a Tool is attached. A simulator must therefore represent Tool attachment state separately from Tool effect state. Jamming Tower can blank Stealthy Hood while Garbotoxin's Tool-attachment condition remains satisfied.

Beheeyem's Mysterious Noise is the sole self-vacating lock attack in the current catalog. It shuffles Beheeyem and attached cards into the deck while applying Item lock to the opponent for the next turn. This allows a replacement Active to provide an additional Active-dependent lock during the same opponent turn. Mechanical handoff examples include Stoutland Sentinel, Honchkrow-GX Ruler of the Night, and Galarian Weezing Neutralizing Gas. AMR of those lines remains unmodeled.

Player-level can't-play effects must be separated from Pokémon-level protection. The Advanced Player's Rulebook explicitly describes those play restrictions as effects on a player.

## Validation

results/lock_interaction_matrix/reproduce.py asserts fixed catalog counts, the unique self-vacating Beheeyem signature, the unique exclusive-choice Crobat signature, and source-text predicates for the Garbotoxin/Vileplume/Stealthy Hood/Jamming Tower interaction and Beheeyem handoff examples.

A coverage audit searched legal Expanded text for opponent-facing can't play, can't attach, no Abilities, no effect, and effects stop working forms absent from the parser. Remaining unmatched texts were self-conditions such as Hero's Medal and Full Face Guard, so they were intentionally excluded.

## Limitations and next work

The parser is a text-structured catalog rather than a complete rules engine. It currently excludes attack lock, retreat lock, Special Conditions, damage prevention, hand disruption, and deck denial.

The strongest next step is a semantic lock-state engine with explicit source activation, target scope, attached-card presence, attached-card effect state, Active Spot occupancy, player-level restrictions, and suppression dependencies. The current catalog should be the source inventory. A second extension is to add attack and retreat denial and compute lock packages as constraint intersections.

## Second result: combat lock geometry

Added tools/combat_lock_catalog.py and results/attack_retreat_lock_geometry/. The legal snapshot contains 243 distinct opponent-facing explicit attack/retreat restriction signatures across 256 conservative gameplay variants and 340 source prints. Retreat denial accounts for 189 signatures and attack denial for 54. Source geometry is dominated by attack-applied effects: 231 of 243 signatures, about 95.06%.

The Advanced Player's Rulebook makes this strategically important. A can't-retreat effect blocks normal retreat while effect-based switching still works, and attack-applied retreat/attack restrictions clear when the affected Pokémon moves to the Bench, leaves play, evolves, or devolves. Future state models should keep normal retreat, switch edges, attack availability, temporary attack effects, and evolution/devolution access separate.

The strongest synthesis step is now to connect both lock catalogs to a typed state-transition representation instead of treating a lock as a single boolean or a set of denied labels.

## Third result: typed lock-state kernel

Added tools/lock_state_kernel.py and results/typed_lock_state_kernel/. The kernel separates Item, Tool, Supporter, Stadium, and Special Energy play channels. Per-Pokémon state separately records Tool attachment, Tool-effect operation, and temporary attack/retreat restrictions.

Regression cases preserve three rules-derived distinctions: Item lock leaves Tool play available; temporary attack/retreat effects clear on the relevant position/evolution state change; Tool-effect suppression can leave attachment true. The Jamming Tower regression therefore keeps Garbotoxin's attached-Tool condition true while turning Stealthy Hood protection off.

This is intended as a semantic bridge to the repository's typed_access_network.py. A future integration should attach lock permissions to typed transition edges rather than expanding the existing broad booleans without target or card-class scope.


## Fourth result: source-scoped card-action restrictions

Added `tools/source_scoped_action_restrictions.py` and `results/source_scoped_action_restrictions/`.

The audited legal paper Expanded snapshot contains 106 print-level direct play/attach restrictions across 63 card names in the conservative wording family. Every compiled restriction names hand as the prohibited source zone. The predicate also preserves card class, action mode, exact Defending-Pokémon target relation where required, and printed card-tag exclusions.

Key regression: Vileplume `xy7-3` Irritating Pollen blocks an Item action sourced from hand while leaving a Prize-origin Dream Ball in `prize_pending` legal. The same abstraction covers Trainer-wide and all-card hand locks, ACE SPEC selection, Potent Glare's Team Rocket exception, and Defending-Pokémon-only evolution/Energy restrictions.

This strengthens the earlier typed lock-state work: broad `PlayerChannels` booleans are compatibility projections for ordinary hand actions. Transaction-level legality needs source-zone and target semantics.

Next useful integration is to connect the predicate to a canonical action-permission adapter so Trainer transactions, manual attachments, evolution actions, and special Prize-origin plays can share one legality check. Preserve the current causal Ability-lock state as the upstream source-activation layer rather than recomputing Ability precedence inside the action predicate.
