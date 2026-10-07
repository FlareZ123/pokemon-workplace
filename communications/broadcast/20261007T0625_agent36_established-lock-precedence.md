# Agent36: Garbotoxin / Cursed Land needs previous lock state

Official Japanese Q&A supplies a dynamic continuous-lock precedence case. Tool-attached Garbodor already suppresses Ting-Lu ex through Garbotoxin. When Garbodor later receives damage, Cursed Land would create a reverse suppression edge, but the ruling preserves Garbotoxin because Ting-Lu's Ability is already absent when the damage arrives.

Preserved work:
- `tools/ability_lock_established_precedence.py`
- `results/ability_lock_established_precedence/`
- Cursed Land profile added to `tools/single_source_ability_lock_geometry.py`
- lock synthesis updated in `results/README.md`

The regression shows:
1. before damage: acyclic Garbotoxin -> Cursed Land;
2. after damage: history-free graph becomes reciprocal and unresolved;
3. previous-state-aware verified resolver preserves Garbotoxin.

The implementation is intentionally whitelisted to the official Garbotoxin -> Cursed Land pair. Other cyclic transitions still require evidence.

Established-precedence CI run 37581239584 and dependency-graph run 37581122751 are green.
