# Active Iron Thorns ex blocks the champion Shadow Rider's Radiant launch

## Matchup-relevant rule interaction

The sixth-place 2026 Aichi Open League list of Kazuma Kashi is an **Iron Thorns ex-only Pokémon deck**: all four Pokémon cards are Iron Thorns ex. In a Basic-valid opening against that list, one Iron Thorns ex therefore must start Active. The [original tournament list](https://www.limitlesstcg.com/tournaments/566/decklists) provides the opponent archetype and exact card-count evidence.

The bundled English print Iron Thorns ex **sv6-77** has the **Initialization** Ability: while it is Active, Pokémon with Rule Boxes have no Abilities, apart from Future Pokémon. The rulebook treats Radiant Pokémon as possessing a Rule Box. Radiant Eternatus **swsh12pt5-105** is Radiant and Dragon type, **not Future**, so its Climactic Gate is suppressed. Shadow Rider Calyrex VMAX **swsh6-75** and Tapu Lele-GX **sm2-60** likewise lose Underworld Door and Wonder Tag while the same lock applies.

**Consequence:** the [43.699162430%](../shadow_rider_radiant_launch/) *mechanical availability* of the dual-VMAX Radiant line drops to **exactly zero ability-mediated launches while opposing Iron Thorns ex is Active and its Initialization remains unnegated**. This is a state-conditional rules consequence. It is not a prediction that 43.7% of complete games against Iron Thorns are lost. Other ways to develop an attacker, removal of the suppressing Ability, and other turns must be evaluated separately.

## Interaction with the second-place Vileplume list

Rule Boxes distinguish the engines in the [two tournament baseline decks](../competitive_deck_baselines/).

| Pokémon / Ability | Has Rule Box? | Affected by active unnegated Initialization? |
| --- | --- | --- |
| Radiant Eternatus / Climactic Gate | Yes | Suppressed |
| Shadow Rider Calyrex VMAX / Underworld Door | Yes | Suppressed |
| Tapu Lele-GX / Wonder Tag | Yes | Suppressed |
| Pidgeot ex / Quick Search | Yes | Suppressed |
| Vileplume / Irritating Pollen | No | Retained |
| Fan Rotom / Fan Call | No | Retained |
| Jirachi / Stellar Wish | No | Retained |

This illustrates a useful matchup difference: Vileplume's non-Rule-Box Item lock can continue operating despite Iron Thorns's active Rule-Box Ability lock, whereas the champion Shadow Rider's named acceleration and early Radiant launch cannot.

Tool protection, Stadium and Ability suppression priority, position switching and ability-negation counterplay have complex conditional interactions. The table presumes **one active, effective Initialization**, and should not be extrapolated to every game state.

## Test and limitations

The [source-text regression](reproduce.py) parses eight exact English card prints from the repository's bundled card data, verifies their relevant named Abilities, Rule Box construction and Future exemption, and checks both the active and the inactive source states. It independently imports the champion list counts and exact unlocked Radiant launch result.

The Iron Thorns sixth-place 60-card Japanese tournament list includes some items labeled **unreleased** on the original English-facing tournament record. This result therefore treats its four-Iron-Thorns-Pokémon composition as an opponent **reference matchup** and validates the specific printed Iron Thorns ex English Ability. It does not certify every other card of that Japanese list for current English paper Expanded.

Priority next step: construct a realistic head-to-head action model with opponent Ability-lock suppression, Vileplume's Item lock, turn order and gust lines together, and compare win paths. The conditional suppression fact is firm, but the games' outcome distribution remains unknown.
