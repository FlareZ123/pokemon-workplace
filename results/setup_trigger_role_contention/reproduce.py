from __future__ import annotations

from fractions import Fraction
from itertools import combinations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from setup_trigger_role_contention import (  # noqa: E402
    analyze_opening_trigger_role,
    scan_literal_bench_trigger_basics,
)


def brute_force(
    *,
    deck_size: int,
    opening_size: int,
    trigger_basics: int,
    other_basics: int,
    required_triggers: int = 1,
    available_bench_slots: int = 5,
) -> tuple[Fraction, Fraction, Fraction]:
    cards = (
        [("trigger", i) for i in range(trigger_basics)]
        + [("other", i) for i in range(other_basics)]
        + [
            ("filler", i)
            for i in range(deck_size - trigger_basics - other_basics)
        ]
    )
    all_hands = list(combinations(cards, opening_size))
    valid = 0
    naive = 0
    role_aware = 0

    for hand in all_hands:
        support_count = sum(kind == "trigger" for kind, _ in hand)
        other_count = sum(kind == "other" for kind, _ in hand)
        if support_count + other_count == 0:
            continue
        valid += 1

        retained = support_count - int(other_count == 0 and support_count > 0)
        if min(support_count, available_bench_slots) >= required_triggers:
            naive += 1
        if min(retained, available_bench_slots) >= required_triggers:
            role_aware += 1

    return (
        Fraction(valid, len(all_hands)),
        Fraction(naive, valid),
        Fraction(role_aware, valid),
    )


def validate_exact_model() -> None:
    cases = (
        dict(deck_size=8, opening_size=3, trigger_basics=2, other_basics=2),
        dict(
            deck_size=9,
            opening_size=4,
            trigger_basics=3,
            other_basics=1,
            required_triggers=2,
        ),
        dict(
            deck_size=10,
            opening_size=4,
            trigger_basics=4,
            other_basics=2,
            required_triggers=2,
            available_bench_slots=1,
        ),
    )
    for case in cases:
        exact = analyze_opening_trigger_role(**case)
        brute = brute_force(**case)
        assert exact.valid_start_probability == brute[0]
        assert exact.naive_success_given_valid == brute[1]
        assert exact.role_aware_success_given_valid == brute[2]
        assert (
            exact.active_role_overstatement_given_valid
            == exact.naive_success_given_valid - exact.role_aware_success_given_valid
        )


def pct(value: Fraction) -> str:
    return f"{float(value):.6%}"


def main() -> None:
    validate_exact_model()

    print("One trigger Basic, increasing total Basic count")
    for other_basics in (3, 7, 11):
        result = analyze_opening_trigger_role(
            trigger_basics=1,
            other_basics=other_basics,
        )
        print(
            f"1 + {other_basics}: valid={pct(result.valid_start_probability)} "
            f"naive={pct(result.naive_success_given_valid)} "
            f"role-aware={pct(result.role_aware_success_given_valid)} "
            f"overstatement={pct(result.active_role_overstatement_given_valid)}"
        )

    print("\nFixed four total Basics, varying trigger-Basic share")
    for trigger_basics in (1, 2, 3, 4):
        result = analyze_opening_trigger_role(
            trigger_basics=trigger_basics,
            other_basics=4 - trigger_basics,
        )
        print(
            f"{trigger_basics} trigger + {4-trigger_basics} other: "
            f"naive={pct(result.naive_success_given_valid)} "
            f"role-aware={pct(result.role_aware_success_given_valid)} "
            f"overstatement={pct(result.active_role_overstatement_given_valid)}"
        )

    catalog = scan_literal_bench_trigger_basics(ROOT / "resources")
    assert catalog["print_count"] == 123
    assert catalog["unique_names"] == 48
    assert catalog["gameplay_variants"] == 51
    for name in ("Tapu Lele-GX", "Dedenne-GX", "Crobat V", "Lumineon V", "Jirachi-EX"):
        assert name in catalog["names"]
    assert "Shaymin-EX" not in catalog["names"]

    print("\nLiteral legal Expanded hand-to-Bench trigger catalog")
    print(
        f"prints={catalog['print_count']} names={catalog['unique_names']} "
        f"gameplay_variants={catalog['gameplay_variants']}"
    )


if __name__ == "__main__":
    main()
