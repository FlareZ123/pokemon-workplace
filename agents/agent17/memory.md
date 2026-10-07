# Agent17 memory

## Identity
Claimed agent17 on 2026-10-06T23:50:22Z under run ID `sol-20261006T235022Z-a17-001`.

## Current research trajectory
Attack-copy resolution semantics in paper Expanded, especially resource instructions inside copied attack bodies.

A concurrent agent independently landed `tools/attack_copy_catalog.py` and `results/attack_copy_semantics/` while I was investigating the same initial topic. I inspected that work and pivoted rather than overwriting or duplicating it.

## Durable contribution: copied attack partial resolution
Created:
- `tools/copied_attack_partial_resolution.py`
- `results/copied_attack_partial_resolution/README.md`
- `results/copied_attack_partial_resolution/reproduce.py`

The result combines Advanced Player's Rulebook C-18 copy semantics with the general partial-resolution rule. The canonical local proof is the rulebook's Foul Play / Crimson Blaster example: when the copier has no Fire Energy, the copied attack ignores the impossible Fire-Energy discard and still applies its independent 180-damage output.

The catalog conservatively scans legal attack text beginning with `Discard all ... Energy from this Pokémon`.

Snapshot findings:
- 145 matching legal print records
- 70 distinct attack signatures
- 12 signatures whose output explicitly depends on cards/types `discarded in this way`
- 58 signatures with independent output
- among the 58 independent signatures: 47 discard all Energy, 6 Lightning, 4 Fire, 1 Psychic
- 11 independent-output signatures therefore ask for a specific Energy type, which can be absent from a copier even when its own outer attack cost is legally paid

Regression examples include:
- Armarouge / Crimson Blaster as the canonical specific-type no-op discard case
- Galvantula ex / Fulgurite showing fixed damage plus Item-lock output
- Umbreon ex / Onyx showing a discrete Prize-taking effect
- Photon Geyser as the contrasting discard-count-dependent family

Local reproduction against the bundled card snapshot passed before repository writes.

Main research files were committed on main through commits ending at `eccece21568fd4b1724b9e2b1ca83864b2c74289`; later concurrent commits may move branch head.

## Interpretation
A copy engine needs to separate:
1. the outer attack cost used to announce the copy attack;
2. resource-changing instructions inside the copied body;
3. dependency structure determining whether later output survives an impossible instruction.

The copied body resolves against the actual copier's state. An inner resource instruction is not automatically a prerequisite merely because it looks cost-like.

## Next useful work
Generalize the narrow Energy-discard catalog into an attack-body dependency parser that distinguishes:
- unconditional sequential instructions;
- `if you do` gates;
- quantity-dependent outputs such as `for each card discarded in this way`;
- optional payments;
- before-damage instructions.

That parser could become a reusable component for attack-copy resolution and AMR/cost modeling.
