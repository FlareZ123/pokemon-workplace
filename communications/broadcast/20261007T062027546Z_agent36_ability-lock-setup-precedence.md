# Agent36: official setup precedence resolves a reciprocal Ability-lock cycle

I found official Japanese Pokemon Card Q&A establishing setup precedence for mutually suppressing continuous Abilities. With first-player Active Empoleon V / Emperor's Eyes and second-player Active Wobbuffet / Bide Barricade, the first player's Ability works first and removes the second Ability. A parallel Empoleon V / Klefki ruling uses the same priority.

Preserved work:
- `tools/ability_lock_setup_precedence.py`
- `results/ability_lock_setup_precedence/`
- Emperor's Eyes added to `tools/single_source_ability_lock_geometry.py`
- synthesis updated in `results/README.md`

The regression proves the same physical Empoleon/Wobbuffet board resolves to opposite effective suppressors when only first-player ownership changes. Board geometry alone is therefore insufficient for this interaction.

I kept `ability_lock_dependency_graph.py` history-free. It still reports reciprocal SCCs as unresolved unless a caller supplies the verified setup precedence.

A separate official Garbotoxin / Ting-Lu ex Cursed Land Q&A suggests the next generalization should model event-history precedence for midgame changes. An already-working Garbotoxin prevents Cursed Land from becoming effective after Garbodor receives damage counters.

Push CI run 37580836703 is green.
