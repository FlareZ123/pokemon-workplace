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

## Durable contribution: attack discard dependency grammar
Created:
- `tools/attack_discard_dependency_grammar.py`
- `results/attack_discard_dependency_grammar/README.md`
- `results/attack_discard_dependency_grammar/reproduce.py`

This broadens the resource-instruction work to attacks whose normalized text begins with either `Discard ` or `You may discard `. It records dependency markers orthogonally because some signatures contain several.

Mandatory discard-opening family:
- 1,346 print instances
- 757 distinct signatures
- 651 with none of the tracked markers
- 27 with exact `if you do`
- 2 with `if you don't` / `if you do not`
- 75 with `discarded in this way`
- 8 with a following `Then,`

Optional discard-opening family:
- 174 print instances
- 84 distinct signatures
- 21 with none of the tracked markers
- 45 with exact `if you do`
- 19 with `discarded in this way`
- 2 with a following `Then,`

The exact-regex distinction matters because a naive substring test for `if you do` incorrectly catches `if you don't`. The two direct failure gates are Passimian / Intentional Grounding and Barraskewda / Spiral Jet.

Local reproduction passed before repository writes. Main commits for this result were `aa11779641f1c62bafb31dd49b745e52a940f38b`, `8584fbffcedab9f7719ea91591c7c00f0dfac7ca`, and `be083d0e6c271cecdaee320cf925df04b3a0a9b5`.

## Interpretation
A copy engine should separate the outer announcement cost from resource-changing instructions inside the copied body. Those inner instructions need typed dependency relations. Useful distinctions include ordinary sequential resolution, success-conditioned continuation, explicit failure-to-nothing gates, quantity-coupled output, optional actions, and contextual `Then` continuations.

The copied body resolves against the actual copier's state. An inner resource instruction is not automatically a prerequisite merely because it looks cost-like.

## Next useful work
The next strong step is a reusable ordered attack-body representation rather than more phrase counts. A prototype should:
- tokenize card text into ordered clauses;
- classify dependency connectors conservatively;
- preserve raw text for unsupported constructions;
- evaluate only rule families with explicit evidence;
- include copy-resolution examples such as Crimson Blaster and quantity-coupled attacks.

A second useful direction is a targeted scan of `before doing damage` and other timing-sensitive resource instructions, since timing can alter copy resolution and AMR even when dependency is understood.
