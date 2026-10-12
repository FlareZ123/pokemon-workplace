"""Physical labeled-card oracle and exact arithmetic regression."""
from collections import Counter
from fractions import Fraction
from itertools import combinations
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from prize_payload_frontier import BASELINE, Payload, coverage, swapped


def brute(
    profile: tuple[Payload, ...], *, basics: int, fillers: int,
    prizes: int, hand: int,
) -> dict[str, Fraction]:
    """Deal accepted physical openings, disjoint Prizes, then one draw."""
    cards: list[tuple[str, bool, str]] = []
    for p in profile:
        cards.extend((p.name, p.basic, "payload") for _ in range(p.copies))
    cards.append(("ball", False, "ball"))
    cards.extend((f"basic_{k}", True, "other") for k in range(basics))
    cards.extend((f"filler_{k}", False, "other") for k in range(fillers))
    counts = Counter()
    worlds = 0

    for opener in combinations(range(len(cards)), hand):
        if not any(cards[k][1] for k in opener):
            continue
        outside_opening = [k for k in range(len(cards)) if k not in opener]
        for prize in combinations(outside_opening, prizes):
            prize_set = set(prize)
            future = [k for k in outside_opening if k not in prize_set]
            prized = Counter(cards[k][0] for k in prize_set)
            missing = [p for p in profile if prized[p.name] == p.copies]
            missing_basic = [p for p in missing if p.basic]
            missing_evo = [p for p in missing if not p.basic]
            for drawn in future:
                worlds += 1
                seen_ball = any(
                    cards[k][2] == "ball" for k in (*opener, drawn)
                )
                if any(prized[p.name] for p in profile):
                    counts["any_payload_print_prized"] += 1
                if not missing:
                    counts["all_payload_types_present"] += 1
                if not missing_evo and (
                    not missing_basic or (len(missing_basic) == 1 and seen_ball)
                ):
                    counts["full_menu_with_visible_ball"] += 1
                dialga = next(p for p in profile if p.name == "Dialga-GX")
                dragapult = next(p for p in profile if p.name == "Dragapult ex")
                if prized[dragapult.name] < dragapult.copies and (
                    prized[dialga.name] < dialga.copies or seen_ball
                ):
                    counts["timeless_phantom_with_visible_ball"] += 1
                if seen_ball:
                    counts["heavy_ball_seen"] += 1
                for p in profile:
                    if prized[p.name]:
                        counts[f"prized_{p.name}"] += 1
                    if prized[p.name] < p.copies or (p.basic and seen_ball):
                        counts[f"covered_{p.name}"] += 1
                    if prized[p.name] == p.copies and p.basic and seen_ball:
                        counts[f"rescued_{p.name}"] += 1

    return {key: Fraction(counts[key], worlds) for key in counts}


def check() -> None:
    for profile in (BASELINE, swapped("Dragapult ex"), swapped("Dialga-GX")):
        total_cards = 12
        other_basics = 2
        filler = total_cards - sum(p.copies for p in profile) - 1 - other_basics
        exact = coverage(
            profile, other_basics=other_basics,
            deck_size=total_cards, prize_count=2, opening_size=3,
        )
        physical = brute(
            profile, basics=other_basics, fillers=filler, prizes=2, hand=3,
        )
        for metric, result in physical.items():
            assert exact[metric] == result, (metric, exact[metric], result)
        print("Toy physical oracle PASS", len(physical), "metrics",
              [(p.name, p.copies) for p in profile])

    baseline = coverage(BASELINE)
    extra_dragapult = coverage(swapped("Dragapult ex"))
    extra_goodra = coverage(swapped("Hisuian Goodra VSTAR"))
    assert baseline["all_payload_types_present"] + baseline["any_payload_print_prized"] == 1
    assert baseline["full_menu_with_visible_ball"] >= baseline["all_payload_types_present"]
    assert extra_dragapult["all_payload_types_present"] > baseline["all_payload_types_present"]
    assert extra_goodra["all_payload_types_present"] > baseline["all_payload_types_present"]
    assert extra_dragapult["covered_Dragapult ex"] > baseline["covered_Dragapult ex"]
    assert (
        extra_dragapult["timeless_phantom_with_visible_ball"]
        > baseline["timeless_phantom_with_visible_ball"]
    )
    assert (
        extra_goodra["timeless_phantom_with_visible_ball"]
        == baseline["timeless_phantom_with_visible_ball"]
    )
    assert baseline["rescued_Dialga-GX"] == baseline["rescued_Kyurem"]
    assert baseline["rescued_Dragapult ex"] == 0
    assert baseline["rescued_Hisuian Goodra VSTAR"] == 0

    print("60-card arithmetic identities PASS")
    for name, result in (
        ("published Regidrago", baseline),
        ("second Dragapult", extra_dragapult),
        ("second Goodra", extra_goodra),
    ):
        print(name)
        for key in (
            "all_payload_types_present",
            "full_menu_with_visible_ball",
            "timeless_phantom_with_visible_ball",
            "heavy_ball_seen",
        ):
            print(" ", key, f"{100*float(result[key]):.9f}%", result[key])


if __name__ == "__main__":
    check()
