"""Reproduce and validate timed Prize-rescue access results."""

from __future__ import annotations

from itertools import permutations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from prize_rescue_deadline import (  # noqa: E402
    conditional_deadline_failure_probability_given_valid_start,
    deadline_failure_probability_given_valid_start,
)
from prize_rescue_start_condition import (  # noqa: E402
    conditional_collapse_probability_given_valid_start,
)


def pct(value: float) -> str:
    return f"{100 * value:.6f}%"


def exhaustive_deadline_probabilities(
    deck_size: int,
    prize_count: int,
    *,
    starter_cards: int,
    critical_starter: int,
    critical_nonstarter: int,
    rescue_starter: int,
    rescue_nonstarter: int,
    opening_hand_size: int,
    cards_seen_by_window: tuple[int, ...],
) -> tuple[float, float]:
    """Enumerate every labeled deck permutation for a small regression case."""
    cards: list[tuple[bool, bool, bool]] = []
    cards += [(True, False, True)] * critical_starter
    cards += [(False, False, True)] * critical_nonstarter
    cards += [(True, True, False)] * rescue_starter
    cards += [(False, True, False)] * rescue_nonstarter
    cards += [(True, False, False)] * (
        starter_cards - critical_starter - rescue_starter
    )
    cards += [(False, False, False)] * (
        deck_size - starter_cards - critical_nonstarter - rescue_nonstarter
    )

    accepted = 0
    any_critical = 0
    failed = 0
    window_count = len(cards_seen_by_window)

    for order in permutations(range(deck_size)):
        opening = order[:opening_hand_size]
        if not any(cards[index][0] for index in opening):
            continue
        accepted += 1

        prizes = order[opening_hand_size : opening_hand_size + prize_count]
        critical_prized = sum(cards[index][2] for index in prizes)
        if critical_prized == 0:
            continue
        any_critical += 1

        rescue_prized = sum(cards[index][1] for index in prizes)
        rescue_total = rescue_starter + rescue_nonstarter
        if critical_prized > rescue_total - rescue_prized or critical_prized > window_count:
            failed += 1
            continue

        rescuers_seen = sum(cards[index][1] for index in opening)
        draw_order = order[opening_hand_size + prize_count :]
        previous_seen = opening_hand_size
        feasible = True

        for window_index, cards_seen in enumerate(cards_seen_by_window, start=1):
            draw_start = previous_seen - opening_hand_size
            draw_end = cards_seen - opening_hand_size
            rescuers_seen += sum(
                cards[index][1] for index in draw_order[draw_start:draw_end]
            )
            required_by_now = max(
                0, critical_prized - (window_count - window_index)
            )
            if rescuers_seen < required_by_now:
                feasible = False
                break
            previous_seen = cards_seen

        if not feasible:
            failed += 1

    return failed / accepted, failed / any_critical


def validate() -> None:
    cases = [
        dict(
            deck_size=8,
            prize_count=2,
            starter_cards=3,
            critical_starter=0,
            critical_nonstarter=2,
            rescue_starter=0,
            rescue_nonstarter=2,
            opening_hand_size=2,
            cards_seen_by_window=(3, 4),
        ),
        dict(
            deck_size=8,
            prize_count=2,
            starter_cards=3,
            critical_starter=1,
            critical_nonstarter=1,
            rescue_starter=1,
            rescue_nonstarter=1,
            opening_hand_size=2,
            cards_seen_by_window=(3, 4),
        ),
    ]

    for case in cases:
        exact_overall = deadline_failure_probability_given_valid_start(**case)
        exact_conditional = conditional_deadline_failure_probability_given_valid_start(
            **case
        )
        brute_overall, brute_conditional = exhaustive_deadline_probabilities(**case)
        if abs(exact_overall - brute_overall) > 1e-15:
            raise AssertionError((case, exact_overall, brute_overall))
        if abs(exact_conditional - brute_conditional) > 1e-15:
            raise AssertionError((case, exact_conditional, brute_conditional))


def main() -> None:
    validate()

    base = dict(
        deck_size=60,
        prize_count=6,
        starter_cards=12,
        critical_starter=0,
        critical_nonstarter=4,
        rescue_starter=0,
        opening_hand_size=7,
    )

    print("Four non-starter critical singletons, 12 starters, exposure windows 8/9/10")
    print("rescuers | topology failure | deadline failure | overall deadline failure")
    for rescuers in range(1, 5):
        topology = conditional_collapse_probability_given_valid_start(
            **base,
            rescue_nonstarter=rescuers,
        )
        deadline = conditional_deadline_failure_probability_given_valid_start(
            **base,
            rescue_nonstarter=rescuers,
            cards_seen_by_window=(8, 9, 10),
        )
        overall = deadline_failure_probability_given_valid_start(
            **base,
            rescue_nonstarter=rescuers,
            cards_seen_by_window=(8, 9, 10),
        )
        print(
            f"{rescuers:8d} | {pct(topology):>16} | {pct(deadline):>16} | {pct(overall):>24}"
        )

    print("\nTwo non-starter rescuers, four criticals: random-exposure sensitivity")
    topology = conditional_collapse_probability_given_valid_start(
        **base,
        rescue_nonstarter=2,
    )
    print(f"Topology-only conditional failure: {pct(topology)}")
    print("cards seen by Supporter window | conditional deadline failure | overall deadline failure")
    for windows in [
        (8, 9, 10),
        (8, 9, 10, 11, 12),
        (10, 13, 16),
        (12, 18, 24),
    ]:
        conditional = conditional_deadline_failure_probability_given_valid_start(
            **base,
            rescue_nonstarter=2,
            cards_seen_by_window=windows,
        )
        overall = deadline_failure_probability_given_valid_start(
            **base,
            rescue_nonstarter=2,
            cards_seen_by_window=windows,
        )
        print(
            f"{'/'.join(map(str, windows)):>30} | {pct(conditional):>28} | {pct(overall):>24}"
        )

    print("\nCritical-count sensitivity: two rescuers, exposure windows 8/9/10")
    print("criticals | topology failure | conditional deadline failure")
    for criticals in range(1, 6):
        params = dict(base)
        params["critical_nonstarter"] = criticals
        topology = conditional_collapse_probability_given_valid_start(
            **params,
            rescue_nonstarter=2,
        )
        deadline = conditional_deadline_failure_probability_given_valid_start(
            **params,
            rescue_nonstarter=2,
            cards_seen_by_window=(8, 9, 10),
        )
        print(f"{criticals:9d} | {pct(topology):>16} | {pct(deadline):>28}")


if __name__ == "__main__":
    main()
