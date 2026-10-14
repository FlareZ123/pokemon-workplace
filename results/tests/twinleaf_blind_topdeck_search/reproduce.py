"""Exact K0-to-K1 Prize posterior for narrow blind search-Item policy.

Reproduce: python results/tests/twinleaf_blind_topdeck_search/reproduce.py
No game outcome, draw-engine, deck-search, or matchup simulation is implied.
"""
from fractions import Fraction
from itertools import combinations
from math import comb


def hit(n: int, successes: int, window: int) -> Fraction:
    """Uniform without-replacement top-window target probability."""
    if successes == 0 or window == 0:
        return Fraction(0)
    if n - successes < window:
        return Fraction(1)
    return 1 - Fraction(comb(n - successes, window), comb(n, window))


def posterior(pool: int, prizes: int, hits: int, window: int):
    """Exact distribution over number of eligible cards among initial prizes."""
    deck = pool - prizes
    assert 0 <= hits <= pool and 0 <= prizes < pool
    assert 0 <= window <= deck
    denominator = comb(pool, prizes)
    for prized_hits in range(max(0, prizes - (pool - hits)),
                             min(prizes, hits) + 1):
        weight = Fraction(
            comb(hits, prized_hits) * comb(pool - hits, prizes - prized_hits),
            denominator,
        )
        yield prized_hits, weight, hit(deck, hits - prized_hits, window)


def brute(pool: int, prizes: int, successes: int, window: int) -> Fraction:
    """Independent physical enumeration of Prize sets and deck windows."""
    targets = frozenset(range(successes))
    total = favorable = 0
    for prized in combinations(range(pool), prizes):
        remaining = tuple(i for i in range(pool) if i not in prized)
        for top in combinations(remaining, window):
            total += 1
            favorable += bool(targets.intersection(top))
    return Fraction(favorable, total)


def main():
    for pool, prizes, count, window in [(9, 2, 2, 3),
                                         (10, 3, 3, 2),
                                         (12, 2, 4, 3)]:
        rows = list(posterior(pool, prizes, count, window))
        assert sum((weight for _, weight, _ in rows), Fraction(0)) == 1
        weighted = sum((weight * value for _, weight, value in rows),
                       Fraction(0))
        assert weighted == hit(pool, count, window)
        assert weighted == brute(pool, prizes, count, window)

    for count, window, expected_shift in [
        (4, 7, Fraction(3292, 54145)),
        (8, 4, Fraction(1227, 363545)),
    ]:
        rows = list(posterior(52, 6, count, window))
        assert sum((weight for _, weight, _ in rows), Fraction(0)) == 1
        marginal = sum((weight * value for _, weight, value in rows),
                       Fraction(0))
        assert marginal == hit(52, count, window)
        k0_play = 6 * marginal - 2 > 0
        assert k0_play
        disagree = sum((weight for _, weight, value in rows
                        if (6 * value - 2 > 0) != k0_play), Fraction(0))
        assert disagree == expected_shift
        print({
            "targets": count,
            "window": window,
            "k0_hit_probability": str(marginal),
            "k0_play": k0_play,
            "k1_recommendation_disagreement_mass": str(disagree),
            "k1_cases": [
                {
                    "prized_targets": j,
                    "configuration_mass": str(weight),
                    "top_window_hit_probability": str(value),
                    "play_at_k1": 6 * value - 2 > 0,
                }
                for j, weight, value in rows
            ],
        })
    print("PASS: exact posterior normalizes, independently enumerated tiny physical oracles match")


if __name__ == "__main__":
    main()
