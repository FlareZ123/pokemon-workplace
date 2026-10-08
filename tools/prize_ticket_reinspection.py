"""Exact stopping-policy values for consecutive Redeemable Ticket resets.

Research scope: a fixed initial, fully known Prize composition; a uniformly
shuffled deck; no intervening draws or deck/Prize mutations except Ticket;
and exact reinspection after each ticket for the adaptive policy. Every Ticket
moves the current Prize set to the bottom and replaces it with the next P
cards. For at most floor(deck_size/P) resets, new Prize sets are disjoint
consecutive samples from the ORIGINAL deck.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import comb


@dataclass(frozen=True)
class TicketResults:
    # Index zero is the initial state; index i represents at most i resets.
    success_by_limit: tuple[Fraction, ...]
    expected_uses_by_limit: tuple[Fraction, ...]
    # Probability of success after any fixed positive count of blind resets.
    blind_terminal_success: Fraction


def _compositions(total: int, bounds: tuple[int, ...]):
    """Yield bounded category counts of a sample of "total" physical cards."""
    if len(bounds) == 1:
        if 0 <= total <= bounds[0]:
            yield (total,)
        return
    for count in range(min(total, bounds[0]) + 1):
        for suffix in _compositions(total - count, bounds[1:]):
            yield (count,) + suffix


def analyze_tickets(
    deck_targets: tuple[int, ...],
    old_prize_targets: tuple[int, ...],
    required_in_deck: tuple[int, ...],
    *,
    deck_size: int,
    prize_count: int,
    max_resets: int,
) -> TicketResults:
    """Exact adaptive-with-reinspection and fixed-blind Ticket success.

    "deck_targets" are counts of disjoint target groups in the current deck.
    "old_prize_targets" are counts in the current Prize zone. Targets in hand,
    discard, or other zones cannot be restored by this model.

    Each reset returns *all* current Prizes to the bottom of the deck and takes
    "prize_count" new Prizes from its top. The adaptive policy checks exact
    Prize composition after each reset and stops as soon as all target groups
    have their required searchable copies in the deck. Its upper-bound access
    to immediate, repeated inspection is an explicit assumption.
    """
    if not (len(deck_targets) == len(old_prize_targets) == len(required_in_deck)):
        raise ValueError("target, old-Prize and requirement vectors must match")
    if not deck_targets or any(x < 0 for xs in (deck_targets, old_prize_targets, required_in_deck) for x in xs):
        raise ValueError("nonempty vectors with nonnegative counts required")
    if prize_count < 1 or max_resets < 0 or max_resets * prize_count > deck_size:
        raise ValueError("each modeled replacement must come from untouched original deck cards")
    if deck_size < sum(deck_targets) or prize_count < sum(old_prize_targets):
        raise ValueError("target-group counts exceed their current zone size")

    baseline = all(c >= need for c, need in zip(deck_targets, required_in_deck))
    if baseline:
        return TicketResults(
            (Fraction(1),) * (max_resets + 1),
            (Fraction(0),) * (max_resets + 1),
            Fraction(1),
        )

    original_targets = deck_targets
    categories = deck_targets + (deck_size - sum(deck_targets),)
    failures: dict[tuple[int, ...], Fraction] = {categories: Fraction(1)}
    success = [Fraction(0)]
    expected = [Fraction(0)]
    blind = Fraction(0)

    for reset in range(1, max_resets + 1):
        next_failures: dict[tuple[int, ...], Fraction] = {}
        # A Ticket is used precisely when every previous observed state failed.
        expected.append(expected[-1] + sum(failures.values(), Fraction(0)))
        for remaining, path_mass in failures.items():
            den = comb(sum(remaining), prize_count)
            for sample in _compositions(prize_count, remaining):
                ways = 1
                for capacity, drawn in zip(remaining, sample):
                    ways *= comb(capacity, drawn)
                p = path_mass * Fraction(ways, den)
                new_prize_targets = sample[:-1]
                searchable = tuple(
                    old + deck - newly_prized
                    for old, deck, newly_prized in zip(
                        old_prize_targets, original_targets, new_prize_targets
                    )
                )
                if all(have >= need for have, need in zip(searchable, required_in_deck)):
                    continue
                next_remaining = tuple(a - b for a, b in zip(remaining, sample))
                next_failures[next_remaining] = next_failures.get(next_remaining, Fraction(0)) + p
        failures = next_failures
        success.append(Fraction(1) - sum(failures.values(), Fraction(0)))
        if reset == 1:
            blind = success[-1]

    return TicketResults(tuple(success), tuple(expected), blind)


if __name__ == "__main__":
    v = analyze_tickets((0, 1, 1), (1, 0, 0), (1, 1, 1), deck_size=47, prize_count=6, max_resets=3)
    for n, p in enumerate(v.success_by_limit):
        print(f"{n} resets: success={100 * float(p):.9f}%, expected uses={float(v.expected_uses_by_limit[n]):.9f}")
    print(f"blind terminal success after 1, 2 or 3 forced resets: {100 * float(v.blind_terminal_success):.9f}%")
