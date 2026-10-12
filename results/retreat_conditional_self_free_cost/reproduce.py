"""Reproduce conditional free-Retreat source semantics and physical action frontiers."""
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from board_object_kernel import EnergyAttachment, make_board, make_pokemon
from energy_board_conservation import EnergyBoardState
from multicopy_zone_state import ZoneCountState
from retreat_action_enumerator import enumerate_board_derived_retreat_actions
from retreat_conditional_self_free_cost import (
    SOURCES, derive_conditional_self_free_cost,
)
from retreat_cost_semantics import effective_retreat_cost
from retreat_energy_transaction import RetreatEnergyTransactionState
from retreat_environment_modifiers import derive_environment_retreat_modifiers
from turn_action_budget import TurnActionBudget
from unified_state_kernel import make_state


def opponent(tags=()):
    return make_board(make_pokemon("opponent", "Opposing Pokemon", tags=tags))


def source_fixture(source):
    return make_pokemon("holder", source.card_name, print_id=source.print_id)


def source_regression() -> None:
    basic = EnergyAttachment("energy", "Basic Psychic Energy", ("P",))
    cases = {
        "any_energy": dict(energy=(basic,)),
        "damaged": dict(damage_counters=1),
        "stadium": dict(stadium_print_id="swsh2-160"),
        "opponent_v": dict(opponent_tags=("Pokemon VMAX",)),
        "opponent_gx_ex": dict(opponent_tags=("Pokemon-GX",)),
    }

    for source in SOURCES:
        holder = source_fixture(source)
        assert derive_conditional_self_free_cost(holder, opponent()) is None
        assert derive_conditional_self_free_cost(
            make_pokemon(
                "holder", source.card_name, print_id=source.print_id,
                abilities_enabled=False, energy=(basic,), damage_counters=1,
            ),
            opponent(("Pokemon VMAX", "Pokemon-GX")),
            stadium_print_id="swsh2-160",
        ) is None
        assert derive_conditional_self_free_cost(
            make_pokemon("holder", "Incorrect name", print_id=source.print_id),
            opponent(),
        ) is None
        scenario = cases[source.trigger]
        active = make_pokemon(
            "holder", source.card_name, print_id=source.print_id,
            energy=scenario.get("energy", ()),
            damage_counters=scenario.get("damage_counters", 0),
        )
        result = derive_conditional_self_free_cost(
            active, opponent(scenario.get("opponent_tags", ())),
            stadium_print_id=scenario.get("stadium_print_id"),
        )
        assert result is not None and result.no_retreat_cost, source
        assert effective_retreat_cost(5, (result,)) == 0

    wimpod = make_pokemon("w", "Wimpod", print_id="pgo-25")
    assert derive_conditional_self_free_cost(
        wimpod, opponent(("Pokemon VSTAR",)),
    ) is not None
    assert derive_conditional_self_free_cost(
        wimpod, opponent(("Pokemon-GX",)),
    ) is None

    genesect = make_pokemon(
        "g", "Genesect", print_id="sm10-127",
    )
    assert derive_conditional_self_free_cost(
        genesect, opponent(("Pokemon-EX",)),
    ) is not None
    assert derive_conditional_self_free_cost(
        genesect, opponent(("Pokemon V",)),
    ) is None


def physical_retreat_frontier() -> None:
    """Healing removes Sudowoodo's permission to Retreat under Galar Mine."""
    def enumerate_sudowoodo(damage: int):
        holder = make_pokemon(
            "sudowoodo", "Sudowoodo", print_id="swsh10-74",
            damage_counters=damage,
        )
        physical = RetreatEnergyTransactionState(
            unified=make_state({}, turn_budget=TurnActionBudget()),
            energy=EnergyBoardState(
                zones=ZoneCountState.from_mapping({}),
                board=make_board(holder, (make_pokemon("pivot", "Pivot"),)),
                instance_classes=(),
            ),
        )
        return enumerate_board_derived_retreat_actions(
            physical, opponent(), base_retreat_cost=2,
            stadium_print_id="swsh2-160",
        )

    damaged = enumerate_sudowoodo(1)
    healed = enumerate_sudowoodo(0)
    assert damaged.preflight is not None
    assert healed.preflight is not None
    assert damaged.preflight.effective_retreat_cost == 0
    assert healed.preflight.effective_retreat_cost == 4
    assert {
        (action.bench_object_id, action.discard_energy_ids)
        for action in damaged.actions
    } == {("pivot", ())}
    assert healed.actions == ()

    # A Stadium continues to satisfy a *presence* predicate even when the
    # Stadium's own effects are disabled. Its Galar Mine +2 effect is suppressed.
    raichu = make_board(
        make_pokemon("raichu", "Alolan Raichu", print_id="sm4-31")
    )
    with_disabled_stadium = derive_environment_retreat_modifiers(
        raichu, opponent(), stadium_print_id="swsh2-160",
        stadium_effect_enabled=False,
    )
    without_stadium = derive_environment_retreat_modifiers(
        raichu, opponent(), stadium_print_id=None,
    )
    assert effective_retreat_cost(2, with_disabled_stadium) == 0
    assert effective_retreat_cost(2, without_stadium) == 2


def main() -> None:
    source_regression()
    physical_retreat_frontier()
    print("Conditional self free-Retreat source and action regression: PASS")
    print({"print_sources": len(SOURCES), "damaged_cost": 0,
           "healed_cost_under_galar_mine": 4})


if __name__ == "__main__":
    main()
