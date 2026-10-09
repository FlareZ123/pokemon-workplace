"""Exact finite-window Bench release scheduler for sequential named-Ability guards.

First named guard has already resolved; its dispensable Benched prerequisites
can be released. A fixed Active stays. Supporter cleanup can remove a batch
of up to N objects, but only once per turn. Attack cleanup ends the turn.
"""
from __future__ import annotations

import argparse
import json
import unittest
from collections import deque
from dataclasses import dataclass
from typing import Any

from bench_temporal_guard_release_bounds import sequential_budget


@dataclass(frozen=True)
class ReleaseResources:
    item: int = 0
    ability: int = 0
    supporter: int = 0
    attack: int = 0
    supporter_batch_size: int = 2

    def __post_init__(self) -> None:
        if min(self.item, self.ability, self.supporter, self.attack) < 0:
            raise ValueError("release resource counts must be nonnegative")
        if self.supporter_batch_size < 1:
            raise ValueError("supporter batch must be positive")


@dataclass(frozen=True)
class _Node:
    turn: int
    bench_occupants: int
    expendable: int
    arrivals_left: int
    items: int
    abilities: int
    supporters: int
    attacks: int
    supporter_used: bool


@dataclass(frozen=True)
class GuardSchedule:
    reached: bool
    earliest_turn: int | None
    actions: tuple[str, ...]
    states_explored: int


def schedule_second_guard(
    first: frozenset[str],
    second: frozenset[str],
    *,
    active: str,
    bench_capacity: int = 5,
    max_turns: int = 1,
    resources: ReleaseResources = ReleaseResources(),
    supporter_already_used: bool = False,
) -> GuardSchedule:
    """BFS with exact occupancy, remaining cards and typed action windows."""
    if max_turns < 1:
        raise ValueError("max_turns must be positive")
    lower_bound = sequential_budget(
        first, second, capacity=bench_capacity, active=active
    )
    if lower_bound is None:
        return GuardSchedule(False, None, (), 0)

    start = _Node(
        turn=1,
        bench_occupants=len(first) - 1,
        expendable=len(first - second - {active}),
        arrivals_left=len(second - first),
        items=resources.item,
        abilities=resources.ability,
        supporters=resources.supporter,
        attacks=resources.attack,
        supporter_used=supporter_already_used,
    )
    queue = deque([start])
    parents: dict[_Node, tuple[_Node | None, str]] = {start: (None, "")}

    def visit(parent: _Node, child: _Node, action: str) -> None:
        if child not in parents:
            parents[child] = (parent, action)
            queue.append(child)

    while queue:
        node = queue.popleft()
        if node.arrivals_left == 0:
            history = []
            walk = node
            while True:
                prev, step = parents[walk]
                if prev is None:
                    break
                history.append(step)
                walk = prev
            return GuardSchedule(True, node.turn, tuple(reversed(history)), len(parents))

        if node.bench_occupants < bench_capacity:
            visit(
                node,
                _Node(
                    node.turn, node.bench_occupants + 1, node.expendable,
                    node.arrivals_left - 1, node.items, node.abilities,
                    node.supporters, node.attacks, node.supporter_used,
                ),
                "Bench one second-engine Pokémon",
            )

        if node.expendable:
            if node.items:
                visit(
                    node,
                    _Node(
                        node.turn, node.bench_occupants - 1,
                        node.expendable - 1, node.arrivals_left,
                        node.items - 1, node.abilities, node.supporters,
                        node.attacks, node.supporter_used,
                    ),
                    "Item cleanup removes one expendable Bench object",
                )
            if node.abilities:
                visit(
                    node,
                    _Node(
                        node.turn, node.bench_occupants - 1,
                        node.expendable - 1, node.arrivals_left,
                        node.items, node.abilities - 1, node.supporters,
                        node.attacks, node.supporter_used,
                    ),
                    "Ability cleanup removes one expendable Bench object",
                )
            if node.supporters and not node.supporter_used:
                for amount in range(1, min(
                    resources.supporter_batch_size, node.expendable
                ) + 1):
                    visit(
                        node,
                        _Node(
                            node.turn, node.bench_occupants - amount,
                            node.expendable - amount, node.arrivals_left,
                            node.items, node.abilities, node.supporters - 1,
                            node.attacks, True,
                        ),
                        f"Supporter cleanup removes {amount} Bench object(s)",
                    )

        if node.turn < max_turns:
            visit(
                node,
                _Node(
                    node.turn + 1, node.bench_occupants, node.expendable,
                    node.arrivals_left, node.items, node.abilities,
                    node.supporters, node.attacks, False,
                ),
                "Advance to next turn",
            )
            if node.expendable and node.attacks:
                visit(
                    node,
                    _Node(
                        node.turn + 1, node.bench_occupants - 1,
                        node.expendable - 1, node.arrivals_left,
                        node.items, node.abilities, node.supporters,
                        node.attacks - 1, False,
                    ),
                    "Attack cleanup removes one Bench object and ends turn",
                )

    return GuardSchedule(False, None, (), len(parents))


REGI = frozenset((
    "Regigigas", "Regirock", "Regice", "Registeel",
    "Regieleki", "Regidrago",
))
LUNAR = frozenset(("Lunatone", "Solrock"))
TRIO = frozenset(("Uxie", "Mesprit", "Azelf"))


