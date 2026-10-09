"""Resolve documented direct action turn-ending channels."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from board_object_kernel import make_board, make_pokemon
from direct_action_turn_end import close_after_completed_source_effect
from turn_action_budget import TurnAction, TurnActionBudget


def main() -> None:
    base = TurnActionBudget()

    for print_id in ("swsh1-181", "sv5-143", "swsh7-142"):
        done = close_after_completed_source_effect(
            ROOT / "resources", source_print_id=print_id,
            channel="item_effect", budget=base,
        )
        assert done.budget.turn_ended
        assert done.budget.supporter_plays_used == 0
        assert not done.budget.can(TurnAction.ATTACK)

    # Merely playing Lumiose City as the turn's Stadium does NOT close
    # the turn. Its subsequent search effect is a separate activation.
    stadium_played = base.consume(TurnAction.STADIUM_PLAY)
    assert stadium_played is not None
    assert stadium_played.can(TurnAction.ATTACK)
    activated = close_after_completed_source_effect(
        ROOT / "resources", source_print_id="me3-77",
        channel="stadium_activation", budget=stadium_played,
        active_stadium_print_id="me3-77",
    )
    assert activated.budget.turn_ended
    assert activated.budget.stadium_plays_used == 1
    assert activated.budget.supporter_plays_used == 0

    # Pokémon Research Lab has the same activated-Stadium semantics.
    research_lab = close_after_completed_source_effect(
        ROOT / "resources", source_print_id="sm11-205",
        channel="stadium_activation", budget=base,
        active_stadium_print_id="sm11-205",
    )
    assert research_lab.budget.turn_ended
    assert research_lab.budget.stadium_plays_used == 0

    for print_id, name, ability in (
        ("sv1-125", "Koraidon ex", "Dino Cry"),
        ("swsh1-138", "Zacian V", "Intrepid Sword"),
        ("sm11-173", "Munchlax", "Snack Search"),
    ):
        board = make_board(make_pokemon("source", name, print_id=print_id))
        done = close_after_completed_source_effect(
            ROOT / "resources", source_print_id=print_id,
            channel="ability_use", budget=base, player_board=board,
            ability_object_id="source", ability_name=ability,
        )
        assert done.budget.turn_ended
        assert done.action_name == ability
        assert done.budget.manual_energy_attachments_used == 0

    # A Stadium cannot be treated as an Item, nor can a stale or replaced
    # Stadium's activation be used.
    invalid = [
        dict(source_print_id="me3-77", channel="item_effect"),
        dict(source_print_id="sv1-196", channel="item_effect"),
        dict(
            source_print_id="me3-77", channel="stadium_activation",
            active_stadium_print_id="sm11-205",
        ),
    ]
    for kwargs in invalid:
        try:
            close_after_completed_source_effect(
                ROOT / "resources", budget=base, **kwargs
            )
        except ValueError:
            pass
        else:
            raise AssertionError(f"invalid channel/print accepted: {kwargs}")

    active = make_board(
        make_pokemon("source", "Koraidon ex", print_id="sv1-125")
    )
    try:
        close_after_completed_source_effect(
            ROOT / "resources", source_print_id="sv1-125",
            channel="ability_use", budget=base, player_board=active,
            ability_object_id="source", ability_name="Dino Cry",
            suppressed_ability_object_ids=frozenset({"source"}),
        )
    except ValueError:
        pass
    else:
        raise AssertionError("suppressed Ability was allowed to execute")

    print("direct_action_turn_end regression: PASS")
    print("Items, Stadium activations and Abilities close without extra quota")
    print("playing a Stadium alone does not close the turn")


if __name__ == "__main__":
    main()
