from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from energy_action_budget import (  # noqa: E402
    EnergyRouteProfile,
    EnergyRouteType,
    evaluate_energy_routes,
    unit,
)


def load_cards() -> dict[str, dict]:
    cards: dict[str, dict] = {}
    for path in sorted((ROOT / "resources" / "cards" / "en").glob("*.json")):
        for card in json.loads(path.read_text(encoding="utf-8")):
            cards[card["id"]] = card
    return cards


def contains_rule(card: dict, fragment: str) -> bool:
    return any(fragment in rule for rule in card.get("rules", []))


def main() -> None:
    cards = load_cards()

    # Card-pool anchors for the modeled semantics.
    thorns = cards["sv6-77"]
    assert thorns["legalities"]["expanded"] == "Legal"
    assert thorns["attacks"][0]["cost"] == [
        "Lightning",
        "Colorless",
        "Colorless",
    ]

    dce = cards["sm2-166"]
    assert dce["legalities"]["expanded"] == "Legal"
    assert contains_rule(dce, "provides ColorlessColorless Energy")

    thunder_mountain = cards["sm8-191"]
    assert thunder_mountain["legalities"]["expanded"] == "Legal"
    assert contains_rule(
        thunder_mountain,
        "attacks of Lightning Pokémon",
    )
    assert contains_rule(thunder_mountain, "cost Lightning less")

    dde = cards["xy6-97"]
    assert dde["legalities"]["expanded"] == "Legal"
    assert contains_rule(dde, "only be attached to Dragon Pokémon")
    assert contains_rule(dde, "provides only 2 Energy at a time")

    welder = cards["sm10-189"]
    assert welder["legalities"]["expanded"] == "Legal"
    assert contains_rule(welder, "Attach up to 2 Fire Energy cards")

    energy_switch = cards["bw1-94"]
    assert energy_switch["legalities"]["expanded"] == "Legal"
    assert contains_rule(energy_switch, "Move a basic Energy")

    crispin = cards["sv7-133"]
    assert crispin["legalities"]["expanded"] == "Legal"
    assert contains_rule(crispin, "Basic Energy cards of different types")
    assert contains_rule(crispin, "Attach the other to 1 of your Pokémon")

    guzma_hala = cards["sm12-193"]
    assert guzma_hala["legalities"]["expanded"] == "Legal"
    assert contains_rule(
        guzma_hala,
        "search for a Pokémon Tool card and a Special Energy card",
    )

    manual_lightning = EnergyRouteType(
        "manual Lightning Energy",
        2,
        (
            EnergyRouteProfile(
                units=(unit("L"),),
                resource_costs=(("manual_attachment", 1),),
            ),
        ),
    )
    two_manual = evaluate_energy_routes(
        ("C", "C"),
        {"manual_attachment": 1},
        {"Basic"},
        (manual_lightning,),
    )
    assert two_manual.raw_unit_count_reachable
    assert two_manual.typed_resource_ignorant_feasible
    assert not two_manual.exact_feasible
    assert two_manual.minimum_unmet_symbols == 1

    dce_route = EnergyRouteType(
        "manual Double Colorless Energy",
        1,
        (
            EnergyRouteProfile(
                units=(unit("C"), unit("C")),
                resource_costs=(("manual_attachment", 1),),
            ),
        ),
    )
    dce_ready = evaluate_energy_routes(
        ("C", "C"),
        {"manual_attachment": 1},
        {"Basic"},
        (dce_route,),
    )
    assert dce_ready.exact_feasible

    dce_wrong_types = evaluate_energy_routes(
        ("R", "R"),
        {"manual_attachment": 1},
        {"Basic"},
        (dce_route,),
    )
    assert dce_wrong_types.raw_unit_count_reachable
    assert not dce_wrong_types.typed_resource_ignorant_feasible
    assert not dce_wrong_types.exact_feasible

    thunder_route = EnergyRouteType(
        "Thunder Mountain Prism Star",
        1,
        (
            EnergyRouteProfile(
                reductions=(("L", 1),),
                resource_costs=(("stadium_play", 1),),
                required_target_tags=frozenset({"Lightning"}),
            ),
        ),
    )
    thorns_ready = evaluate_energy_routes(
        ("L", "C", "C"),
        {"manual_attachment": 1, "stadium_play": 1},
        {"Lightning", "Basic"},
        (dce_route, thunder_route),
    )
    assert thorns_ready.exact_feasible

    non_lightning = evaluate_energy_routes(
        ("L", "C", "C"),
        {"manual_attachment": 1, "stadium_play": 1},
        {"Basic"},
        (dce_route, thunder_route),
    )
    assert non_lightning.raw_unit_count_reachable
    assert not non_lightning.typed_resource_ignorant_feasible
    assert not non_lightning.exact_feasible

    dde_route = EnergyRouteType(
        "manual Double Dragon Energy",
        1,
        (
            EnergyRouteProfile(
                units=(unit("*"), unit("*")),
                resource_costs=(("manual_attachment", 1),),
                required_target_tags=frozenset({"Dragon"}),
            ),
        ),
    )
    assert evaluate_energy_routes(
        ("R", "W"),
        {"manual_attachment": 1},
        {"Dragon"},
        (dde_route,),
    ).exact_feasible
    non_dragon = evaluate_energy_routes(
        ("R", "W"),
        {"manual_attachment": 1},
        {"Basic"},
        (dde_route,),
    )
    assert non_dragon.raw_unit_count_reachable
    assert not non_dragon.typed_resource_ignorant_feasible
    assert not non_dragon.exact_feasible

    welder_route = EnergyRouteType(
        "Welder attach two Fire",
        1,
        (
            EnergyRouteProfile(
                units=(unit("R"), unit("R")),
                resource_costs=(
                    ("supporter_play", 1),
                    ("fire_energy_in_hand", 2),
                ),
            ),
        ),
    )
    manual_fire = EnergyRouteType(
        "manual Fire Energy",
        1,
        (
            EnergyRouteProfile(
                units=(unit("R"),),
                resource_costs=(
                    ("manual_attachment", 1),
                    ("fire_energy_in_hand", 1),
                ),
            ),
        ),
    )
    welder_three = evaluate_energy_routes(
        ("R", "R", "R"),
        {
            "supporter_play": 1,
            "manual_attachment": 1,
            "fire_energy_in_hand": 3,
        },
        {"Basic"},
        (welder_route, manual_fire),
    )
    assert welder_three.exact_feasible

    welder_short = evaluate_energy_routes(
        ("R", "R", "R"),
        {
            "supporter_play": 1,
            "manual_attachment": 1,
            "fire_energy_in_hand": 2,
        },
        {"Basic"},
        (welder_route, manual_fire),
    )
    assert welder_short.typed_resource_ignorant_feasible
    assert not welder_short.exact_feasible

    switch_route = EnergyRouteType(
        "Energy Switch donor transfer",
        1,
        (
            EnergyRouteProfile(
                units=(unit("L"),),
                resource_costs=(("donor_basic_energy", 1),),
            ),
        ),
    )
    assert not evaluate_energy_routes(
        ("L",),
        {"donor_basic_energy": 0},
        {"Basic"},
        (switch_route,),
    ).exact_feasible
    assert evaluate_energy_routes(
        ("L",),
        {"donor_basic_energy": 1},
        {"Basic"},
        (switch_route,),
    ).exact_feasible

    crispin_compiled = EnergyRouteType(
        "Crispin effect attach plus manual searched Energy",
        1,
        (
            EnergyRouteProfile(
                units=(unit("R"), unit("W")),
                resource_costs=(
                    ("supporter_play", 1),
                    ("manual_attachment", 1),
                    ("two_basic_types_in_deck", 1),
                ),
            ),
        ),
    )
    crispin_ready = evaluate_energy_routes(
        ("R", "W"),
        {
            "supporter_play": 1,
            "manual_attachment": 1,
            "two_basic_types_in_deck": 1,
        },
        {"Basic"},
        (crispin_compiled,),
    )
    assert crispin_ready.exact_feasible
    assert not evaluate_energy_routes(
        ("R", "W"),
        {
            "supporter_play": 1,
            "manual_attachment": 0,
            "two_basic_types_in_deck": 1,
        },
        {"Basic"},
        (crispin_compiled,),
    ).exact_feasible

    guzma_hala_compiled = EnergyRouteType(
        "Guzma & Hala -> DCE + Thunder Mountain -> Volt Cyclone",
        1,
        (
            EnergyRouteProfile(
                units=(unit("C"), unit("C")),
                reductions=(("L", 1),),
                resource_costs=(
                    ("supporter_play", 1),
                    ("discardable_cards", 2),
                    ("manual_attachment", 1),
                    ("stadium_play", 1),
                ),
                required_target_tags=frozenset({"Lightning"}),
            ),
        ),
    )
    iron_thorns_line = evaluate_energy_routes(
        ("L", "C", "C"),
        {
            "supporter_play": 1,
            "discardable_cards": 2,
            "manual_attachment": 1,
            "stadium_play": 1,
        },
        {"Lightning", "Basic"},
        (guzma_hala_compiled,),
    )
    assert iron_thorns_line.exact_feasible
    assert not evaluate_energy_routes(
        ("L", "C", "C"),
        {
            "supporter_play": 1,
            "discardable_cards": 1,
            "manual_attachment": 1,
            "stadium_play": 1,
        },
        {"Lightning", "Basic"},
        (guzma_hala_compiled,),
    ).exact_feasible

    print(
        json.dumps(
            {
                "manual_two_basics": two_manual.exact_feasible,
                "dce_one_attachment": dce_ready.exact_feasible,
                "iron_thorns_dce_thunder_mountain": thorns_ready.exact_feasible,
                "double_dragon_two_typed_symbols": True,
                "welder_plus_manual_three_fire": welder_three.exact_feasible,
                "energy_switch_without_donor": False,
                "crispin_plus_manual_two_types": crispin_ready.exact_feasible,
                "guzma_hala_iron_thorns_compiled_line": iron_thorns_line.exact_feasible,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
