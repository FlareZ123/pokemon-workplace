"""Exact opening role tradeoff when extra Heavy Ball copies displace Psychic Energy."""

from __future__ import annotations
from collections import Counter
from fractions import Fraction
from math import comb, prod
from tools.shadow_rider_heavy_ball_launch import allocations, classify


def source_counts(heavy_copies: int) -> tuple[int, ...]:
    """60-card champion role counts after an Energy-to-Heavy Ball swap."""
    if heavy_copies not in range(5):
        raise ValueError("only zero through four copies are allowed")
    return (1, 4, 4, heavy_copies, 13, 38 - heavy_copies)


def launch_filler_hand_buckets(
    caps: tuple[int, ...], opening_size: int = 7, prize_count: int = 6
) -> dict[int, Fraction]:
    """Probability of dual VMAX access for each number of held filler cards."""
    n = sum(caps)
    starts = comb(n, opening_size) - comb(n - caps[0] - caps[4], opening_size)
    den = starts * comb(n - opening_size, prize_count) * (n - opening_size - prize_count)
    weighted: Counter[int] = Counter()
    for opened in allocations(opening_size, caps):
        if not (opened[0] + opened[4]):
            continue
        ow = prod(comb(c, k) for c, k in zip(caps, opened))
        remaining = tuple(c - k for c, k in zip(caps, opened))
        for prizes in allocations(prize_count, remaining):
            pw = ow * prod(comb(c, k) for c, k in zip(remaining, prizes))
            unprized = tuple(c - k for c, k in zip(remaining, prizes))
            for drawn, quantity in enumerate(unprized):
                if quantity and classify(opened, prizes, drawn, caps).endswith("_2"):
                    weighted[opened[5] + int(drawn == 5)] += pw * quantity
    return {k: Fraction(v, den) for k, v in sorted(weighted.items())}


def energy_reserve_probability(
    buckets: dict[int, Fraction], filler_total: int, energy_copies: int
) -> Fraction:
    """Probability of launch and at least one initial-hand Energy copy."""
    if not 0 <= energy_copies <= filler_total:
        raise ValueError("invalid Energy subset size")
    total = Fraction(0)
    for held, mass in buckets.items():
        unavailable = (
            Fraction(0) if held > filler_total - energy_copies else
            Fraction(comb(filler_total - energy_copies, held), comb(filler_total, held))
        )
        total += mass * (1 - unavailable)
    return total


def energy_swap_frontier() -> tuple[tuple[int, int, Fraction, Fraction], ...]:
    """For H=0..4 evaluate dual VMAX access and an Energy-hand reserve."""
    rows = []
    for heavy in range(5):
        caps = source_counts(heavy)
        energy = 12 - heavy
        buckets = launch_filler_hand_buckets(caps)
        rows.append((
            heavy, energy, sum(buckets.values(), Fraction(0)),
            energy_reserve_probability(buckets, caps[5], energy),
        ))
    return tuple(rows)
