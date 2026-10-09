"""SFT: paid Quick plus no-discard Nest Basic searches."""
from __future__ import annotations

import json
import sys
from dataclasses import replace
from fractions import Fraction
from itertools import combinations
from math import comb
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from build_expanded_legality_baseline import classify_effective_legality
from gothitelle_core_board_joint_access import exact_core_board_access
from gothitelle_quick_nest_joint_board import QuickNestSetup, exact_quick_nest_board


def exhaustive(case: QuickNestSetup) -> tuple[Fraction, ...]:
    labels = "".join(
        category * count
        for category, count in zip("GTCOQSNX", case.categories)
    )
    universe = set(range(case.total))
    denominator = (
        comb(case.total, case.opening)
        * comb(case.total - case.opening, case.prizes)
        * (case.total - case.opening - case.prizes)
    )
    masses = [Fraction(0) for _ in range(5)]
    for opener in combinations(range(case.total), case.opening):
        if not any(labels[i] == "O" for i in opener):
            continue
        outside = universe - set(opener)
        for prizes in combinations(sorted(outside), case.prizes):
            deck = outside - set(prizes)
            for first in deck:
                observed = tuple(opener) + (first,)
                names = {labels[i] for i in observed}
                if not {"Q", "S"} <= names:
                    continue
                ordinary = sum(labels[i] == "O" for i in observed)
                need_g = int("G" not in names)
                need_o = max(0, 4 - ordinary)
                count = need_g + need_o
                if count > 2 or (count == 2 and "N" not in names):
                    continue
                live = deck - {first}
                # Both searches remove separate unprized physical Basics.
                valid = True
                for target in "G" * need_g + "O" * need_o:
                    chosen = next(
                        (i for i in live if labels[i] == target), None
                    )
                    if chosen is None:
                        valid = False
                        break
                    live = live - {chosen}
                if not valid:
                    continue
                branch = (
                    0 if count == 0
                    else 1 if count == 1 and need_o
                    else 2 if count == 1
                    else 3 if need_o == 2
                    else 4
                )
                successes = sum(
                    ("T" in names or labels[i] == "T")
                    and ("C" in names or labels[i] == "C")
                    for i in live
                )
                masses[branch] += Fraction(successes, len(live))
    return tuple(mass / denominator for mass in masses)


def main() -> None:
    rows = json.loads(
        (ROOT / "resources" / "cards" / "en" / "sv1.json")
        .read_text(encoding="utf-8")
    )
    nest = next(card for card in rows if card["id"] == "sv1-181")
    assert nest["name"] == "Nest Ball"
    assert classify_effective_legality(nest)[0] == "Legal"
    assert (
        "Search your deck for a Basic Pokémon and put it onto your Bench"
        in " ".join(nest["rules"])
    )
    print("PASS: Nest Ball legal direct-Bench Basic search")

    small = (
        QuickNestSetup(
            total=12, opening=7, prizes=1,
            gothita=1, gothitelle=1, rare_candy=1,
            other_basics=4, quick_ball=1, sky_field=1, nest_ball=1,
        ),
        QuickNestSetup(
            total=13, opening=7, prizes=2,
            gothita=2, gothitelle=1, rare_candy=1,
            other_basics=4, quick_ball=2, sky_field=1, nest_ball=2,
        ),
    )
    for case in small + (replace(small[0], prizes=0),):
        odds = exact_quick_nest_board(case)
        analytic = (
            odds.complete_without_search, odds.quick_search_core,
            odds.quick_search_gothita, odds.quick_nest_two_cores,
            odds.quick_nest_mixed,
        )
        assert analytic == exhaustive(case)
        print("PASS: independent physical-labeled search/prize paths", case)

    base = QuickNestSetup()
    baseline = exact_core_board_access(base.one_quick_projection())
    trials = [
        exact_quick_nest_board(replace(base, nest_ball=n))
        for n in range(5)
    ]
    assert trials[0].per_attempt == baseline.per_attempt
    assert all(
        trials[i+1].per_attempt > trials[i].per_attempt
        for i in range(4)
    )
    second_differences = [
        trials[i+2].per_attempt - 2*trials[i+1].per_attempt
        + trials[i].per_attempt
        for i in range(3)
    ]
    assert (
        second_differences[0] == second_differences[1]
        == second_differences[2] < 0
    )
    assert exact_quick_nest_board(
        replace(base, quick_ball=0)
    ).per_attempt == 0
    for n, odds in enumerate(trials):
        print(
            f"PASS Nest={n}: joint per attempt "
            f"{100*float(odds.per_attempt):.12f}% "
            f"second-search gain {100*float(odds.nest_increment):.12f} pp"
        )
    print("PASS: exactly quadratic concave Nest-count probability")
    print("gothitelle_quick_nest_joint_board regression: PASS")


if __name__ == "__main__":
    main()
