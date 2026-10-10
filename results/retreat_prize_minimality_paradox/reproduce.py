"""Unknown-Prize guaranteed Retreat can vanish under naive minimality pruning."""
from __future__ import annotations

from itertools import combinations, product
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from board_object_kernel import make_board, make_pokemon
from results.retreat_action_enumeration.robust_prize_oracle import (
    BEHIND, TIED, action_set, make_case,
)


def minimal(actions: set[tuple[str, ...]]) -> set[tuple[str, ...]]:
    """Retain physically inclusion-minimal legal payment actions."""
    return {
        payment
        for payment in actions
        if not any(
            set(smaller) < set(payment)
            for smaller in actions
        )
    }


def witness() -> None:
    opponent = make_board(make_pokemon("opponent", "Opponent"))
    state = make_case(("counter", "basic"), 2, 3, ("Stage1",))
    unknown, info = action_set(state, opponent, 2)
    tied, tied_info = action_set(state, opponent, 2, TIED)
    behind, behind_info = action_set(state, opponent, 2, BEHIND)

    assert unknown == tied & behind == {("basic", "counter")}
    assert tied == {("basic", "counter")}
    assert behind == {("counter",), ("basic", "counter")}
    assert minimal(tied) == {("basic", "counter")}
    assert minimal(behind) == {("counter",)}
    assert minimal(tied) & minimal(behind) == set()
    assert minimal(unknown) == unknown
    assert not info.information_complete
    assert tied_info.information_complete and behind_info.information_complete


def exhaustive() -> dict[str, int]:
    opponent = make_board(make_pokemon("opponent", "Opponent"))
    pool = ("counter", "reversal", "dce", "basic")
    subsets = tuple(
        subset for n in range(5) for subset in combinations(pool, n)
    )
    tags = (
        ("Stage1",), ("Basic",),
        ("Stage1", "RuleBox"),
        ("Stage1", "Pokemon-GX", "RuleBox"),
    )
    checked = had_guaranteed = paradox_cases = vanished_payments = 0
    for subset, counter_cache, reversal_cache, holder, cost in product(
        subsets, (1, 2), (1, 3), tags, range(7),
    ):
        state = make_case(subset, counter_cache, reversal_cache, holder)
        unknown, _ = action_set(state, opponent, cost)
        tied, _ = action_set(state, opponent, cost, TIED)
        behind, _ = action_set(state, opponent, cost, BEHIND)
        assert unknown == tied & behind, (subset, holder, cost)
        # The full unknown-context frontier is the set intersection.
        guaranteed_minimal = minimal(unknown)
        invalid_algorithm = minimal(tied) & minimal(behind)
        if unknown:
            had_guaranteed += 1
        lost = guaranteed_minimal - invalid_algorithm
        if lost:
            paradox_cases += 1
            vanished_payments += len(lost)
        checked += 1
    assert checked == 1792 and paradox_cases > 0
    return {
        "checked_cases": checked,
        "cases_with_guaranteed_actions": had_guaranteed,
        "paradox_cases": paradox_cases,
        "guaranteed_minimal_actions_lost": vanished_payments,
    }


def main() -> None:
    witness()
    results = exhaustive()
    print("Unknown-Prize minimality intersection paradox: PASS")
    print(results)


if __name__ == "__main__":
    main()
