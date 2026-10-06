# Typed lock-state kernel

## Purpose

The two lock catalogs show that a single boolean such as items_allowed or immobilized cannot represent several important Expanded interactions. This result adds a minimal state kernel that preserves distinctions established by card text and the Advanced Player's Rulebook.

Implementation: tools/lock_state_kernel.py

Regression: results/typed_lock_state_kernel/reproduce.py

## State channels

The kernel separates play permissions for Items, Pokémon Tools, Supporters, Stadiums, and Special Energy.

It also separates per-Pokémon state for Tool attachment, Tool-effect operation, temporary attack denial from an attack effect, and temporary retreat denial from an attack effect.

## Regression 1: Item lock leaves Tool play available

Applying an Item-play lock disables only the Item channel. The Tool channel remains available.

This encodes the current rule that Pokémon Tools are their own Trainer-card type. It prevents a Vileplume Irritating Pollen state from accidentally blocking Stealthy Hood solely because older Tool printings once displayed Item text.

Applying a broad Trainer lock disables Item, Tool, Supporter, and Stadium play channels together.

## Regression 2: temporary combat locks clear on the appropriate state change

The kernel can attach temporary attack-denial and retreat-denial flags to a Pokémon. A position or evolution-state change clears both flags.

This represents the rulebook treatment of attack-applied can't-attack and can't-retreat effects. It preserves a separate switch escape route instead of treating retreat denial as complete immobilization.

## Regression 3: Tool attachment and Tool effect are independent state variables

A Garbodor state with a Tool attached satisfies Garbotoxin's attachment condition.

A Stealthy Hood holder is protected only while the Tool is attached and its Tool effect is functioning.

Applying Tool-effect suppression, as from Jamming Tower, changes the Tool-effect flag while preserving attachment. The regression therefore has both outcomes at once: Garbotoxin's attachment condition remains true, and Stealthy Hood protection becomes false.

That is the asymmetry identified in the lock interaction matrix.

## Relation to the existing typed access network

The repository's typed Supporter-access engine currently stores broad booleans such as items_allowed, abilities_allowed, and supporters_allowed. Those are useful for its narrow regression cases. The lock catalogs show where a larger engine needs more structure.

Tool play cannot be inferred from Item play. Retreat denial does not imply that Switch effects are unavailable. Tool-effect suppression does not remove the attached Tool. Target-specific Ability suppression will also need per-Pokémon scope instead of one global Ability boolean.

The present kernel is intentionally small. It establishes typed state variables that a future general state-transition engine can compose with the existing zone and action-window model.

## Next step

A stronger combined engine should attach permissions to typed transition edges. Item lock would remove Item-play edges, Trainer lock would remove four Trainer subchannels, retreat lock would remove the normal-retreat edge, and switching would remain available unless separately denied. Continuous sources such as Garbotoxin, Jamming Tower, and Active-only Abilities would then add or remove constraints as board state changes.
