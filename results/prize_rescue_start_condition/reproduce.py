"""Reproduce valid-start-conditioned Prize-rescue results and validations."""

from __future__ import annotations

from itertools import combinations
from math import comb
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from prize_rescue_start_condition import (  # noqa: E402
    any_critical_prized_probability_given_valid_start,
    collapse_probability_given_valid_start,
    conditioned_prize_state_distribution,
    conditional_collapse_probability_given_valid_start,
)


def pct(value: float) -> str:
    return f"{100 * value:.6f}%"


def unconditioned_joint_probability(
    deck_size: int, prize_count: int, critical_singletons: int, rescue_copies: int,
    critical_prized: int, rescuers_prized: int,
) -> float:
    filler = deck_size - critical_singletons - rescue_copies
    filler_prized = prize_count - critical_prized - rescuers_prized
    if not 0 <= filler_prized <= filler:
        return 0.0
    return (comb(critical_singletons, critical_prized) * comb(rescue_copies, rescuers_prized)
            * comb(filler, filler_prized) / comb(deck_size, prize_count))


def unconditioned_collapse_probability(
    deck_size: int, prize_count: int, critical_singletons: int, rescue_copies: int
) -> float:
    probability = 0.0
    for critical_prized in range(min(critical_singletons, prize_count) + 1):
        for rescuers_prized in range(min(rescue_copies, prize_count - critical_prized) + 1):
            if critical_prized > rescue_copies - rescuers_prized:
                probability += unconditioned_joint_probability(
                    deck_size, prize_count, critical_singletons, rescue_copies,
                    critical_prized, rescuers_prized
                )
    return probability


def unconditioned_any_critical_probability(
    deck_size: int, prize_count: int, critical_singletons: int
) -> float:
    return 1.0 - comb(deck_size - critical_singletons, prize_count) / comb(deck_size, prize_count)


def exhaustive_probabilities(
    deck_size: int, prize_count: int, opening_hand_size: int, starter_cards: int,
    critical_starter: int, critical_nonstarter: int, rescue_starter: int, rescue_nonstarter: int,
) -> tuple[float, float]:
    categories: list[tuple[str, bool]] = []
    categories += [("CS", True)] * critical_starter
    categories += [("CN", False)] * critical_nonstarter
    categories += [("RS", True)] * rescue_starter
    categories += [("RN", False)] * rescue_nonstarter
    categories += [("FS", True)] * (starter_cards - critical_starter - rescue_starter)
    categories += [("FN", False)] * (deck_size - starter_cards - critical_nonstarter - rescue_nonstarter)

    starters = {i for i, (_, is_starter) in enumerate(categories) if is_starter}
    total_rescue = rescue_starter + rescue_nonstarter
    all_cards = set(range(deck_size))
    accepted_layouts = collapse_layouts = critical_layouts = 0

    for opening_tuple in combinations(range(deck_size), opening_hand_size):
        opening = set(opening_tuple)
        if not opening & starters:
            continue
        remaining = all_cards - opening
        for prize_tuple in combinations(sorted(remaining), prize_count):
            prizes = set(prize_tuple)
            accepted_layouts += 1
            critical_prized = sum(categories[i][0] in {"CS", "CN"} for i in prizes)
            rescue_prized = sum(categories[i][0] in {"RS", "RN"} for i in prizes)
            critical_layouts += int(critical_prized > 0)
            collapse_layouts += int(critical_prized > total_rescue - rescue_prized)

    return collapse_layouts / accepted_layouts, critical_layouts / accepted_layouts


