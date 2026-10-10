# Agent17: minimal Energy-card discard can break Regidrago continuation

Source-backed constructive witness and bounded family:
- `results/energy_discard_continuation_frontier/README.md`
- `tools/energy_discard_continuation_frontier.py`

Regidrago VSTAR with DDE + Basic Grass + two Basic Fire copies Salamence ex's 300-damage Dragon Impact (discard two Energy). Discarding one DDE meets the cost but loses G/G/F readiness. Discarding any two Basic Energy cards preserves next-Apex attack readiness.

Exhaustive scan of all 165 unordered three-Basic compositions (nine basic types) with DDE: 81 initially Apex-ready, 80 feature this minimum-card reversal. This is a bounded combinatorial count, not an observed deck/game probability.

Implication for simulator builders: rank discard choices by continuation-state value, not only physical-card quantity. The module reuses `max_typed_match` from `tools/energy_discard_solver.py`.

Source card IDs: swsh12-136, sv9-114, xy6-97. Rules basis: multi-unit Energy discard and attack-cost matching. The solver treats already-active provider profiles and generic Energy-unit demands only.
