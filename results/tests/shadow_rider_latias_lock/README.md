# Champion Latias ex reopens Guzma's own-switch route when Active Ability lock moves away

**Status:** Exact, source-grounded one-turn tactical result. Independent action-order regression. No match-win-rate claim or recommended 60-card change.

## Source-derived mechanisms

The published [2026 Aichi Shadow Rider Calyrex VMAX champion](../../decks/shadow-rider-calyrex/) includes **one Latias ex** (sv8-76) and **one Guzma**. Latias ex is a Basic Pokémon with the *Skyliner* Ability, which grants your Basic Pokémon in play **no Retreat Cost** while the Ability is active. In the Advanced Player's Rulebook (A-03, A-02, C-05), retreating costs Energy, can occur once per turn and requires a replacement Pokémon; active-dependent Abilities may change as a Pokémon moves between Active and Bench. Playing Guzma successfully switches the opponent's Bench target Active, then forces your own Active to switch with a Benched Pokémon when possible.

Two opposing ability-suppression sources from the real Expanded card pool make the timing question important:

- **Galarian Weezing (swsh2-113)**: *Neutralizing Gas* suppresses opposing Pokémon Abilities **only while this Weezing is Active**. Switching it onto the Bench deactivates the lock.
- **Path to the Peak (swsh6-148)**: while Stadium in play, Pokémon with Rule Boxes have no Abilities, including Latias ex. Its effect persists when an opposing Active Pokémon is switched.

These two locks have different dependency geometries. The controlled snapshot does not claim that Galarian Weezing and Shadow Rider V are featured together in any published tournament deck.

## Controlled attacking-turn board

Own Active: Shadow Rider VMAX with five Basic Psychic Energy. Own Bench: two Shadow Rider VMAX with two and one Psychic, two unpowered Basic support Pokémon (Tapu Lele-GX and Lillie's Clefairy ex), and **Latias ex** with no Energy, occupying the fifth Bench slot. This substitutes the published champion's Latias ex for the unpowered Mimikyu used in [the earlier tested board](../shadow_rider_guzma_damage/). Every card in this own board belongs to the published champion 60.

The opposing Bench target is an undamaged 210-HP two-Prize Shadow Rider V. Under the **active-only lock** variant, the opposing Active is Galarian Weezing with Neutralizing Gas. Under the **Stadium lock** variant, Path to the Peak is active. Both are independently specified hypothetical opposing effect states. Our attacking turn already has one selected Supporter in hand, all described Pokémon established, and no manual Energy attachment, draw, other Ability actions, stadium replacement, Tool cards or independent switch effect. The objective is to **KO the specified two-Prize Benched target this turn**.

Without extra Energy payment, eight Psychic in play make Max Geist deal 250. Our two low-Energy VMAX Bench Pokémon cannot attack with Max Geist, and the only ready VMAX starts Active.

## Exact opponent-first timing results

| Dynamic lock state | Latias present on own Bench? | Source | Two-Prize target can be Knocked Out? |
| --- | --- | --- | --- |
| No Ability lock | Yes | Guzma | **Yes** |
| Active Galarian Weezing lock, gust removes Weezing first | Yes | Guzma | **Yes** |
| Path to the Peak, Latias Rule Box Ability suppressed throughout | Yes | Guzma | **No** |
| No Ability lock | No | Guzma | **No** |
| Active Galarian Weezing lock | No | Guzma | **No** |
| Path to the Peak | Yes | Hypothetical Boss's Orders | **Yes** |

The winning Guzma route while Latias is present:
1. Guzma switches opposing Shadow Rider V to Active, moving the opposing Galarian Weezing to Bench, where its active-only Neutralizing Gas ceases.
2. Latias ex's Skyliner immediately functions again and gives your Basic Pokémon no Retreat Cost.
3. The mandatory own part of Guzma promotes a Benched Basic Pokémon, such as Tapu Lele-GX.
4. Normal Retreat of that newly Active Basic is free thanks to Skyliner. Promote the originally powered VMAX back to Active.
5. Max Geist does 250 with all eight Psychic preserved, taking two Prizes from the 210-HP V.

With Path to the Peak, moving an opposing Active does nothing to remove the Stadium, so Skyliner stays suppressed. None of the unpowered Basic Pokémon can pay their ordinary Retreat Costs, and returning the ready VMAX by paying its own Retreat 2 lowers the available damage to 190. The two-Prize knockout fails in this restricted scenario. A hypothetical Boss's Orders keeps the ready VMAX Active and succeeds regardless of Latias suppression.

## Methods and verification

`tools/shadow_rider_latias_lock.py` uses an explicit dynamic lock state before/after the opposing gust, rather than treating a starting Ability lock as permanently active for an entire attacking turn. It tracks six own Pokémon, their attached Psychic counts, one Retreat, one Supporter and the chosen Active as actions resolve. The independent `reproduce.py` uses a breadth-first action graph and verifies printed Abilities/rules for Latias ex, Galarian Weezing and Path to the Peak.

**3,888** state/source/Ability-lock/HP comparisons were independently verified. Reproduce from repository root:
`python -m results.tests.shadow_rider_latias_lock.reproduce`.

**Limits and implications:** This model omits other attacking options, Pokémon with additional attached Energy, Ability reactivation triggers, evolving and searching, Tool access, stadium replacement and opponent retaliation. It identifies a specific reason that an active-only Ability lock can be neutralized by an opponent-first gust before choosing a free retreat line. It also shows why Bench selection between Mimikyu and Latias, both actual champion 60 cards, may change tactical source availability. Any assertion about which to Bench in a real game requires its matchup-specific counterattacks and resources.
