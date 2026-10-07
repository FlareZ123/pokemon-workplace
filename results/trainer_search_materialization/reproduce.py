"""Reproduce typed Trainer search payload materialization into physical zones."""

from __future__ import annotations

import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from card_class_namespace import exact_print  # noqa: E402
from identity_materialization import IdentityLedger, assert_conserved  # noqa: E402
from multicopy_zone_state import ZoneCountState  # noqa: E402
from resource_constrained_connectors import (  # noqa: E402
    evaluate_resource_constrained_connectors,
)
from trainer_search_materialization import (  # noqa: E402
    SearchTargetBinding,
    materialize_search_witness,
)
from trainer_search_profile_compiler import (  # noqa: E402
    compile_multi_output_trainer_profiles,
)
from trainer_search_state_adapter import (  # noqa: E402
    TrainerSearchState,
    adapt_compiled_search_profile_typed,
)
from typed_search_target_allocator import (  # noqa: E402
    ITEM,
    POKEMON_TOOL,
    STADIUM,
    SUPPORTER,
    TargetGroup,
    make_demand,
)


HAND_SEARCH_RE = re.compile(
    r"search your deck for .*?put (?:it|them) into your hand",
    re.IGNORECASE | re.DOTALL,
)


def representative(profiles: tuple, name: str):
    matches = [profile for profile in profiles if profile.name == name]
    if not matches:
        raise AssertionError(f"{name} missing")
    return matches[0]


def compiled_cards(resources_root: Path, card_ids: set[str]):
    found = {}
    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        for card in json.loads(path.read_text(encoding="utf-8")):
            if card.get("id") in card_ids:
                found[card["id"]] = card
    if set(found) != card_ids:
        missing = sorted(card_ids - set(found))
        raise AssertionError(f"compiled cards missing from database: {missing}")
    return found


def binding(resource_name: str, print_id: str, card_name: str) -> SearchTargetBinding:
    return SearchTargetBinding(
        resource_name=resource_name,
        card_class=exact_print(print_id).token(),
        card_name=card_name,
    )


def main() -> None:
    profiles = compile_multi_output_trainer_profiles(ROOT / "resources")

    # The current compiler semantic island is safe to materialize as deck -> hand:
    # every one of its 40 print profiles literally uses that destination wording.
    cards = compiled_cards(
        ROOT / "resources",
        {profile.card_id for profile in profiles},
    )
    for profile in profiles:
        text = " ".join(cards[profile.card_id].get("rules") or [])
        assert HAND_SEARCH_RE.search(text), profile.card_id
        if profile.conditional_outputs:
            assert "may also search for" in text.lower()
            assert "in this way" in text.lower()

    # Secret Box proves that one exact four-axis solver witness can now move the
    # four selected physical target classes into hand without losing copy totals.
    secret_box = representative(profiles, "Secret Box")
    secret_targets = (
        TargetGroup("Quick Ball", 1, frozenset({ITEM})),
        TargetGroup("Float Stone", 1, frozenset({POKEMON_TOOL})),
        TargetGroup("Boss's Orders", 1, frozenset({SUPPORTER})),
        TargetGroup("Artazon", 1, frozenset({STADIUM})),
    )
    secret_demands = (
        make_demand("item", "Item card"),
        make_demand("tool", "Pokémon Tool card"),
        make_demand("supporter", "Supporter card"),
        make_demand("stadium", "Stadium card"),
    )
    secret_adaptation = adapt_compiled_search_profile_typed(
        secret_box,
        secret_demands,
        secret_targets,
        TrainerSearchState(discardable_cards=3),
    )
    assert secret_adaptation is not None
    secret_plan = evaluate_resource_constrained_connectors(
        (1, 1, 1, 1),
        secret_adaptation.resource_capacities,
        (secret_adaptation.connector,),
    )
    assert secret_plan.exact_joint_feasible
    assert secret_plan.witness_actions is not None

    secret_bindings = (
        binding(secret_adaptation.resource_names[3], "swsh1-179", "Quick Ball"),
        binding(secret_adaptation.resource_names[4], "xy8-137", "Float Stone"),
        binding(secret_adaptation.resource_names[5], "swsh2-154", "Boss's Orders"),
        binding(secret_adaptation.resource_names[6], "sv2-171", "Artazon"),
    )
    secret_ledger = IdentityLedger(
        ZoneCountState.from_mapping(
            {
                (row.card_class, "deck"): 1
                for row in secret_bindings
            }
        )
    )
    secret_after = materialize_search_witness(
        secret_ledger,
        secret_adaptation,
        secret_plan,
        secret_bindings,
    )
    assert_conserved(secret_ledger, secret_after.ledger)
    for row in secret_bindings:
        assert secret_after.ledger.exchangeable.count(row.card_class, "deck") == 0
        assert secret_after.ledger.exchangeable.count(row.card_class, "hand") == 1
    assert len(secret_after.moves) == 4

    # Two Arven uses share the same physical Quick Ball pool. The solver witness
    # consumes two target copies, and physical execution moves exactly two copies.
    arven = representative(profiles, "Arven")
    arven_targets = (
        TargetGroup("Quick Ball", 2, frozenset({ITEM})),
    )
    arven_demands = (
        make_demand("two Items", "Item card", copies=2),
    )
    arven_adaptation = adapt_compiled_search_profile_typed(
        arven,
        arven_demands,
        arven_targets,
        TrainerSearchState(supporter_plays_remaining=2),
        copies=2,
    )
    assert arven_adaptation is not None
    arven_plan = evaluate_resource_constrained_connectors(
        (2,),
        arven_adaptation.resource_capacities,
        (arven_adaptation.connector,),
    )
    assert arven_plan.exact_joint_feasible
    assert arven_plan.witness_actions is not None
    assert len(arven_plan.witness_actions) == 2

    quick_ball_class = exact_print("swsh1-179").token()
    arven_bindings = (
        SearchTargetBinding(
            resource_name=arven_adaptation.resource_names[3],
            card_class=quick_ball_class,
            card_name="Quick Ball",
        ),
    )
    arven_ledger = IdentityLedger(
        ZoneCountState.from_mapping({(quick_ball_class, "deck"): 2})
    )
    arven_after = materialize_search_witness(
        arven_ledger,
        arven_adaptation,
        arven_plan,
        arven_bindings,
    )
    assert_conserved(arven_ledger, arven_after.ledger)
    assert arven_after.ledger.exchangeable.count(quick_ball_class, "deck") == 0
    assert arven_after.ledger.exchangeable.count(quick_ball_class, "hand") == 2
    assert sum(move.amount for move in arven_after.moves) == 2

    # A target-cost witness becomes stale if the physical deck no longer contains
    # the represented copy. Execution must fail rather than recreate the card.
    stale_ledger = IdentityLedger(
        ZoneCountState.from_mapping({(quick_ball_class, "hand"): 2})
    )
    try:
        materialize_search_witness(
            stale_ledger,
            arven_adaptation,
            arven_plan,
            arven_bindings,
        )
    except ValueError:
        stale_witness_rejected = True
    else:
        stale_witness_rejected = False
    assert stale_witness_rejected

    print(
        json.dumps(
            {
                "compiled_hand_search_prints": len(profiles),
                "compiled_hand_search_unique_names": len({p.name for p in profiles}),
                "secret_box_materialized_targets": len(secret_after.moves),
                "arven_materialized_quick_balls": arven_after.ledger.exchangeable.count(
                    quick_ball_class,
                    "hand",
                ),
                "stale_witness_rejected": stale_witness_rejected,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
