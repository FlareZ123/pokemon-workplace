"""SFT: paid second Quick Ball and exact complete-board probability."""
from __future__ import annotations

import sys
from dataclasses import replace
from fractions import Fraction
from itertools import combinations
from math import comb
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from gothitelle_core_board_joint_access import exact_core_board_access
from gothitelle_two_quick_joint_board import TwoQuickSetup, exact_two_quick_board


def exhaustive(case: TwoQuickSetup) -> tuple[Fraction, ...]:
    """Independent labeled Prize and searched-copy enumeration."""
    labels = "".join(
        symbol * count for symbol, count in zip(
            "GTCOQSDX", case.categories
        )
    )
    universe = set(range(case.total))
    divisor = (
        comb(case.total, case.opening)
        * comb(case.total-case.opening, case.prizes)
        * (case.total-case.opening-case.prizes)
    )
    masses = [Fraction(0) for _ in range(5)]
    for opening in combinations(range(case.total), case.opening):
        opening_seen = {labels[i] for i in opening}
        if "O" not in opening_seen:
            continue
        remainder = universe - set(opening)
        for prizes in combinations(sorted(remainder), case.prizes):
            deck = remainder - set(prizes)
            for first in deck:
                observed = tuple(opening) + (first,)
                types = {labels[i] for i in observed}
                if not {"Q", "S"} <= types:
                    continue
                ordinary = sum(labels[i] == "O" for i in observed)
                need_g = int("G" not in types)
                need_o = max(0, 4-ordinary)
                searches = need_g + need_o
                if searches > 2 or (
                    searches == 2 and (
                        sum(labels[i] == "Q" for i in observed) < 2
                        or "D" not in types
                    )
                ):
                    continue
                live = deck - {first}
                needed = "G" * need_g + "O" * need_o
                search_valid = True
                for target in needed:
                    chosen = next(
                        (i for i in live if labels[i] == target), None
                    )
                    if chosen is None:
                        search_valid = False
                        break
                    live = live - {chosen}
                if not search_valid:
                    continue
                branch = (
                    0 if searches == 0
                    else 1 if searches == 1 and need_o
                    else 2 if searches == 1
                    else 3 if need_o == 2
                    else 4
                )
                successes = sum(
                    ("T" in types or labels[i] == "T")
                    and ("C" in types or labels[i] == "C")
                    for i in live
                )
                masses[branch] += Fraction(successes, len(live))
    return tuple(value/divisor for value in masses)


def main() -> None:
    tiny_cases = (
        TwoQuickSetup(
            total=12, opening=7, prizes=1,
            gothita=1, gothitelle=1, rare_candy=1,
            other_basics=4, quick_ball=2, sky_field=1,
            approved_discard=1,
        ),
        TwoQuickSetup(
            total=13, opening=7, prizes=2,
            gothita=2, gothitelle=1, rare_candy=1,
            other_basics=4, quick_ball=2, sky_field=1,
            approved_discard=1,
        ),
    )
    for case in tiny_cases + (replace(tiny_cases[0], prizes=0),):
        result = exact_two_quick_board(case)
        exact_branches = (
            result.complete_without_search, result.single_search_core,
            result.single_search_gothita, result.double_search_two_cores,
            result.double_search_mixed,
        )
        assert exact_branches == exhaustive(case)
        print("PASS independently enumerated physical targets", case,
              exact_branches)

    base = TwoQuickSetup()
    single = exact_core_board_access(base.one_quick_projection())
    zero_fodder = exact_two_quick_board(
        replace(base, approved_discard=0)
    )
    assert zero_fodder.per_attempt == single.per_attempt
    assert zero_fodder.increment_from_second_search == 0

    current = exact_two_quick_board(base)
    assert current.per_attempt > single.per_attempt
    assert current.increment_from_second_search > 0
    increment_four = exact_two_quick_board(
        replace(base, approved_discard=4)
    ).increment_from_second_search
    assert current.increment_from_second_search == 3*increment_four
    assert exact_two_quick_board(
        replace(base, approved_discard=20)
    ).increment_from_second_search == 5*increment_four
    assert exact_two_quick_board(
        replace(base, quick_ball=1)
    ).increment_from_second_search == 0

    print(
        f"PASS one Quick baseline={100*float(single.per_attempt):.12f}% "
        f"two Quick + 12 approved payment cards="
        f"{100*float(current.per_attempt):.12f}% "
        f"increment={100*float(current.increment_from_second_search):.12f} pp "
        f"relative={100*float(current.increment_from_second_search/single.per_attempt):.9f}%"
    )
    print(
        "PASS 8-card timing window makes the extra paid-search contribution "
        "exactly linear in approved-discard copies with filler substitution"
    )
    print("gothitelle_two_quick_joint_board regression: PASS")


if __name__ == "__main__":
    main()
