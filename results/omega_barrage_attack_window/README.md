# Omega Barrage and the attack continuation window

## Question

How should the shared turn-action model represent card text that permits a second attack in the same turn?

The ordinary turn budget treats an attack as an absorbing turn boundary. Ω Barrage is an Expanded-legal exception and therefore needs a narrower attack-phase state.

Implementation: `tools/turn_attack_window.py`

Regression: `results/omega_barrage_attack_window/reproduce.py`

## Evidence

The bundled card data contains five effectively legal Ω Barrage prints. Their Ancient Trait says the Pokémon may attack twice a turn.

A historical TPCi Rules Team ruling provides the missing timing detail. Bulbapedia's Ancient Trait reference attributes the ruling to the Primal Clash FAQ dated 2015-02-05 and records that, after the first Ω Barrage attack, the player may proceed to the second attack or end the turn. Ordinary effects and other turn actions do not reopen in between. The underlying Compendium ruling is identified as "Omega Barrage" from the TPCi Rules Team.

This result treats that source as an authoritative ruling preserved through a secondary index because the Compendium endpoint is currently inaccessible to the research web client.

## State model

`AttackPhaseBudget` stores:

- maximum attacks permitted in the current attack phase;
- attacks already used;
- the physical Pokémon object that began the attack phase;
- whether the turn has ended.

`TurnExecutionWindow` composes that state with the existing `TurnActionBudget`.

Before the first attack, ordinary action quotas behave exactly as the shared budget already specifies. Once the first attack begins, the ordinary action window closes. If another attack slot remains, the same Pokémon object may attack again or the player may end the turn.

The attacker binding matters because Ω Barrage belongs to "this Pokémon." A remaining attack slot cannot be transferred to another Active Pokémon merely because board state changes.

## Regression cases

The reproducer verifies:

- an ordinary one-attack window still ends the turn after its first attack;
- a two-attack Ω Barrage window remains open after the first attack;
- Supporter, Stadium, manual Energy attachment, and Retreat actions are unavailable after that first attack;
- the same attacker can use the second attack slot;
- a different Pokémon object cannot inherit the second slot;
- the second attack closes the turn;
- the player can voluntarily end the turn instead of using the second attack.

This keeps the existing action-budget quotas reusable. The attack layer determines whether the turn has actually reached its absorbing boundary.

## Scope

The model represents attack permission and action-window closure. Each attack still needs its own announcement legality checks, including Energy, Special Conditions, temporary effects, and any card-specific restrictions.

Knock Out resolution and promotion between Ω Barrage attacks remain board-state transitions. The card text explicitly anticipates promotion after a first-attack Knock Out, so a complete engine should resolve that board transition before checking the second attack.

The current model does not yet compose extra-turn scheduling with a partially consumed multi-attack phase. That interaction should be tested separately before merging this layer into the shared turn-sequence kernel.
