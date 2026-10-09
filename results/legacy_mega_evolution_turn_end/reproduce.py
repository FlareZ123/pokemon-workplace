"""Printed legacy Mega Evolution and Spirit Link turn-boundary tests."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from board_object_kernel import (
    EnergyAttachment, ToolAttachment, evolve, make_board, make_pokemon,
)
from legacy_mega_evolution_turn_end import resolve_evolution_turn_boundary
from turn_action_budget import TurnAction, TurnActionBudget


def run_evolution(
    *, from_name: str, to_name: str, to_print: str,
    tool_name: str | None = None,
    tool_print: str | None = None,
    tool_active: bool = True,
    with_energy: bool = False,
):
    tool = (
        ToolAttachment("tool1", tool_name, print_id=tool_print)
        if tool_name is not None
        else None
    )
    energy = (
        (EnergyAttachment("energy1", "Fire Energy", ("Fire",)),)
        if with_energy else ()
    )
    base_pokemon = make_pokemon(
        "evolving", from_name, tool=tool, tool_effect_enabled=tool_active,
        energy=energy, damage_counters=3,
    )
    before = make_board(base_pokemon)
    after = evolve(
        before, "evolving", new_card_name=to_name, new_print_id=to_print
    )
    assert after is not None
    return resolve_evolution_turn_boundary(
        ROOT / "resources",
        before=before, after=after, object_id="evolving",
        budget=TurnActionBudget(),
    )


def main() -> None:
    # The original XY Mega rule is a turn closure on evolution.
    bare = run_evolution(
        from_name="Charizard-EX", to_name="M Charizard-EX",
        to_print="xy2-13", with_energy=True,
    )
    assert bare.legacy_rule == "mega_evolution"
    assert bare.ended_by_evolution and bare.budget.turn_ended
    assert bare.budget.remaining(TurnAction.SUPPORTER) == 0
    assert not bare.budget.can(TurnAction.ATTACK)

    # A matching attached Spirit Link suppresses the turn end. This Tool
    # stays on the same physical Pokémon throughout its evolution.
    linked = run_evolution(
        from_name="Charizard-EX", to_name="M Charizard-EX",
        to_print="xy2-13", tool_name="Charizard Spirit Link",
        tool_print="xy12-75", with_energy=True,
    )
    assert linked.legacy_rule == "mega_evolution"
    assert not linked.ended_by_evolution
    assert linked.prevented_by_spirit_link
    assert linked.spirit_link_print_id == "xy12-75"
    assert linked.budget.can(TurnAction.ATTACK)

    # The wrong species' Spirit Link can be attached as a Tool yet does
    # not prevent this evolution from ending the turn.
    wrong = run_evolution(
        from_name="Charizard-EX", to_name="M Charizard-EX",
        to_print="xy2-13", tool_name="Manectric Spirit Link",
        tool_print="xy4-100",
    )
    assert wrong.ended_by_evolution

    # Jamming Tower-like Tool suppression defeats the matching link.
    suppressed = run_evolution(
        from_name="Charizard-EX", to_name="M Charizard-EX",
        to_print="xy2-13", tool_name="Charizard Spirit Link",
        tool_print="xy12-75", tool_active=False,
    )
    assert suppressed.ended_by_evolution
    assert suppressed.spirit_link_print_id is None

    # A name-only Tool without trustworthy print identity cannot grant
    # the exemption in this print-specific executor.
    unknown = run_evolution(
        from_name="Charizard-EX", to_name="M Charizard-EX",
        to_print="xy2-13", tool_name="Charizard Spirit Link",
    )
    assert unknown.ended_by_evolution

    primal_bare = run_evolution(
        from_name="Kyogre-EX", to_name="Primal Kyogre-EX",
        to_print="xy5-55",
    )
    assert primal_bare.legacy_rule == "primal_reversion"
    assert primal_bare.ended_by_evolution

    primal_link = run_evolution(
        from_name="Kyogre-EX", to_name="Primal Kyogre-EX",
        to_print="xy5-55", tool_name="Kyogre Spirit Link",
        tool_print="xy5-132",
    )
    assert not primal_link.ended_by_evolution
    assert primal_link.prevented_by_spirit_link

    # A 2026 30th Celebration M Gardevoir-EX reprint removes the legacy
    # label but retains the exact turn-ending wording, so it still closes.
    unlabeled = run_evolution(
        from_name="Gardevoir-EX", to_name="M Gardevoir-EX",
        to_print="me55c-106m",
    )
    assert unlabeled.legacy_rule == "mega_evolution"
    assert unlabeled.ended_by_evolution
    covered_reprint = run_evolution(
        from_name="Gardevoir-EX", to_name="M Gardevoir-EX",
        to_print="me55c-106m", tool_name="Gardevoir Spirit Link",
        tool_print="xy5-130",
    )
    assert covered_reprint.prevented_by_spirit_link
    assert not covered_reprint.ended_by_evolution

    # Modern Mega Evolution ex has a *three-Prize* rule, no evolution
    # turn-end trigger, even though its card has the MEGA subtype.
    newer = run_evolution(
        from_name="Ivysaur", to_name="Mega Venusaur ex",
        to_print="me1-3",
    )
    assert newer.legacy_rule is None and not newer.ended_by_evolution
    assert newer.budget.can(TurnAction.ATTACK)

    # A legacy Rule is not enough to excuse an illegal evolutionary
    # chain. Upstream timing checks and this origin check are distinct.
    base = make_board(make_pokemon("p", "Charizard-EX"))
    illegal_after = evolve(
        base, "p", new_card_name="Primal Kyogre-EX", new_print_id="xy5-55"
    )
    assert illegal_after is not None
    try:
        resolve_evolution_turn_boundary(
            ROOT / "resources", before=base, after=illegal_after,
            object_id="p", budget=TurnActionBudget(),
        )
    except ValueError as e:
        assert "evolution origin" in str(e)
    else:
        raise AssertionError("incorrect printed evolution origin was accepted")

    print("legacy_mega_evolution_turn_end regression: PASS")
    print("XY Mega and Primal Rule close turn; matching active Spirit Link exempts")
    print("wrong/suppressed/unproven Tool does not exempt; newer Mega ex differs")


if __name__ == "__main__":
    main()
