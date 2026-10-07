# Typed Trainer search integration

## Question

Can compiled Trainer search text become an executable connector action while preserving semantic target matching, physical target depletion, discard costs, and shared action budgets in one model?

Yes.

Implementation layers:

- `tools/trainer_search_profile_compiler.py`
- `tools/typed_search_target_allocator.py`
- `tools/trainer_search_state_adapter.py`
- `tools/resource_constrained_connectors.py`

Reproducer: `results/trainer_search_typed_integration/reproduce.py`  
Validation workflow: `.github/workflows/validate-trainer-search-typed-integration.yml`

## Integration

The typed adapter appends physical target-copy capacities to the existing shared resource vector.

The first three capacities remain:

1. acceptable discard cards;
2. remaining Supporter plays;
3. remaining Stadium plays.

Each physical searchable target group then contributes another capacity.

Every compiled connector action carries both its ordinary action cost and the exact target copies it consumes. The shared resource solver can therefore evaluate several connector copies without reusing one singleton target.

## Validated cases

### Rosa broad outputs to narrower needs

Rosa's compiled outputs are broad Pokémon, Trainer, and Basic Energy categories.

With physical targets consisting of one Basic Pokémon, one Item, and one Basic Energy, the typed adapter satisfies narrower Basic Pokémon, Item, and Basic Energy demands in one Supporter action.

Supporter lock removes the line.

### Guzma & Hala optional branch

With no relevant Stadium target and one Pokémon Tool target, a broad Trainer demand can be satisfied through Guzma & Hala's conditional Tool search only when the two-card optional discard is payable.

Without acceptable discard capacity, the adapter emits no useful action in that state.

### Secret Box

Secret Box combines:

- a three-card discard gate;
- Item play availability;
- four separate search axes;
- four physical target groups.

The end-to-end state reaches the complete Item + Tool + Supporter + Stadium demand vector and exposes seven total resource dimensions: three ordinary state resources plus four target-copy pools.

With only two acceptable discards, the action disappears.

### Multi-copy physical target depletion

Two Arven copies are given two available Supporter plays and a demand for two distinct Item cards.

With one physical Item target remaining, raw connector reachability exists while exact joint feasibility is false.

With two physical copies of that Item target, the exact plan succeeds.

This is the important integration property: search connectivity, action capacity, and target multiplicity are allocated together.

## Validation

GitHub Actions run `37554778899` passed.

Reported values:

```json
{
  "guzma_hala_conditional_tool_to_trainer_feasible": true,
  "rosa_broad_to_narrow_joint_feasible": true,
  "secret_box_full_state_feasible": true,
  "two_arven_single_item_target_feasible": false,
  "two_arven_two_item_targets_feasible": true,
  "typed_resource_dimensions_for_secret_box": 7
}
```

## Limits

This remains a state-local search layer. It does not yet move the selected target cards into hand in the unified board/zone state, execute later plays of those cards, or model target values.

The compiler's `Pokémon of different types` selector is still deliberately unsupported because it requires a diversity constraint across several selected cards.

## Next work

The next semantic extension should handle constrained multi-selection such as Sabrina & Brycen's different-types clause while keeping physical target allocation exact.

After that, typed search actions can be materialized into the unified state kernel so searched cards change zones and can participate in later Bench, Energy, lock, and attack transitions.
