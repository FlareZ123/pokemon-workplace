"""Paired exact Shadow Rider Radiant launch access: first vs second turn.

Same accepted seven-card opening and six-Prize world, with uniform optional
first draw. Quantifies *both* added access and lost VMAX targets instead of
assuming another drawn card cannot hurt a search-from-deck objective.
"""
from __future__ import annotations

from collections import Counter
from fractions import Fraction
from itertools import combinations
from math import comb, prod

from results.shadow_rider_radiant_launch.reproduce import (
    COUNTS,
    allocations,
    classify as second_class,
    exact as second_exact,
)

PAIRS = ((False, False), (False, True), (True, False), (True, True))


def first_class(
    opening: tuple[int, ...],
    prizes: tuple[int, ...],
    caps: tuple[int, ...],
) -> str:
    """No normal draw when going first. Other Basic must start Active."""
    if opening[0] + opening[3] == 0:
        return "reject"
    if opening[3] == 0:
        return "no_eligible_active"
    deck = [c - x - y for c, x, y in zip(caps, opening, prizes)]
    if opening[0]:
        source = "direct"
    elif opening[2] and deck[0]:
        source = "treasure"
    else:
        return "no_radiant_access"
    return f"{source}_{min(2, deck[1])}"


def paired_exact(
    caps: tuple[int, ...] = COUNTS,
    opening_size: int = 7,
    prize_size: int = 6,
) -> tuple[dict[tuple[bool, bool], Fraction], dict[str, Fraction]]:
    """Return source-identity-preserving paired outcomes at fixed shuffle."""
    size = sum(caps)
    opening_ways = comb(size, opening_size) - comb(
        size - caps[0] - caps[3], opening_size
    )
    ways = (
        opening_ways
        * comb(size - opening_size, prize_size)
        * (size - opening_size - prize_size)
    )
    both: Counter[tuple[bool, bool]] = Counter()
    switches: Counter[str] = Counter()
    total = 0

    for opening in allocations(opening_size, caps):
        if opening[0] + opening[3] == 0:
            continue
        opening_weight = prod(comb(c, x) for c, x in zip(caps, opening))
        remaining = tuple(c - x for c, x in zip(caps, opening))
        for prizes in allocations(prize_size, remaining):
            prize_weight = opening_weight * prod(
                comb(c, x) for c, x in zip(remaining, prizes)
            )
            after_prizes = tuple(
                c - x for c, x in zip(remaining, prizes)
            )
            start = first_class(opening, prizes, caps)
            ready_first = start.endswith("_2")
            for draw_index, available in enumerate(after_prizes):
                if not available:
                    continue
                end = second_class(opening, prizes, draw_index, caps)
                ready_second = end.endswith("_2")
                weight = prize_weight * available
                both[ready_first, ready_second] += weight
                total += weight

                if not ready_first and ready_second:
                    switches[f"gain_draw_{draw_index}"] += weight
                if ready_first and not ready_second:
                    switches[f"loss_draw_{draw_index}"] += weight

    assert total == ways
    assert sum(both.values()) == ways
    return (
        {pair: Fraction(both[pair], ways) for pair in PAIRS},
        {label: Fraction(value, ways) for label, value in switches.items()},
    )


def toy_physical_oracle() -> None:
    """Independently enumerate full labeled outcomes for a small physical deck."""
    caps = (1, 2, 1, 2, 4)
    identities = tuple(
        category for category, copies in enumerate(caps)
        for _ in range(copies)
    )
    outcomes: Counter[tuple[bool, bool]] = Counter()
    reasons: Counter[str] = Counter()
    total = 0

    for opener in combinations(range(len(identities)), 3):
        start = tuple(identities[i] for i in opener)
        if 0 not in start and 3 not in start:
            continue
        other = [i for i in range(len(identities)) if i not in opener]
        for prize_slots in combinations(other, 2):
            prizes = tuple(identities[i] for i in prize_slots)
            after_prizes = [i for i in other if i not in prize_slots]
            o = tuple(start.count(i) for i in range(5))
            p = tuple(prizes.count(i) for i in range(5))
            early = first_class(o, p, caps).endswith("_2")
            for draw_slot in after_prizes:
                draw_index = identities[draw_slot]
                late = second_class(o, p, draw_index, caps).endswith("_2")
                outcomes[early, late] += 1
                total += 1
                if not early and late:
                    reasons[f"gain_draw_{draw_index}"] += 1
                if early and not late:
                    reasons[f"loss_draw_{draw_index}"] += 1

    exact, changes = paired_exact(caps, 3, 2)
    assert all(exact[p] == Fraction(outcomes[p], total) for p in PAIRS)
    assert {
        key: Fraction(value, total) for key, value in reasons.items()
    } == changes
    print(f"Physical paired-turn oracle passed: {total} labeled states")


def main() -> None:
    toy_physical_oracle()
    paired, switches = paired_exact()
    first = paired[True, True] + paired[True, False]
    second = paired[True, True] + paired[False, True]
    gain = paired[False, True]
    loss = paired[True, False]

    second_model = second_exact()
    second_marginal = sum(
        probability
        for label, probability in second_model.items()
        if label.endswith("_2")
    )
    assert second == second_marginal
    assert first == Fraction(151384620437, 382489276400)
    assert gain == Fraction(31573698707, 719979814400)
    assert loss == Fraction(13907893, 5248566400)
    assert second - first == gain - loss
    assert second - first == Fraction(504319671543, 12239656844800)
    assert switches["loss_draw_1"] == loss
    assert switches["gain_draw_0"] + switches["gain_draw_2"] == gain

    for pair, probability in paired.items():
        print(f"{pair}: {probability} = {float(probability):.12%}")
    for reason, probability in sorted(switches.items()):
        print(f"{reason}: {probability} = {float(probability):.12%}")
    print(f"First turn (no draw): {float(first):.12%}")
    print(f"Second turn order (one draw): {float(second):.12%}")
    print(f"Net draw gain: {float(second-first):.12%}")


if __name__ == "__main__":
    main()