def validate() -> None:
    cases = [
        (9, 2, 3, 3, 0, 2, 0, 1),
        (9, 2, 3, 4, 1, 1, 0, 1),
        (10, 3, 3, 4, 2, 1, 1, 1),
        (10, 3, 3, 6, 1, 2, 2, 0),
    ]
    for args in cases:
        deck_size, prize_count, hand, starters, cs, cn, rs, rn = args
        exact_collapse = collapse_probability_given_valid_start(
            deck_size, prize_count, starter_cards=starters, critical_starter=cs,
            critical_nonstarter=cn, rescue_starter=rs, rescue_nonstarter=rn,
            opening_hand_size=hand
        )
        exact_any = any_critical_prized_probability_given_valid_start(
            deck_size, prize_count, starter_cards=starters, critical_starter=cs,
            critical_nonstarter=cn, rescue_starter=rs, rescue_nonstarter=rn,
            opening_hand_size=hand
        )
        brute_collapse, brute_any = exhaustive_probabilities(*args)
        if abs(exact_collapse - brute_collapse) > 1e-15:
            raise AssertionError((args, exact_collapse, brute_collapse))
        if abs(exact_any - brute_any) > 1e-15:
            raise AssertionError((args, exact_any, brute_any))
        mass = sum(
            probability for _, probability in conditioned_prize_state_distribution(
                deck_size, prize_count, starter_cards=starters, critical_starter=cs,
                critical_nonstarter=cn, rescue_starter=rs, rescue_nonstarter=rn,
                opening_hand_size=hand
            )
        )
        if abs(mass - 1.0) > 1e-14:
            raise AssertionError((args, mass))


def main() -> None:
    validate()
    deck_size = 60
    prize_count = 6
    hand = 7

    print("Specific-card Prize probability after a valid opening")
    print("starters | starter critical | non-starter critical")
    for starters in [4, 6, 8, 10, 12, 16, 20]:
        starter_p = any_critical_prized_probability_given_valid_start(
            deck_size, prize_count, starter_cards=starters, critical_starter=1,
            critical_nonstarter=0, opening_hand_size=hand
        )
        nonstarter_p = any_critical_prized_probability_given_valid_start(
            deck_size, prize_count, starter_cards=starters, critical_starter=0,
            critical_nonstarter=1, opening_hand_size=hand
        )
        print(f"{starters:8d} | {pct(starter_p):>16} | {pct(nonstarter_p):>20}")

    print("\nTwo non-starter rescuers protecting non-starter criticals, 12 starters")
    print("criticals | uncond collapse | valid-start collapse | uncond conditional | valid-start conditional")
    for criticals in range(1, 6):
        uncond = unconditioned_collapse_probability(deck_size, prize_count, criticals, 2)
        uncond_any = unconditioned_any_critical_probability(deck_size, prize_count, criticals)
        conditioned = collapse_probability_given_valid_start(
            deck_size, prize_count, starter_cards=12, critical_starter=0,
            critical_nonstarter=criticals, rescue_starter=0, rescue_nonstarter=2,
            opening_hand_size=hand
        )
        conditioned_conditional = conditional_collapse_probability_given_valid_start(
            deck_size, prize_count, starter_cards=12, critical_starter=0,
            critical_nonstarter=criticals, rescue_starter=0, rescue_nonstarter=2,
            opening_hand_size=hand
        )
        print(f"{criticals:9d} | {pct(uncond):>15} | {pct(conditioned):>20} | "
              f"{pct(uncond / uncond_any):>18} | {pct(conditioned_conditional):>23}")

    print("\nFour criticals, two non-starter rescuers, 12 starters")
    print("critical starters | valid-start collapse | collapse given any critical Prized")
    for critical_starters in range(5):
        critical_nonstarters = 4 - critical_starters
        collapse = collapse_probability_given_valid_start(
            deck_size, prize_count, starter_cards=12, critical_starter=critical_starters,
            critical_nonstarter=critical_nonstarters, rescue_starter=0, rescue_nonstarter=2
        )
        conditional = conditional_collapse_probability_given_valid_start(
            deck_size, prize_count, starter_cards=12, critical_starter=critical_starters,
            critical_nonstarter=critical_nonstarters, rescue_starter=0, rescue_nonstarter=2
        )
        print(f"{critical_starters:17d} | {pct(collapse):>20} | {pct(conditional):>34}")


if __name__ == "__main__":
    main()
