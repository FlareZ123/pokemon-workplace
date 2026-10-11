"""SFT: the paid extra-output G&H branch remains legal when essentials are held.

This is a conditional physical-card witness, not an Aichi win-rate estimate.
"""
from __future__ import annotations

from collections import Counter
from fractions import Fraction
from itertools import combinations

from tools.aichi_gnh_discard_frontier import paid_gnh_states
from tools.aichi_post_gnh_prize_reset import Prepared

TOOL = "Technical Machine: Evolution"
ENERGY = "Jet Energy"
STADIUM = "Artazon"
TICKET = "TechSlot1"


def paid_spare_resources(state: Prepared, discard: tuple[str, str]) -> tuple[
    Counter[str], Counter[str], Counter[str]
]:
    """Execute a chosen legal two-card G&H cost before any deck search."""
    hand, deck, trash = state.hand.copy(), state.remaining.copy(), Counter()
    assert state.gnh_access
    for name in discard:
        if hand[name] <= 0:
            raise ValueError(f"Unavailable discard instance: {name}")
        hand[name] -= 1
        trash[name] += 1
        if hand[name] == 0:
            del hand[name]
    # Branch intentionally chooses a Stadium and two spare G&H bonus outputs.
    for name in (STADIUM, TOOL, ENERGY):
        if deck[name] <= 0:
            raise ValueError(f"Unavailable search output: {name}")
        deck[name] -= 1
        hand[name] += 1
        if deck[name] == 0:
            del deck[name]
    return hand, deck, trash


def physical_hit_probability(deck: Counter[str], inspected: int) -> Fraction:
    """Independent labeled top-five enumeration, with one Ticket copy."""
    cards = tuple(name for name, count in deck.items() for _ in range(count))
    assert cards.count(TICKET) == 1 and inspected <= len(cards)
    seen = sum(TICKET in tuple(cards[i] for i in subset)
               for subset in combinations(range(len(cards)), inspected))
    return Fraction(seen, sum(1 for _ in combinations(range(len(cards)), inspected)))


def main() -> None:
    state = Prepared(
        hand=Counter({TOOL: 1, ENERGY: 1, "Guzma": 1, "Karen": 1}),
        remaining=Counter({TOOL: 1, ENERGY: 1, STADIUM: 1,
                           TICKET: 1, "Other": 8}),
        active="Jirachi",
        prizes=(),
        gnh_access=True,
    )
    before = state.hand + state.remaining
    existing = paid_gnh_states(state)
    assert len(existing) == 1 and existing[0].paid_with is None
    ordinary = existing[0]
    assert ordinary.hand[TOOL] == 1 and ordinary.hand[ENERGY] == 1

    hand, deck, trash = paid_spare_resources(state, ("Guzma", "Karen"))
    assert hand[TOOL] == 2 and hand[ENERGY] == 2
    assert trash == Counter({"Guzma": 1, "Karen": 1})
    assert hand + deck + trash == before
    assert sum(ordinary.remaining.values()) == 11
    assert sum(deck.values()) == 9

    ordinary_hit = physical_hit_probability(ordinary.remaining, 5)
    paid_hit = physical_hit_probability(deck, 5)
    assert ordinary_hit == Fraction(5, 11), ordinary_hit
    assert paid_hit == Fraction(5, 9), paid_hit
    assert paid_hit - ordinary_hit == Fraction(10, 99)

    print("PASS: physically conserved, paid G&H two-spare search")
    print("PASS: original planner has one no-payment path and omits this legal paid path")
    print(f"Conditional five-card Ticket hit: ordinary {ordinary_hit}, paid {paid_hit}")
    print(f"Gain conditional on this chosen line: {paid_hit - ordinary_hit}")


if __name__ == "__main__":
    main()
