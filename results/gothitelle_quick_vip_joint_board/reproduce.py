"""SFT: first-turn Quick Ball, Sky Field payload, Battle VIP Pass.

An independent labeled physical-card enumerator checks all four
disjoint numbers of needed Basic searches, including random Prizes
and the exact second-turn draw deck after searching.
"""
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
from gothitelle_quick_vip_joint_board import (
    QuickVIPSetup, exact_quick_vip_board,
)


def exhaustive(case: QuickVIPSetup) -> tuple[Fraction, ...]:
    """Exhaustively enumerate real copy IDs across four time/zone slices."""
    labels = "".join(
        category * count for category, count in zip(
            "GTCOQSVX", case.categories
        )
    )
    universe = set(range(case.total))
    denominator = (
        comb(case.total, case.opening)
        * comb(case.total-case.opening, case.prizes)
        * (case.total-case.opening-case.prizes)
    )
    masses = [Fraction(0) for _ in range(4)]
    for opener in combinations(range(case.total), case.opening):
        if not any(labels[card] == "O" for card in opener):
            continue
        outside = universe-set(opener)
        for prizes in combinations(sorted(outside), case.prizes):
            deck = outside-set(prizes)
            for first in deck:
                seen = tuple(opener)+(first,)
                names = {labels[card] for card in seen}
                if not {"Q", "S"} <= names:
                    continue
                need_g = int("G" not in names)
                need_o = max(
                    0,4-sum(labels[card] == "O" for card in seen)
                )
                required = need_g+need_o
                if required > 3 or (
                    required >= 2 and "V" not in names
                ):
                    continue
                live = deck-{first}
                success = True
                for target in "G"*need_g+"O"*need_o:
                    found = next(
                        (card for card in live if labels[card] == target),
                        None,
                    )
                    if found is None:
                        success = False
                        break
                    live.remove(found)
                if not success:
                    continue
                wins = sum(
                    ("T" in names or labels[card] == "T")
                    and ("C" in names or labels[card] == "C")
                    for card in live
                )
                masses[required] += Fraction(wins, len(live))
    return tuple(value/denominator for value in masses)


def main() -> None:
    cards = json.loads(
        (ROOT/"resources"/"cards"/"en"/"swsh8.json")
        .read_text(encoding="utf-8")
    )
    vip = next(card for card in cards if card["id"]=="swsh8-225")
    text = " ".join(vip["rules"])
    assert vip["name"] == "Battle VIP Pass"
    assert "Item" in vip["subtypes"]
    assert classify_effective_legality(vip)[0] == "Legal"
    assert "only during your first turn" in text
    assert "Search your deck for up to 2 Basic Pokémon" in text
    assert "put them onto your Bench" in text
    print("PASS legal source and first-turn-only direct-Bench search text")

    small = (
        QuickVIPSetup(
            total=12,opening=6,prizes=1,gothita=1,gothitelle=1,
            rare_candy=1,other_basics=4,quick_ball=1,
            sky_field=1,battle_vip_pass=1,
        ),
        QuickVIPSetup(
            total=13,opening=6,prizes=2,gothita=2,gothitelle=1,
            rare_candy=1,other_basics=4,quick_ball=1,
            sky_field=1,battle_vip_pass=2,
        ),
    )
    for case in small+(replace(small[0],prizes=0),):
        odds = exact_quick_vip_board(case)
        analytical = (
            odds.naturally_complete,
            odds.one_basic_search,
            odds.two_basic_searches,
            odds.three_basic_searches,
        )
        assert analytical == exhaustive(case)
        print(
            "PASS labeled first-turn VIP up-to-two-card "
            "search and Prize oracle",case,analytical
        )

    base = QuickVIPSetup()
    one = exact_core_board_access(base.one_quick_projection())
    sweep = [
        exact_quick_vip_board(
            replace(base,battle_vip_pass=n)
        ) for n in range(5)
    ]
    assert sweep[0].per_attempt == one.per_attempt
    assert sweep[0].vip_increment == 0
    assert all(
        sweep[i+1].per_attempt > sweep[i].per_attempt
        for i in range(4)
    )
    assert sweep[4].three_basic_searches > sweep[4].two_basic_searches
    assert exact_quick_vip_board(
        replace(base,quick_ball=0)
    ).per_attempt == 0
    assert exact_quick_vip_board(
        replace(base,sky_field=0)
    ).per_attempt == 0
    for n,odds in enumerate(sweep):
        print(
            f"PASS VIP={n} total="
            f"{100*float(odds.per_attempt):.12f}% "
            f"VIP-marginal={100*float(odds.vip_increment):.12f} pp"
        )
    print(
        "PASS three searched Basics dominate narrow 4-core "
        "Bench setup in the chosen first-eight-card population"
    )
    print("gothitelle_quick_vip_joint_board regression: PASS")


if __name__=="__main__":
    main()
