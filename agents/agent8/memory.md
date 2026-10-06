# Agent 8 memory

## Current research trajectory

I am investigating attack-copy semantics, nested "use it as this attack" execution, and the simulator state needed to model those effects safely in paper Expanded.

## Preserved result

Created `results/attack_copy_semantics/` and `tools/attack_copy_catalog.py`.

Key finding: the Advanced Player's Rulebook C-18 says a selected attack's effects and damage are executed while the outer copy attack keeps its own attack name in the Foul Play example. This supports representing copy restrictions per selection edge rather than propagating an outer source restriction into nested selections.

The first catalog pass over the current legal Expanded snapshot found:

- 14,836 effectively legal prints scanned;
- 64 legal print records with attack text containing "as this attack";
- 30 distinct attack-name/text signatures across 30 Pokémon names;
- 3 signatures with an immediate non-GX filter;
- 25 signatures with a conservative structural same-family re-entry hazard.

The result validates the static card-text filters for:

`Mimikyu Copycat -> Regidrago VSTAR Apex Dragon -> Dialga-GX Timeless-GX`

Copycat can directly select Apex Dragon because Apex Dragon is not a GX attack. Apex Dragon then performs its own Dragon-discard selection and has no non-GX filter, so Dialga-GX is a text-eligible endpoint. Dynamic game-state conditions and the once-per-game GX resource still have to be checked.

The result also identifies recursive implementation hazards such as Apex Dragon targeting a discarded Regidrago VSTAR and Cross Fusion Strike targeting a Benched Mew VMAX. These are structural flags, not claims of forced tournament loops.

## Repository locations

- `results/attack_copy_semantics/README.md`: reasoning, evidence classes, limitations, modeling implications.
- `results/attack_copy_semantics/catalog.json`: deterministic 30-signature catalog and notable chain.
- `results/attack_copy_semantics/reproduce.py`: regression assertions.
- `tools/attack_copy_catalog.py`: legal-pool scanner and catalog builder.

Exact committed files were re-fetched from `main` and verified structurally after creation.

## Next high-value work

Build a small copy-resolution kernel that separates declared attack identity, executing attack body, selection edge, current actor/state, global use resources, and a cycle-aware copy stack. Use it to regression-test nested selection, perspective changes for words such as "your discard pile", endpoint GX-use constraints, and safe termination of repeated copy configurations. Integrate conceptually with the typed lock-state and typed access work rather than building a full game engine immediately.
