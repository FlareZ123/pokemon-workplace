"""Independent exact regression for sequential Prize redeals with inspection."""

from __future__ import annotations

from fractions import Fraction
from itertools import permutations
from math import comb
from pathlib import Path
import sys

# A runnable result file inside results/ may import the reusable tool from repo root.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.prize_ticket_reinspection import analyze_tickets


def brute_force(deck: tuple[str, ...], old_prizes: tuple[str, ...],
                needs: dict[str, int], prize_count: int, max_resets: int):
    total = 0
    hits = [0] * (max_resets + 1)
    uses = [0] * (max_resets + 1)
    initial_ok = all(deck.count(group) >= count for group, count in needs.items())
    for sequence in permutations(range(len(deck))):
        total += 1
        kept = initial_ok
        used = 0
        for limit in range(max_resets + 1):
            if limit:
                if not kept:
                    used += 1
                    new_prizes = [deck[i] for i in sequence[(limit - 1) * prize_count:limit * prize_count]]
                    kept = all(old_prizes.count(group) + deck.count(group) - new_prizes.count(group)
                               >= count for group, count in needs.items())
            hits[limit] += kept
            uses[limit] += used
    return tuple(Fraction(x, total) for x in hits), tuple(Fraction(x, total) for x in uses)


def main():
    # All eight original deck cards are distinct as physical cards; two are target copies.
    deck = ("B", "C", "F", "F", "F", "F", "F", "F")
    requirements = {"A": 1, "B": 1, "C": 1}
    policy = analyze_tickets((0, 1, 1), (1, 0, 0), (1, 1, 1),
                              deck_size=8, prize_count=2, max_resets=3)
    hits, uses = brute_force(deck, ("A", "F"), requirements, 2, 3)
    assert policy.success_by_limit == hits, (policy.success_by_limit, hits)
    assert policy.expected_uses_by_limit == uses, (policy.expected_uses_by_limit, uses)
    assert policy.success_by_limit[-1] == 1

    # Second independent validation uses two copies of B with an all-copies requirement.
    deck2 = ("B", "B", "F", "F", "F", "F", "F", "F")
    policy2 = analyze_tickets((0, 2), (1, 0), (1, 2),
                               deck_size=8, prize_count=2, max_resets=3)
    hits2, uses2 = brute_force(deck2, ("A", "F"), {"A": 1, "B": 2}, 2, 3)
    assert policy2.success_by_limit == hits2
    assert policy2.expected_uses_by_limit == uses2
    assert policy2.success_by_limit[-1] == 1

    # A realistic 47-card deck and six current Prizes at the Aichi timing size.
    # A is in the old Prizes, B and C are in the deck; all three must be searchable.
    large = analyze_tickets((0, 1, 1), (1, 0, 0), (1, 1, 1),
                            deck_size=47, prize_count=6, max_resets=3)
    first = Fraction(comb(45, 6), comb(47, 6))
    second = Fraction(1) - Fraction(2 * 6 * 6, 47 * 46)
    assert large.success_by_limit == (Fraction(0), first, second, Fraction(1))
    assert large.blind_terminal_success == first
    assert large.expected_uses_by_limit[3] == 1 + (1 - first) + (1 - second)
    assert large.success_by_limit == tuple(sorted(large.success_by_limit))
    assert analyze_tickets((1,), (0,), (1,), deck_size=8, prize_count=2,
                            max_resets=3).expected_uses_by_limit == (0, 0, 0, 0)

    for label, x in (("first", first), ("second", second)):
        print(f"{label} success: {float(x):.12%} = {x}")
    print(f"third success: {float(large.success_by_limit[3]):.12%}")
    print(f"expected Tickets at 3-reset ceiling: {float(large.expected_uses_by_limit[3]):.12f}")
    print("PASS: 2 independent labeled-deck exhaustive regressions, closed-form Aichi-sized oracle, quota and monotonic checks")


if __name__ == "__main__":
    main()
