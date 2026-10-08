"""Exact consecutive Prize Ticket policy with a deck shuffle between uses.

Unlike the no-shuffle policy, subsequent Prize blocks can contain targets
returned to the deck by earlier Tickets. The state tracks target counts both
in the current deck and in the current Prize set. A deck shuffle makes every
remaining physical deck card exchangeable before the next reset.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import comb


@dataclass(frozen=True)
class ShuffleTicketResults:
    success_by_limit: tuple[Fraction, ...]
    expected_uses_by_limit: tuple[Fraction, ...]


def bounded_compositions(total: int, bounds: tuple[int, ...]):
    if len(bounds) == 1:
        if 0 <= total <= bounds[0]:
            yield (total,)
        return
    for i in range(min(total, bounds[0]) + 1):
        for suffix in bounded_compositions(total - i, bounds[1:]):
            yield (i,) + suffix


def analyze_shuffled_tickets(
    deck_targets: tuple[int, ...],
    old_prize_targets: tuple[int, ...],
    required_in_deck: tuple[int, ...],
    *,
    deck_size: int,
    prize_count: int,
    max_resets: int,
) -> ShuffleTicketResults:
    """Exact stop-on-success policy with uniform deck reshuffle between resets.

    A Ticket selects P cards from the preexisting deck, deposits the previous
    P Prizes at bottom and replaces them with its selected cards. Before the
    NEXT Ticket, the full current deck is shuffled independently. Current
    target counts in deck/Prizes are sufficient statistics under this policy.

    Access to Tickets, exact Prize reinspection, and full deck shuffles are
    conditional assumptions, not automatically executable card lines.
    """
    if not deck_targets or not (
        len(deck_targets) == len(old_prize_targets) == len(required_in_deck)
    ):
        raise ValueError("nonempty target, Prize, requirement vectors must agree")
    if min(deck_size, prize_count, max_resets) < 0 or prize_count > deck_size:
        raise ValueError("invalid zone sizes")
    if any(c < 0 for group in (deck_targets, old_prize_targets, required_in_deck) for c in group):
        raise ValueError("counts must be nonnegative")
    if sum(deck_targets) > deck_size or sum(old_prize_targets) > prize_count:
        raise ValueError("target counts exceed zone capacities")
    if all(x >= need for x, need in zip(deck_targets, required_in_deck)):
        return ShuffleTicketResults(
            (Fraction(1),) * (max_resets + 1),
            (Fraction(0),) * (max_resets + 1),
        )
    if prize_count == 0 and max_resets:
        raise ValueError("no Prize cards to replace")
    failures: dict[tuple[tuple[int, ...], tuple[int, ...]], Fraction] = {
        (deck_targets, old_prize_targets): Fraction(1)
    }
    success = [Fraction(0)]
    uses = [Fraction(0)]
    denominator = comb(deck_size, prize_count)
    for _ in range(max_resets):
        uses.append(uses[-1] + sum(failures.values(), Fraction(0)))
        next_failures: dict[tuple[tuple[int, ...], tuple[int, ...]], Fraction] = {}
        for (deck, prized), state_mass in failures.items():
            capacities = deck + (deck_size - sum(deck),)
            for new_prizes in bounded_compositions(prize_count, capacities):
                ways = 1
                for count, take in zip(capacities, new_prizes):
                    ways *= comb(count, take)
                probability = state_mass * Fraction(ways, denominator)
                newly_prized = new_prizes[:-1]
                new_deck = tuple(
                    d - p + old for d, p, old in zip(deck, newly_prized, prized)
                )
                if all(d >= need for d, need in zip(new_deck, required_in_deck)):
                    continue
                key = (new_deck, newly_prized)
                next_failures[key] = next_failures.get(key, Fraction(0)) + probability
        failures = next_failures
        success.append(Fraction(1) - sum(failures.values(), Fraction(0)))
    return ShuffleTicketResults(tuple(success), tuple(uses))


def main() -> None:
    from tools.prize_ticket_reinspection import analyze_tickets
    params = dict(deck_targets=(0, 1, 1), old_prize_targets=(1, 0, 0),
                  required_in_deck=(1, 1, 1), deck_size=47,
                  prize_count=6, max_resets=3)
    shuffled = analyze_shuffled_tickets(**params)
    untouched = analyze_tickets(**params)
    for i in range(4):
        print(f"{i} reset(s): no-shuffle={100*float(untouched.success_by_limit[i]):.9f}%, "
              f"reshuffle={100*float(shuffled.success_by_limit[i]):.9f}%")


if __name__ == "__main__":
    main()
