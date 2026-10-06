"""Reproduce timed Prize-rescue results and validations."""

from __future__ import annotations

from itertools import combinations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from timed_prize_rescue import timed_rescue_probabilities  # noqa: E402


def pct(value: float) -> str:
    return f"{100 * value:.6f}%"


def brute_force(
    deck_size: int,
    prize_count: int,
    *,
    starter_cards: int,
    critical_starter: int,
    critical_nonstarter: int,
    rescue_starter: int,
    rescue_nonstarter: int,
    opening_hand_size: int,
    extra_random_draws: int,
    supporter_opportunities: int,
) -> tuple[float, float]:
    cards: list[tuple[bool, bool, bool]] = []
    cards += [(True, True, False)] * critical_starter
    cards += [(False, True, False)] * critical_nonstarter
    cards += [(True, False, True)] * rescue_starter
    cards += [(False, False, True)] * rescue_nonstarter
    cards += [(True, False, False)] * (
        starter_cards - critical_starter - rescue_starter
    )
    cards += [(False, False, False)] * (
        deck_size - starter_cards - critical_nonstarter - rescue_nonstarter
    )

    all_cards = set(range(deck_size))
    accepted = failures = any_critical = 0

    for hand_tuple in combinations(range(deck_size), opening_hand_size):
        hand = set(hand_tuple)
        if not any(cards[index][0] for index in hand):
            continue
        after_hand = all_cards - hand

        for prize_tuple in combinations(sorted(after_hand), prize_count):
            prizes = set(prize_tuple)
            after_prizes = after_hand - prizes

            for draw_tuple in combinations(sorted(after_prizes), extra_random_draws):
                draws = set(draw_tuple)
                accepted += 1
                critical_prized = sum(cards[index][1] for index in prizes)
                if critical_prized == 0:
                    continue
                any_critical += 1
                rescuers_accessible = sum(
                    cards[index][2] for index in hand | draws
                )
                if (
                    critical_prized > supporter_opportunities
                    or rescuers_accessible < critical_prized
                ):
                    failures += 1

    return failures / accepted, any_critical / accepted


def validate() -> None:
    exact = timed_rescue_probabilities(
        10,
        2,
        starter_cards=4,
        critical_starter=1,
        critical_nonstarter=2,
        rescue_starter=1,
        rescue_nonstarter=1,
        opening_hand_size=3,
        extra_random_draws=2,
        supporter_opportunities=2,
    )
    brute_failure, brute_any = brute_force(
        10,
        2,
        starter_cards=4,
        critical_starter=1,
        critical_nonstarter=2,
        rescue_starter=1,
        rescue_nonstarter=1,
        opening_hand_size=3,
        extra_random_draws=2,
        supporter_opportunities=2,
    )
    if abs(exact.failure_probability - brute_failure) > 1e-15:
        raise AssertionError((exact.failure_probability, brute_failure))
    if abs(exact.any_critical_prized - brute_any) > 1e-15:
        raise AssertionError((exact.any_critical_prized, brute_any))
    if abs(exact.state_mass - 1.0) > 1e-14:
        raise AssertionError(exact.state_mass)

    topology = timed_rescue_probabilities(
        60,
        6,
        starter_cards=12,
        critical_starter=0,
        critical_nonstarter=4,
        rescue_starter=0,
        rescue_nonstarter=2,
        extra_random_draws=47,
        supporter_opportunities=99,
    )
    if abs(topology.failure_probability - 0.010576751696984328) > 1e-15:
        raise AssertionError(topology.failure_probability)


def main() -> None:
    validate()

    print("Four non-starter criticals, two non-starter rescuers, 12 starters")
    print("random draws | failure | failure given any critical Prized")
    for draws in [0, 1, 2, 5, 10, 20, 47]:
        result = timed_rescue_probabilities(
            60,
            6,
            starter_cards=12,
            critical_starter=0,
            critical_nonstarter=4,
            rescue_starter=0,
            rescue_nonstarter=2,
            extra_random_draws=draws,
            supporter_opportunities=2,
        )
        print(
            f"{draws:12d} | {pct(result.failure_probability):>10} | "
            f"{pct(result.conditional_failure_probability):>33}"
        )

    print(
        "\nFour non-starter criticals, four non-starter rescuers, "
        "all rescuers eventually seen"
    )
    print(
        "supporter opportunities | failure | "
        "failure given any critical Prized"
    )
    for opportunities in [1, 2, 3, 4]:
        result = timed_rescue_probabilities(
            60,
            6,
            starter_cards=12,
            critical_starter=0,
            critical_nonstarter=4,
            rescue_starter=0,
            rescue_nonstarter=4,
            extra_random_draws=47,
            supporter_opportunities=opportunities,
        )
        print(
            f"{opportunities:23d} | {pct(result.failure_probability):>10} | "
            f"{pct(result.conditional_failure_probability):>33}"
        )


if __name__ == "__main__":
    main()
