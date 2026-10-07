"""Reproduce Pokémon Checkup's deferred Knock Out batch boundary."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from checkup_execution_kernel import (  # noqa: E402
    CheckupBoard,
    CheckupPokemon,
    CounterMutation,
    MutationKind,
    execute_checkup_schedule,
)
from special_condition_state import CHECKUP_CONDITION_BLOCK  # noqa: E402


def main() -> None:
    board = CheckupBoard(
        (
            CheckupPokemon("a-target", hp=100, damage_counters=9),
            CheckupPokemon("b-target", hp=100, damage_counters=9),
            CheckupPokemon("garganacl", hp=180, damage_counters=0),
            CheckupPokemon("froslass", hp=90, damage_counters=0),
        )
    )

    effects = {
        "Freezing Shroud": (
            CounterMutation(
                "freezing-shroud",
                MutationKind.PUT,
                ("a-target", "b-target", "garganacl"),
                1,
            ),
        ),
        "Blessed Salt": (
            CounterMutation(
                "blessed-salt",
                MutationKind.HEAL,
                ("a-target", "garganacl"),
                2,
            ),
        ),
    }

    execution = execute_checkup_schedule(
        board,
        (
            "Freezing Shroud",
            "Blessed Salt",
            CHECKUP_CONDITION_BLOCK,
        ),
        effect_mutations=effects,
    )

    first = execution.snapshots[0]
    assert set(first.zero_hp_ids) == {"a-target", "b-target"}
    assert first.board.get("a-target").remaining_hp == 0
    assert first.board.get("b-target").remaining_hp == 0

    second = execution.snapshots[1]
    assert "a-target" not in second.zero_hp_ids
    assert second.board.get("a-target").damage_counters == 8
    assert second.board.get("a-target").remaining_hp == 20
    assert second.board.get("b-target").remaining_hp == 0

    assert execution.knocked_out_ids == ("b-target",)
    assert {row.object_id for row in execution.final_board.pokemon} == {
        "a-target",
        "b-target",
        "garganacl",
        "froslass",
    }

    print("intermediate zero-HP batch:", first.zero_hp_ids)
    print("final zero-HP batch:", execution.knocked_out_ids)
    print(
        "a-target final remaining HP:",
        execution.final_board.get("a-target").remaining_hp,
    )
    print("checkup deferred-KO regression passed")


if __name__ == "__main__":
    main()
