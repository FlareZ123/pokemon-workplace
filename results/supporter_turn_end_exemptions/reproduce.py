"""Print-specific active Ability exemptions for turn-ending Supporters."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from board_object_kernel import make_board, make_pokemon
from supporter_turn_end_exemptions import resolve_completed_supporter_turn
from turn_action_budget import TurnAction, TurnActionBudget


def completed(print_id, board, budget=None, *, suppressed=frozenset()):
    return resolve_completed_supporter_turn(
        ROOT / "resources", supporter_print_id=print_id, player_board=board,
        budget=budget if budget is not None else TurnActionBudget(),
        suppressed_ability_object_ids=suppressed,
    )


def main() -> None:
    neutral = make_board(make_pokemon("a", "Neutral Active"))
    metal = make_board(
        make_pokemon("metal", "Metagross", print_id="sm7-95")
    )
    alcremie = make_board(
        make_pokemon("sweet", "Alcremie", print_id="swsh9-71")
    )
    alt_alcremie = make_board(
        make_pokemon("sweet", "Alcremie", print_id="swsh9tg-TG08")
    )

    steven = completed("sm7-145", neutral)
    assert steven is not None and steven.ended_by_supporter
    assert steven.budget.supporter_plays_used == 1
    assert steven.budget.turn_ended
    assert not steven.budget.can(TurnAction.ATTACK)

    extend = completed("sm7-145", metal)
    assert extend is not None and not extend.ended_by_supporter
    assert extend.exemption_source_print_id == "sm7-95"
    assert extend.budget.supporter_plays_used == 1
    assert extend.budget.can(TurnAction.ATTACK)
    assert not extend.budget.can(TurnAction.SUPPORTER)
    alt_steven = completed("sm7-165", metal)
    assert alt_steven is not None and alt_steven.exempted_by_active_ability

    benched = make_board(
        make_pokemon("pivot", "Pivot"),
        (make_pokemon("metal", "Metagross", print_id="sm7-95"),),
    )
    benched_steven = completed("sm7-145", benched)
    assert benched_steven is not None and benched_steven.ended_by_supporter

    disabled = make_board(
        make_pokemon("metal", "Metagross", print_id="sm7-95",
                     abilities_enabled=False)
    )
    blocked = completed("sm7-145", disabled)
    assert blocked is not None and blocked.ended_by_supporter
    causal_block = completed(
        "sm7-145", metal, suppressed=frozenset({"metal"})
    )
    assert causal_block is not None and causal_block.ended_by_supporter

    for board in (alcremie, alt_alcremie):
        cafe = completed("swsh9-133", board)
        assert cafe is not None
        assert cafe.supporter_name == "Café Master"
        assert cafe.printed_ends_turn and cafe.exempted_by_active_ability
        assert cafe.budget.supporter_plays_used == 1
        assert not cafe.budget.turn_ended and cafe.budget.can(TurnAction.ATTACK)

    bad_cafe = completed("swsh9-133", neutral)
    assert bad_cafe is not None and bad_cafe.ended_by_supporter
    katy = completed("sv1-177", metal)
    assert katy is not None and katy.ended_by_supporter
    assert not katy.exempted_by_active_ability

    ordinary = completed("sv1-166", neutral)
    assert ordinary is not None
    assert not ordinary.printed_ends_turn
    assert ordinary.budget.supporter_plays_used == 1
    assert ordinary.budget.can(TurnAction.ATTACK)

    # A second Supporter is blocked by forced turn closure despite spare
    # quota, but permitted when the relevant Ability prevented closure.
    doubled = TurnActionBudget().with_limit(TurnAction.SUPPORTER, 2)
    force_end = completed("sm7-145", neutral, doubled)
    assert force_end is not None
    assert force_end.budget.supporter_plays_used == 1
    assert not force_end.budget.can(TurnAction.SUPPORTER)
    first = completed("sm7-145", metal, doubled)
    assert first is not None and first.budget.can(TurnAction.SUPPORTER)
    second = completed("sv1-166", metal, first.budget)
    assert second is not None
    assert second.budget.supporter_plays_used == 2
    assert not second.budget.can(TurnAction.SUPPORTER)
    assert second.budget.can(TurnAction.ATTACK)

    print("supporter_turn_end_exemptions regression: PASS")
    print("Steven / Metagross, Café Master / Alcremie, suppression and quota")


if __name__ == "__main__":
    main()
