"""SFT: dual-use Gothitelle setup with a fully assembled four-core board."""
from __future__ import annotations

import sys
from dataclasses import replace
from fractions import Fraction
from itertools import combinations
from math import comb
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from gothitelle_dual_use_joint_access import DualUseSetup, exact_dual_use_access
from gothitelle_core_board_joint_access import exact_core_board_access


def exhaustive(case: DualUseSetup) -> tuple[Fraction, Fraction, Fraction]:
    """Independent physical-ID enumerator, including the searched target."""
    labels = "".join(
        category * count for category, count in zip(
            "GTCOQSX", case.categories
        )
    )
    universe = set(range(case.total))
    denominator = (
        comb(case.total, case.opening)
        * comb(case.total - case.opening, case.prizes)
        * (case.total - case.opening - case.prizes)
    )
    sums = [Fraction(0), Fraction(0), Fraction(0)]
    for opener in combinations(range(case.total), case.opening):
        opening_types = {labels[i] for i in opener}
        if "O" not in opening_types:
            continue  # Initial Active must be an ordinary Basic.
        outside = universe - set(opener)
        for prize in combinations(sorted(outside), case.prizes):
            deck = outside - set(prize)
            for first in deck:
                observed = tuple(opener) + (first,)
                types = {labels[i] for i in observed}
                if not {"Q", "S"} <= types:
                    continue
                cores = sum(labels[i] == "O" for i in observed)
                has_g = "G" in types
                if has_g and cores >= 4:
                    target, branch = None, 0
                elif has_g and cores == 3:
                    target, branch = "O", 1
                elif not has_g and cores >= 4:
                    target, branch = "G", 2
                else:
                    continue
                remainder = deck - {first}
                if target is not None:
                    chosen = next(
                        (i for i in remainder if labels[i] == target),
                        None,
                    )
                    if chosen is None:
                        continue
                    remainder = remainder - {chosen}
                successes = sum(
                    ("T" in types or labels[i] == "T")
                    and ("C" in types or labels[i] == "C")
                    for i in remainder
                )
                sums[branch] += Fraction(
                    successes, len(remainder)
                )
    return tuple(x / denominator for x in sums)


def main() -> None:
    cases = (
        DualUseSetup(
            total=12, opening=7, prizes=1,
            gothita=1, gothitelle=1, rare_candy=1,
            other_basics=4, quick_ball=1, sky_field=1,
        ),
        DualUseSetup(
            total=13, opening=7, prizes=2,
            gothita=2, gothitelle=1, rare_candy=1,
            other_basics=4, quick_ball=1, sky_field=2,
        ),
    )
    for case in cases + (replace(cases[0], prizes=0),):
        result = exact_core_board_access(case)
        brute = exhaustive(case)
        assert (
            result.already_complete,
            result.search_core_basic,
            result.search_gothita,
        ) == brute
        print("PASS labeled exact opening/prize/search/T2 enumeration",
              case, brute)
    standard = DualUseSetup()
    coarse = exact_dual_use_access(standard)
    finer = exact_core_board_access(standard)
    assert finer.per_attempt > 0
    assert finer.per_attempt < coarse.per_attempt
    assert exact_core_board_access(
        replace(standard, quick_ball=0)
    ).per_attempt == 0
    assert exact_core_board_access(
        replace(standard, sky_field=0)
    ).per_attempt == 0
    assert exact_core_board_access(
        replace(standard, sky_field=3)
    ).per_attempt > finer.per_attempt
    assert exact_core_board_access(
        replace(standard, other_basics=3)
    ).per_attempt == 0
    print(
        f"PASS example per opener: completed {100*float(finer.already_complete):.9f}%, "
        f"Quick finds ordinary Basic {100*float(finer.search_core_basic):.9f}%, "
        f"Quick finds Gothita {100*float(finer.search_gothita):.9f}%, "
        f"total {100*float(finer.per_attempt):.9f}% "
        f"among legal {100*float(finer.conditional_legal_opener):.9f}%"
    )
    print(
        f"PASS abstract access {100*float(coarse.per_attempt):.9f}% "
        "exceeds stricter four-core turn-one board probability"
    )
    print("gothitelle_core_board_joint_access regression: PASS")


if __name__ == "__main__":
    main()
