from __future__ import annotations

from fractions import Fraction
from itertools import combinations
from math import comb
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from bench_trigger_access import analyze_bench_trigger_access  # noqa: E402


def brute_force(
    *,
    deck_size: int,
    opening_size: int,
    prize_count: int,
    extra_random_draws: int,
    trigger_basics: int,
    other_basics: int,
    hand_connectors: int,
    direct_bench_connectors: int,
    available_bench_slots: int = 1,
) -> tuple[Fraction, Fraction, Fraction, Fraction, Fraction]:
    cards = (
        [("trigger", i) for i in range(trigger_basics)]
        + [("other", i) for i in range(other_basics)]
        + [("hand", i) for i in range(hand_connectors)]
        + [("direct", i) for i in range(direct_bench_connectors)]
        + [
            ("filler", i)
            for i in range(
                deck_size
                - trigger_basics
                - other_basics
                - hand_connectors
                - direct_bench_connectors
            )
        ]
    )

    valid_openings = 0
    total_sequences = 0
    naive = 0
    zone_aware = 0
    role_aware = 0
    exact = 0

    for opening in combinations(cards, opening_size):
        opening_set = set(opening)
        open_trigger = sum(kind == "trigger" for kind, _ in opening)
        open_other = sum(kind == "other" for kind, _ in opening)
        open_hand = sum(kind == "hand" for kind, _ in opening)
        open_direct = sum(kind == "direct" for kind, _ in opening)
        if open_trigger + open_other == 0:
            continue
        valid_openings += 1
        retained = open_trigger - int(open_other == 0 and open_trigger > 0)
        after_open = [card for card in cards if card not in opening_set]

        for prizes in combinations(after_open, prize_count):
            prize_set = set(prizes)
            after_prizes = [card for card in after_open if card not in prize_set]
            prize_trigger = sum(kind == "trigger" for kind, _ in prizes)

            for draws in combinations(after_prizes, extra_random_draws):
                total_sequences += 1
                draw_trigger = sum(kind == "trigger" for kind, _ in draws)
                draw_hand = sum(kind == "hand" for kind, _ in draws)
                draw_direct = sum(kind == "direct" for kind, _ in draws)
                searchable = trigger_basics - open_trigger - prize_trigger - draw_trigger

                role_naive_in_hand = open_trigger + draw_trigger
                role_aware_in_hand = retained + draw_trigger
                hand_in_hand = open_hand + draw_hand
                any_connector = hand_in_hand + open_direct + draw_direct

                n = role_naive_in_hand > 0 or (any_connector > 0 and searchable > 0)
                z = role_naive_in_hand > 0 or (hand_in_hand > 0 and searchable > 0)
                r = role_aware_in_hand > 0 or (hand_in_hand > 0 and searchable > 0)
                e = r and available_bench_slots > 0

                naive += int(n)
                zone_aware += int(z)
                role_aware += int(r)
                exact += int(e)

    all_openings = comb(deck_size, opening_size)
    return (
        Fraction(valid_openings, all_openings),
        Fraction(naive, total_sequences),
        Fraction(zone_aware, total_sequences),
        Fraction(role_aware, total_sequences),
        Fraction(exact, total_sequences),
    )


def validate() -> None:
    cases = (
        dict(
            deck_size=9,
            opening_size=3,
            prize_count=2,
            extra_random_draws=1,
            trigger_basics=2,
            other_basics=2,
            hand_connectors=1,
            direct_bench_connectors=1,
        ),
        dict(
            deck_size=10,
            opening_size=3,
            prize_count=2,
            extra_random_draws=2,
            trigger_basics=1,
            other_basics=3,
            hand_connectors=2,
            direct_bench_connectors=1,
        ),
        dict(
            deck_size=9,
            opening_size=3,
            prize_count=2,
            extra_random_draws=1,
            trigger_basics=2,
            other_basics=2,
            hand_connectors=1,
            direct_bench_connectors=1,
            available_bench_slots=0,
        ),
    )
    for case in cases:
        exact = analyze_bench_trigger_access(**case)
        brute = brute_force(**case)
        assert exact.valid_start_probability == brute[0]
        assert exact.naive_access_given_valid == brute[1]
        assert exact.zone_aware_access_given_valid == brute[2]
        assert exact.role_aware_access_given_valid == brute[3]
        assert exact.exact_access_given_valid == brute[4]
        assert (
            exact.combined_overstatement_given_valid
            == exact.naive_access_given_valid - exact.exact_access_given_valid
        )
        assert (
            exact.combined_overstatement_given_valid
            == exact.direct_to_bench_overstatement_given_valid
            + exact.active_role_overstatement_given_valid
            + exact.bench_capacity_overstatement_given_valid
        )


def pct(value: Fraction) -> str:
    return f"{float(value):.6%}"


def main() -> None:
    validate()

    scenarios = (
        ("4 hand + 4 direct connectors", 4, 4),
        ("4 hand connectors", 4, 0),
        ("4 direct connectors", 0, 4),
    )
    for label, hand, direct in scenarios:
        result = analyze_bench_trigger_access(
            trigger_basics=1,
            other_basics=3,
            hand_connectors=hand,
            direct_bench_connectors=direct,
        )
        print(label)
        print(f"  naive:      {pct(result.naive_access_given_valid)}")
        print(f"  zone-aware: {pct(result.zone_aware_access_given_valid)}")
        print(f"  role-aware: {pct(result.role_aware_access_given_valid)}")
        print(f"  exact:      {pct(result.exact_access_given_valid)}")
        print(f"  combined overstatement: {pct(result.combined_overstatement_given_valid)}")


if __name__ == "__main__":
    main()
