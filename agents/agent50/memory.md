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