class ReleaseScheduleTests(unittest.TestCase):
    def test_two_discards_one_supporter_same_turn(self) -> None:
        result = schedule_second_guard(
            REGI, LUNAR, active="Regigigas",
            resources=ReleaseResources(supporter=1),
        )
        self.assertTrue(result.reached)
        self.assertEqual(result.earliest_turn, 1)
        self.assertIn(
            "Supporter cleanup removes 2 Bench object(s)", result.actions
        )
        self.assertEqual(result.actions.count("Bench one second-engine Pokémon"), 2)

    def test_supporter_one_target_only_cannot_finish_turn_one(self) -> None:
        result = schedule_second_guard(
            REGI, LUNAR, active="Regigigas",
            resources=ReleaseResources(supporter=1, supporter_batch_size=1),
        )
        self.assertFalse(result.reached)
        with_item = schedule_second_guard(
            REGI, LUNAR, active="Regigigas",
            resources=ReleaseResources(
                supporter=1, supporter_batch_size=1, item=1
            ),
        )
        self.assertTrue(with_item.reached)

    def test_three_departures_timing_and_supporter_quota(self) -> None:
        one = schedule_second_guard(
            REGI, TRIO, active="Regigigas",
            resources=ReleaseResources(supporter=1),
        )
        self.assertFalse(one.reached)
        supplement = schedule_second_guard(
            REGI, TRIO, active="Regigigas",
            resources=ReleaseResources(supporter=1, item=1),
        )
        self.assertTrue(supplement.reached)
        two_one_turn = schedule_second_guard(
            REGI, TRIO, active="Regigigas",
            resources=ReleaseResources(supporter=2),
        )
        self.assertFalse(two_one_turn.reached)
        two_two_turns = schedule_second_guard(
            REGI, TRIO, active="Regigigas", max_turns=2,
            resources=ReleaseResources(supporter=2),
        )
        self.assertTrue(two_two_turns.reached)
        self.assertEqual(two_two_turns.earliest_turn, 2)

    def test_attack_release_ends_turn(self) -> None:
        turn_one = schedule_second_guard(
            REGI, LUNAR, active="Regigigas",
            resources=ReleaseResources(supporter=1, supporter_batch_size=1, attack=1),
        )
        self.assertFalse(turn_one.reached)
        turn_two = schedule_second_guard(
            REGI, LUNAR, active="Regigigas", max_turns=2,
            resources=ReleaseResources(supporter=1, supporter_batch_size=1, attack=1),
        )
        self.assertTrue(turn_two.reached)
        self.assertEqual(turn_two.earliest_turn, 2)

    def test_supporter_spent_on_first_engine_blocks_same_turn_cleanup(self) -> None:
        first_turn = schedule_second_guard(
            REGI, LUNAR, active="Regigigas",
            resources=ReleaseResources(supporter=1),
            supporter_already_used=True,
        )
        self.assertFalse(first_turn.reached)
        next_turn = schedule_second_guard(
            REGI, LUNAR, active="Regigigas",
            max_turns=2, resources=ReleaseResources(supporter=1),
            supporter_already_used=True,
        )
        self.assertTrue(next_turn.reached)
        self.assertEqual(next_turn.earliest_turn, 2)

    def test_expanded_capacity_removes_release_requirement(self) -> None:
        result = schedule_second_guard(
            REGI, TRIO, active="Regigigas", bench_capacity=8
        )
        self.assertTrue(result.reached)
        self.assertEqual(result.earliest_turn, 1)
        self.assertFalse(any("cleanup" in action for action in result.actions))

    def test_reject_unsupported_or_invalid_counts(self) -> None:
        self.assertFalse(schedule_second_guard(
            REGI, TRIO, active="Regigigas", bench_capacity=4,
            resources=ReleaseResources(item=10),
        ).reached)
        with self.assertRaises(ValueError):
            ReleaseResources(supporter_batch_size=0)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        unittest.main(argv=["bench_batch_release_schedule"], verbosity=2)
    else:
        rows: dict[str, Any] = {}
        for key, second, resources, turns, spent in (
            ("lunar_one_giovanni", LUNAR, ReleaseResources(supporter=1), 1, False),
            ("trio_one_giovanni", TRIO, ReleaseResources(supporter=1), 1, False),
            ("trio_giovanni_plus_item", TRIO, ReleaseResources(supporter=1, item=1), 1, False),
            ("trio_two_giovanni_one_turn", TRIO, ReleaseResources(supporter=2), 1, False),
            ("trio_two_giovanni_two_turns", TRIO, ReleaseResources(supporter=2), 2, False),
            ("lunar_giovanni_window_spent", LUNAR, ReleaseResources(supporter=1), 1, True),
            ("lunar_giovanni_window_spent_next_turn", LUNAR, ReleaseResources(supporter=1), 2, True),
        ):
            outcome = schedule_second_guard(
                REGI, second, active="Regigigas", max_turns=turns,
                resources=resources, supporter_already_used=spent,
            )
            rows[key] = {
                "reached": outcome.reached,
                "earliest_turn": outcome.earliest_turn,
                "actions": list(outcome.actions),
            }
        print(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()
