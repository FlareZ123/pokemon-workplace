"""Bind exact named-Pokémon Ability guards to validated physical Active/Bench state.

The result only establishes whether the named guard is satisfied. Other Ability
costs, targeting, timing and external restrictions belong to the caller.
"""
from __future__ import annotations

import argparse
import json
import unittest
from pathlib import Path
from typing import Any

from bench_named_ability_dependencies import build
from board_object_kernel import BoardState, make_pokemon


def named_guard_status(
    board: BoardState, source_object_id: str, guard: dict[str, Any]
) -> dict[str, Any]:
    board.validate()
    source = board.get(source_object_id)
    needed = set(guard["required_names"])
    min_bench = int(guard["minimum_bench_slots"])

    if source.card_name != guard["source_name"]:
        status = "source_name_mismatch"
    elif source.print_id not in guard["print_ids"]:
        status = "unverified_source_print"
    elif min_bench > board.bench_capacity:
        status = "capacity_impossible"
    else:
        eligible_ids = (
            board.bench_ids
            if guard["location"] == "on your bench"
            else (board.active_id, *board.bench_ids)
        )
        available_names = {board.get(i).card_name for i in eligible_ids}
        if not needed.issubset(available_names):
            status = "missing_named_requirements"
        elif not source.abilities_enabled:
            status = "source_ability_suppressed"
        else:
            status = "named_guard_satisfied"

    names_in_zone = {
        board.get(i).card_name
        for i in (
            board.bench_ids
            if guard["location"] == "on your bench"
            else (board.active_id, *board.bench_ids)
        )
    }
    return {
        "status": status,
        "named_guard_satisfied": status == "named_guard_satisfied",
        "minimum_bench_slots": min_bench,
        "current_capacity": board.bench_capacity,
        "missing_names": sorted(needed - names_in_zone),
        "other_effect_requirements_evaluated": False,
    }


def board_with(
    active_name: str, active_print: str, bench: tuple[str, ...], capacity: int,
    *, source_abilities_enabled: bool = True
) -> BoardState:
    active = make_pokemon(
        "active", active_name, print_id=active_print,
        abilities_enabled=source_abilities_enabled,
    )
    benched = tuple(
        make_pokemon(f"bench{i}", name) for i, name in enumerate(bench)
    )
    board = BoardState(
        active_id="active",
        bench_ids=tuple(p.object_id for p in benched),
        objects=(active, *benched),
        bench_capacity=capacity,
    )
    board.validate()
    return board


class NamedGuardBoardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        entries = build(Path("resources"))["entries"]
        cls.regigigas = next(
            x for x in entries
            if x["source_name"] == "Regigigas"
            and x["ability"] == "Ancient Wisdom"
        )
        cls.lunatone = next(
            x for x in entries
            if x["source_name"] == "Lunatone"
            and x["ability"] == "Lunar Cycle"
            and "me1-74" in x["print_ids"]
        )

    def test_all_six_regi_names_fit_with_five_bench(self) -> None:
        bench = tuple(self.regigigas["required_names"])
        board = board_with("Regigigas", "swsh10-130", bench, 5)
        result = named_guard_status(board, "active", self.regigigas)
        self.assertEqual(result["status"], "named_guard_satisfied")
        self.assertFalse(result["other_effect_requirements_evaluated"])

    def test_cap_four_or_three_is_structural_obstruction(self) -> None:
        needed = tuple(self.regigigas["required_names"])
        for cap in (4, 3):
            board = board_with("Regigigas", "swsh10-130", needed[:cap], cap)
            result = named_guard_status(board, "active", self.regigigas)
            self.assertEqual(result["status"], "capacity_impossible")
            self.assertEqual(len(result["missing_names"]), 5-cap)

    def test_pair_guard_changes_with_bench_presence(self) -> None:
        paired = board_with("Lunatone", "me1-74", ("Solrock",), 1)
        missing = board_with("Lunatone", "me1-74", ("Bidoof",), 1)
        self.assertEqual(
            named_guard_status(paired, "active", self.lunatone)["status"],
            "named_guard_satisfied",
        )
        self.assertEqual(
            named_guard_status(missing, "active", self.lunatone)["status"],
            "missing_named_requirements",
        )

    def test_source_print_and_ability_suppression_are_distinct(self) -> None:
        bench = ("Solrock",)
        suppressed = board_with(
            "Lunatone", "me1-74", bench, 1, source_abilities_enabled=False
        )
        unknown_print = board_with("Lunatone", "sm3-68", bench, 1)
        self.assertEqual(
            named_guard_status(suppressed, "active", self.lunatone)["status"],
            "source_ability_suppressed",
        )
        self.assertEqual(
            named_guard_status(unknown_print, "active", self.lunatone)["status"],
            "unverified_source_print",
        )

    def test_on_bench_clause_uses_bench_only(self) -> None:
        hypothetical = {
            "source_name": "A",
            "print_ids": ["test-A"],
            "required_names": ["B"],
            "location": "on your bench",
            "minimum_bench_slots": 1,
        }
        board = board_with("A", "test-A", ("B",), 1)
        self.assertEqual(
            named_guard_status(board, "active", hypothetical)["status"],
            "named_guard_satisfied",
        )
        board2 = board_with("A", "test-A", ("C",), 1)
        self.assertEqual(
            named_guard_status(board2, "active", hypothetical)["status"],
            "missing_named_requirements",
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        unittest.main(argv=["bench_named_guard_board"], verbosity=2)
    else:
        guards = build(Path("resources"))["entries"]
        regigigas = next(
            x for x in guards if x["source_name"] == "Regigigas"
            and x["ability"] == "Ancient Wisdom"
        )
        names = tuple(regigigas["required_names"])
        result = {
            "default_five": named_guard_status(
                board_with("Regigigas", "swsh10-130", names, 5),
                "active", regigigas,
            ),
            "collapsed_four": named_guard_status(
                board_with("Regigigas", "swsh10-130", names[:4], 4),
                "active", regigigas,
            ),
            "parallel_three": named_guard_status(
                board_with("Regigigas", "swsh10-130", names[:3], 3),
                "active", regigigas,
            ),
        }
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
