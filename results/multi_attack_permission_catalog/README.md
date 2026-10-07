# Expanded multi-attack permission catalog

## Question

Which legal paper Expanded effects permit more than one attack in the same turn, and what state controls those permissions?

Implementation: `tools/multi_attack_permission_catalog.py`

Regression: `results/multi_attack_permission_catalog/reproduce.py`

Generated inventory: `results/multi_attack_permission_catalog/catalog.json`

## Snapshot result

The current English Expanded-set snapshot contains **13 legal print-effect instances** across **10 card names** and **3 distinct effect signatures**:

| Permission family | Source kind | Legal prints | Card names |
| --- | --- | ---: | ---: |
| Ω Barrage | Ancient Trait | 5 | 5 |
| Fluffy Barrage | Ability | 1 | 1 |
| Festival Lead | Ability | 7 | 4 |

The five Ω Barrage prints are Torchic, Nidoqueen, Medicham, Excadrill, and Bunnelby from Primal Clash.

Fluffy Barrage is represented by Jumpluff `swsh7-4`.

Festival Lead appears on Dipplin, Goldeen, Swirlix, and Seaking prints. Its text requires Festival Grounds to be in play.

## Finding 1: attack quota and permission source are separate state

The three families can all create a second attack slot, while the source of that permission differs.

Ω Barrage is an Ancient Trait. The official Pokémon TCG glossary states that Ancient Traits are neither attacks nor Abilities and that effects preventing attacks or Abilities from being used do not affect Ancient Traits.

Fluffy Barrage and Festival Lead are Abilities. Ability suppression can therefore remove their second-attack permission.

A planner should store both the numerical attack capacity and the effect that currently grants the extra slot. Treating "two attacks available" as a permanent turn integer can preserve permission after the source effect has stopped operating.

## Finding 2: Festival Lead adds an independent Stadium-presence gate

Festival Lead says: "If Festival Grounds is in play, this Pokémon may use an attack it has twice."

The relevant state variables are therefore:

- Festival Lead Ability operation;
- Festival Grounds card presence;
- the attacking Pokémon object;
- attack-phase progress.

Festival Grounds' own Stadium effect is a separate channel. An effect that suppresses a Stadium card's text without removing the card does not erase the fact that the named Stadium remains in play. This is the Stadium analogue of the repository's existing Tool attachment versus Tool-effect distinction.

The catalog marks all seven Festival Lead print instances with this named-Stadium condition.

## Finding 3: promotion can change second-attack permission

The second attack is checked after first-attack Knock Out resolution and promotion.

For Ability-based grants, the promoted opposing Active can change whether the grant is operating. Galarian Weezing's Neutralizing Gas says that while it is Active, the opponent's Pokémon in play have no Abilities except Neutralizing Gas.

That creates a concrete dynamic boundary: if Jumpluff's first Fluffy Barrage attack Knocks Out the opposing Active and the opponent promotes Galarian Weezing, Fluffy Barrage becomes suppressed before the optional second attack. A general engine should re-evaluate the permission source after the board transition.

Ω Barrage has different suppression geometry because it is an Ancient Trait.

## Coverage method

The scanner examines Ancient Traits, Abilities, attacks, and rule text on every effectively legal card in sets marked Expanded legal. It recognizes the three current wording families:

- "may attack twice a turn";
- "may attack twice each turn";
- "may use an attack it has twice".

A broad text audit over the same legal card pool found no other matching multi-attack permission records in attacks or rule text.

## Modeling consequence

`turn_attack_window.py` is a correct budget layer for the Ω Barrage timing result when the extra-attack grant remains active. A generalized engine should query the permission source before every continuation attack, especially for Ability-based grants.

The next useful extension is to make continuation permission an explicit predicate supplied by current board state rather than freezing a two-attack limit at the first attack.
