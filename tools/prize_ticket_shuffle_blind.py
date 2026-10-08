"""Forced blind Ticket redeals with intervening full deck shuffles.

This differs from the stop-on-success exact-information policy: every Ticket
is played whether the previous reset fixed the target searchability or not.
No new Prize inspection takes place between forced resets.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import comb

from tools.prize_ticket_shuffle_intervention import bounded_compositions


@dataclass(frozen=True)
class BlindShuffleResult:
    success_by_fixed_count: tuple[Fraction, ...]
    best_fixed_count: int
    best_fixed_success: Fraction


def analyze_blind_shuffled_tickets(
    deck_targets: tuple[int, ...],
    old_prize_targets: tuple[int, ...],
    required_in_deck: tuple[int, ...],
    *,
    deck_size: int,
    prize_count: int,
    resets: int,
) -> BlindShuffleResult:
    """Return exact final target searchability after exactly 0..resets uses.

    Every Ticket replaces all old Prizes with a uniform P-card sample of the
    existing deck, returning old Prizes to its bottom. Between Tickets a
    uniform full-deck shuffle makes the next draw exchangeable. The terminal
    objective is whether the searched deck has the required target copies.
    """
    if not deck_targets or len(deck_targets) != len(old_prize_targets) or len(deck_targets) != len(required_in_deck):
        raise ValueError("nonempty aligned target groups required")
    if deck_size < 1 or not 1 <= prize_count <= deck_size or resets < 0:
        raise ValueError("invalid deck/Prize sizes or reset count")
    if any(x < 0 for group in (deck_targets, old_prize_targets, required_in_deck) for x in group):
        raise ValueError("negative category size")
    if sum(deck_targets) > deck_size or sum(old_prize_targets) > prize_count:
        raise ValueError("target categories exceed zone size")

    states: dict[tuple[tuple[int, ...], tuple[int, ...]], Fraction] = {
        (deck_targets, old_prize_targets): Fraction(1)
    }
    values = [Fraction(int(all(d >= needed for d, needed in zip(deck_targets, required_in_deck))))]
    denominator = comb(deck_size, prize_count)
    for _ in range(resets):
        next_states: dict[tuple[tuple[int, ...], tuple[int, ...]], Fraction] = {}
        for (current_deck, old_prizes), state_probability in states.items():
            categories = current_deck + (deck_size - sum(current_deck),)
            for new_prizes in bounded_compositions(prize_count, categories):
                ways = 1
                for cards, chosen in zip(categories, new_prizes):
                    ways *= comb(cards, chosen)
                mass = state_probability * Fraction(ways, denominator)
                selected = new_prizes[:-1]
                revised_deck = tuple(d - new + old for d, new, old in
                                     zip(current_deck, selected, old_prizes))
                key = (revised_deck, selected)
                next_states[key] = next_states.get(key, Fraction(0)) + mass
        states = next_states
        assert sum(states.values(), Fraction(0)) == 1
        values.append(sum(
            (mass for (deck, _), mass in states.items()
             if all(d >= need for d, need in zip(deck, required_in_deck))),
            Fraction(0),
        ))
    best = max(range(len(values)), key=lambda k: values[k])
    return BlindShuffleResult(tuple(values), best, values[best])


if __name__ == "__main__":
    case = analyze_blind_shuffled_tickets(
        (0, 1, 1), (1, 0, 0), (1, 1, 1), deck_size=47, prize_count=6, resets=10
    )
    for i, p in enumerate(case.success_by_fixed_count):
        print(i, f"{100*float(p):.9f}%")
    print("best", case.best_fixed_count, f"{100*float(case.best_fixed_success):.9f}%")
