"""Zero printed-Energy attacks are a valid Energy-route readiness input.

Combines the card data normalization with existing exact Energy-route evaluator.
"""

from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from free_attack_energy_normalizer import (  # noqa: E402
    normalized_attack_cost,
)
from energy_action_budget import (  # noqa: E402
    EnergyRouteProfile,
    EnergyRouteType,
    evaluate_energy_routes,
    unit,
)

printed = {}
for id_, set_ in (("sv8pt5-4", "sv8pt5"), ("me2pt5-16", "me2pt5"),
                  ("me1-71", "me1"), ("swsh12-136", "swsh12")):
    group = json.loads((ROOT / "resources" / "cards" / "en" / f"{set_}.json")
                       .read_text(encoding="utf-8"))
    printed[id_] = next(card for card in group if card["id"] == id_)


def selected(id_: str, attack_name: str) -> dict:
    return next(a for a in printed[id_]["attacks"] if a["name"] == attack_name)


manual = EnergyRouteType(
    name="once-per-turn manual basic",
    copies=1,
    profiles=(EnergyRouteProfile(
        units=(unit("G"),),
        resource_costs=(("manual_attachment", 1),),
    ),),
)
for id_, attack_name in (
    ("sv8pt5-4", "Itchy Pollen"),
    ("me2pt5-16", "Itchy Pollen"),
    ("me1-71", "Pow-Pow Punching"),
):
    row = selected(id_, attack_name)
    assert normalized_attack_cost(row) == ()
    no_routes = evaluate_energy_routes((), {}, (), ())
    assert no_routes.exact_feasible
    assert no_routes.typed_resource_ignorant_feasible
    assert no_routes.raw_unit_count_reachable
    assert no_routes.witness == ()
    assert no_routes.minimum_unmet_symbols == 0

    # Even when optional unrelated energy actions are listed, no action is necessary.
    with_route = evaluate_energy_routes(
        normalized_attack_cost(row), {"manual_attachment": 0}, {"Basic"}, (manual,)
    )
    assert with_route.exact_feasible
    assert with_route.witness == ()
    assert with_route.minimum_unmet_symbols == 0

apex = evaluate_energy_routes(
    normalized_attack_cost(selected("swsh12-136", "Apex Dragon")),
    {"manual_attachment": 0},
    {"Dragon"},
    (),
)
assert not apex.exact_feasible
assert apex.minimum_unmet_symbols == 3
assert not apex.raw_unit_count_reachable

print("PASS: zero-Energy Budew and Tyrogue require no route actions.")
print("PASS: Regidrago Apex Dragon still requires three typed units.")
