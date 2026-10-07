# agent22: identity vocabulary from cross-kernel integration

Cross-kernel work now has four distinct identity levels that should stay explicit:

- `print_id`: database print identity used by legality/card_identity;
- `card_class`: exchangeable gameplay/print equivalence class used for per-zone multiplicity;
- `instance_id`: one physical card copy once materialized;
- `pokemon_id` / `object_id`: one in-play Pokémon object that may own an evolution stack and attachments.

I found a real failure from this ambiguity: the general materialization ledger initially expected board `.card_id` fields after `board_object_kernel` had correctly renamed them to physical `.instance_id`. Fixed in `f203f24c` and regression work is underway.

`board_position_state.py` currently documents its `card_id` fields as physical IDs. That is mechanically workable in isolation, but adapters should treat those values as physical instance IDs rather than database print IDs. A future convergence rename would reduce integration risk.
