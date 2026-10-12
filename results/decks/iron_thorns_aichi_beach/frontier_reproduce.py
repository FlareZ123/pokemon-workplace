"""Independent labeled-physical Iron Thorns Beach-versus-DCE oracle."""
from __future__ import annotations

from itertools import combinations
from fractions import Fraction
from math import isclose

from tools.iron_thorns_beach_frontier import BeachCounts, beach_fallback, exact


def physical(counts: BeachCounts) -> dict[str, Fraction]:
    cards = tuple(
        (letter, index)
        for letter, size in zip("ITGMDSBP", counts.cats)
        for index in range(size)
    )
    keys = (
        "ideal_attack", "strict_attack", "spare_attack",
        "strict_failed_held_beach", "strict_failed_search_beach",
        "spare_failed_held_beach", "spare_failed_search_beach", "total",
    )
    mass = dict.fromkeys(keys, 0)
    for opening in combinations(cards, counts.opener):
        if not any(name == "I" for name, _ in opening):
            continue
        active = next(card for card in opening if card[0] == "I")
        hand0 = set(opening) - {active}
        unused = set(cards) - set(opening)
        for prizes in combinations(sorted(unused), counts.prizes):
            deck0 = unused - set(prizes)
            for draw in sorted(deck0):
                hand = [name for name, _ in hand0 | {draw}]
                deck = [name for name, _ in deck0 - {draw}]
                mass["total"] += 1
                can_gh = "G" in hand or ("T" in hand and "G" in deck)
                mountain = "M" in hand or "M" in deck
                dce = "D" in hand or "D" in deck
                free = (
                    ("D" in hand and "M" in hand)
                    or ("D" in hand and can_gh and mountain)
                )
                paid = "D" not in hand and can_gh and mountain and dce
                spare_gh = hand.count("G") - int("G" in hand)
                spare_tag = hand.count("T") - int("G" not in hand)
                decisions = {
                    "ideal": free or paid,
                    "strict": free or (paid and hand.count("S") >= 2),
                    "spare": free or (
                        paid and hand.count("S") + spare_gh + spare_tag >= 2
                    ),
                }
                for policy, attack in decisions.items():
                    if attack:
                        mass[policy + "_attack"] += 1
                    elif policy in ("strict", "spare"):
                        if "B" in hand:
                            mass[policy + "_failed_held_beach"] += 1
                        elif can_gh and "B" in deck:
                            mass[policy + "_failed_search_beach"] += 1
    total = mass["total"]
    assert total > 0
    print("Independent physical-state count:", total)
    return {key: Fraction(value, total) for key, value in mass.items()}


def verify() -> None:
    toy_cases = (
        BeachCounts(n=11, iron=2, tag=1, gh=1, mountain=1,
                    dce=1, safe=2, beach=1, opener=3, prizes=2),
        BeachCounts(n=12, iron=2, tag=2, gh=2, mountain=1,
                    dce=1, safe=1, beach=2, opener=3, prizes=2),
        BeachCounts(n=12, iron=2, tag=1, gh=2, mountain=1,
                    dce=2, safe=2, beach=1, opener=4, prizes=2),
    )
    for case in toy_cases:
        assert exact(case) == physical(case), case
        print("PASS: grouped model equals chronological physical oracle", case)

    for safe in (0, 6, 12, 19, 30):
        dce_candidate = exact(BeachCounts(dce=2, beach=1, safe=safe))
        beach_candidate = exact(BeachCounts(dce=1, beach=2, safe=safe))
        assert dce_candidate["strict_attack"] > beach_candidate["strict_attack"]
        assert beach_fallback(beach_candidate, "strict") > beach_fallback(
            dce_candidate, "strict"
        )
        print(
            f"PASS: safe={safe}, two-DCE attack="
            f"{float(dce_candidate['strict_attack']):.9%}, fallback="
            f"{float(beach_fallback(dce_candidate, 'strict')):.9%}; "
            f"two-Beach attack={float(beach_candidate['strict_attack']):.9%}, "
            f"fallback={float(beach_fallback(beach_candidate, 'strict')):.9%}"
        )
    attack_delta = (
        dce_candidate["strict_attack"] - beach_candidate["strict_attack"]
    )
    fallback_delta = (
        beach_fallback(beach_candidate, "strict")
        - beach_fallback(dce_candidate, "strict")
    )
    assert fallback_delta > 0 and attack_delta > 0

    a = exact(BeachCounts(dce=2, beach=1, safe=12))
    b = exact(BeachCounts(dce=1, beach=2, safe=12))
    threshold = (
        (a["strict_attack"] - b["strict_attack"])
        / (beach_fallback(b, "strict") - beach_fallback(a, "strict"))
    )
    assert isclose(float(threshold), 0.3695048538341463, abs_tol=1e-13)
    print("PASS: value-threshold fraction", threshold, "=", float(threshold))


if __name__ == "__main__":
    verify()
