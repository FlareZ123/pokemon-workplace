from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from card_class_namespace import deck_name
from identity_materialization import IdentityLedger, assert_conserved
from multicopy_zone_state import ZoneCountState
from search_materialization import SearchTargetBinding, materialize_search_to_hand
from trainer_search_profile_compiler import compile_multi_output_trainer_profiles
from typed_search_target_allocator import (
    BASIC_ENERGY, BASIC_POKEMON, ITEM, TargetGroup,
    enumerate_typed_target_profiles, make_demand,
)


def main():
    profiles = compile_multi_output_trainer_profiles(ROOT / "resources")
    rosa = next(profile for profile in profiles if profile.name == "Rosa")

    targets = (
        TargetGroup("Bagon", 1, frozenset({BASIC_POKEMON, "type:dragon"})),
        TargetGroup("Quick Ball", 1, frozenset({ITEM})),
        TargetGroup("Basic Fire Energy", 1, frozenset({BASIC_ENERGY, "type:fire"})),
    )
    demands = (
        make_demand("basic", "Basic Pokémon"),
        make_demand("item", "Item card"),
        make_demand("energy", "Basic Energy card"),
    )
    allocation = enumerate_typed_target_profiles(rosa.base_outputs, targets, demands)
    action = next(row for row in allocation.actions if row.output == (1, 1, 1))
    assert action.target_cost == (1, 1, 1)

    bindings = tuple(
        SearchTargetBinding(deck_name(target.name).token(), target.name)
        for target in targets
    )
    initial = IdentityLedger(
        ZoneCountState.from_mapping({
            (binding.card_class, "deck"): 1
            for binding in bindings
        })
    )

    result = materialize_search_to_hand(
        initial,
        targets,
        bindings,
        action.target_cost,
        (("bagon-1",), ("quick-ball-1",), ("fire-energy-1",)),
    )
    assert_conserved(initial, result.ledger)
    assert result.instance_ids == ("bagon-1", "quick-ball-1", "fire-energy-1")
    for binding in bindings:
        assert result.ledger.exchangeable.count(binding.card_class, "deck") == 0
    for instance_id in result.instance_ids:
        assert result.ledger.instance(instance_id).zone == "hand"

    print("typed search materialization regressions passed")


if __name__ == "__main__":
    main()
