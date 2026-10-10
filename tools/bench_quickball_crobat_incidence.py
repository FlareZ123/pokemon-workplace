"""Exact opening + Prize + draw material incidence for QB->Crobat staging.

One Dedenne D, one Crobat C and one non-Basic singleton K; the opening must
hold D, an ordinary Basic O, Quick Ball Q, and safe discard F, with C and K
absent. C must remain in live deck after Prizes and natural later draws.
"""
from dataclasses import dataclass
from fractions import Fraction
from math import comb


def ways(n: int, k: int) -> int:
    return comb(n, k) if 0 <= k <= n else 0


@dataclass(frozen=True)
class Incidence:
    valid_open: Fraction
    opening_material: Fraction
    material_and_crobat_live: Fraction
    material_given_valid: Fraction


def analyze(*, deck_size: int = 60, opening_size: int = 7,
            prize_count: int = 6, later_draws: int = 1,
            quick_balls: int = 4, discardable: int = 4,
            other_basics: int = 4) -> Incidence:
    """Exact ordinary-Basic accepted opener and paired live-Crobat event."""
    assert min(deck_size, opening_size, prize_count, later_draws,
               quick_balls, discardable, other_basics) >= 0
    filler = deck_size - (3 + quick_balls + discardable + other_basics)
    assert filler >= 0
    remainder = deck_size - opening_size
    assert remainder >= prize_count + later_draws
    opening_ways = 0
    for q in range(1, quick_balls + 1):
        for f in range(1, discardable + 1):
            for o in range(1, other_basics + 1):
                extra = opening_size - 1 - q - f - o
                opening_ways += (ways(quick_balls, q) * ways(discardable, f)
                                 * ways(other_basics, o) * ways(filler, extra))
    all_open = comb(deck_size, opening_size)
    basic_count = 2 + other_basics  # 1 D, 1 C, and ordinary starters.
    valid = Fraction(all_open - ways(deck_size - basic_count, opening_size),
                     all_open)
    open_material = Fraction(opening_ways, all_open)
    live_given_material = Fraction(remainder - prize_count - later_draws,
                                   remainder)
    full = open_material * live_given_material
    return Incidence(valid, open_material, full,
                     full / valid if valid else Fraction(0))


if __name__ == "__main__":
    from bench_quickball_crobat_dedenne import analyze as continuation
    result = analyze()
    delta = continuation(hand_size=5).access_gain
    print("valid opener", float(result.valid_open))
    print("material opening given valid", float(result.opening_material / result.valid_open))
    print("material and C live given valid", float(result.material_given_valid))
    print("conditional staged access gain", float(delta))
    print("product contribution to accepted-open access", float(result.material_given_valid * delta))
