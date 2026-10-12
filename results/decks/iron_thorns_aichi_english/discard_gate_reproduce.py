"""Independent physical-card oracle and Iron Thorns discard-gate regressions."""
from __future__ import annotations

from itertools import combinations
from fractions import Fraction
from math import comb, isclose

from tools.iron_thorns_gnh_discard_gate import Counts, exact, reach


def exhaustive(counts: Counts) -> dict[str, Fraction]:
    """Deal labeled opening, Prize cards, then normal draw in physical order."""
    cards = tuple(
        (name, i)
        for name, copies in zip("ITGMDSP", counts.cats)
        for i in range(copies)
    )
    mass = {
        key: 0 for key in (
            "direct", "no_discard", "paid_ideal", "paid_strict",
            "paid_spare", "total",
        )
    }
    for opening in combinations(cards, counts.opener):
        if not any(card[0] == "I" for card in opening):
            continue
        active = next(card for card in opening if card[0] == "I")
        hand_before_draw = set(opening) - {active}
        remaining = set(cards) - set(opening)
        for prizes in combinations(sorted(remaining), counts.prizes):
            deck_before_draw = remaining - set(prizes)
            for drawn in sorted(deck_before_draw):
                hand = hand_before_draw | {drawn}
                deck = deck_before_draw - {drawn}
                h = [name for name, _ in hand]
                d = [name for name, _ in deck]
                mass["total"] += 1

                if "M" in h and "D" in h:
                    mass["direct"] += 1
                    continue
                if "M" not in h and "M" not in d:
                    continue
                if "D" not in h and "D" not in d:
                    continue
                if "G" in h:
                    gh_from_hand = True
                elif "T" in h and "G" in d:
                    gh_from_hand = False
                else:
                    continue
                if "D" in h:
                    mass["no_discard"] += 1
                    continue

                mass["paid_ideal"] += 1
                if h.count("S") >= 2:
                    mass["paid_strict"] += 1
                spare_gh = h.count("G") - int(gh_from_hand)
                spare_tag = h.count("T") - int(not gh_from_hand)
                if h.count("S") + spare_gh + spare_tag >= 2:
                    mass["paid_spare"] += 1

    worlds = mass["total"]
    assert worlds > 0
    print("Physical oracle worlds:", worlds)
    return {name: Fraction(weight, worlds) for name, weight in mass.items()}


def verify() -> None:
    toy_cases = (
        Counts(n=11, iron=2, tag=1, gh=1, mountain=1,
               dce=1, safe=2, opener=3, prizes=2),
        Counts(n=12, iron=2, tag=2, gh=2, mountain=1,
               dce=2, safe=2, opener=3, prizes=2),
        Counts(n=12, iron=2, tag=2, gh=2, mountain=1,
               dce=1, safe=3, opener=4, prizes=2),
    )
    for case in toy_cases:
        found = exact(case)
        physical = exhaustive(case)
        assert found == physical, (case, found, physical)
        print("PASS: exact category model equals independent physical deal", case)

    expected_ideal = {
        1: 0.33781505711,
        2: 0.38080679951,
        3: 0.39107850627,
    }
    for dce, expected in expected_ideal.items():
        result = exact(Counts(dce=dce, safe=12))
        assert isclose(float(reach(result, "paid_ideal")), expected, abs_tol=1e-10)
        assert (
            result["paid_strict"] <= result["paid_spare"]
            <= result["paid_ideal"]
        ), result
        print(
            f"PASS: DCE={dce} ideal={float(reach(result, 'paid_ideal')):.9%} "
            f"strict={float(reach(result, 'paid_strict')):.9%} "
            f"spare={float(reach(result, 'paid_spare')):.9%}"
        )

    for safe in (0, 6, 12, 19, 30, 48):
        before, after = (
            exact(Counts(dce=dce, safe=safe)) for dce in (1, 2)
        )
        metrics = ("paid_ideal", "paid_strict", "paid_spare")
        assert all(reach(after, key) >= reach(before, key) for key in metrics)
        assert all(
            reach(result, "paid_strict")
            <= reach(result, "paid_spare")
            <= reach(result, "paid_ideal")
            for result in (before, after)
        )
        print(
            f"PASS: disposable={safe} "
            f"one-DCE strict={float(reach(before, 'paid_strict')):.9%} "
            f"two-DCE strict={float(reach(after, 'paid_strict')):.9%} "
            f"two-DCE spare={float(reach(after, 'paid_spare')):.9%}"
        )


if __name__ == "__main__":
    verify()
