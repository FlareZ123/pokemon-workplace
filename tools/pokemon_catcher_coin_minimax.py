"""Exact fair-coin Pokemon Catcher endgame and optional same-turn retries.

All old BW/XY prints of Pokemon Catcher follow the current Pokemon TCG errata:
the player flips a coin, and only heads permits the targeted switch. An Item
played on tails is consumed. The attacker can choose when to attempt an Item
and may play a second Catcher on the same turn after a failed flip.

Opponent board has 1..6 one-hit targets with Prize rewards 1, 2, or 3.
Following each KO the defender chooses a worst-case replacement Active.
"""
from fractions import Fraction
from functools import lru_cache
from tools.gust_prize_minimax import enumerate_boards, minimum_attacks


@lru_cache(None)
def expected_attacks(
    active: int,
    bench: tuple[int, ...],
    catchers: int,
    prizes_needed: int = 6,
) -> Fraction:
    """Min expected attacker turns; adversarial defender sees each coin result."""
    if prizes_needed <= 0:
        return Fraction(0)
    if not bench:
        return Fraction(1)

    def attack_and_promote(target: int, survivors: tuple[int, ...], left: int) -> Fraction:
        if target >= prizes_needed or not survivors:
            return Fraction(1)
        return Fraction(1) + max(
            expected_attacks(
                promoted, survivors[:j] + survivors[j + 1 :],
                left, prizes_needed - target
            )
            for j, promoted in enumerate(survivors)
        )

    no_attempt = attack_and_promote(active, bench, catchers)
    if not catchers:
        return no_attempt

    # On heads the player chooses a target after knowing the flip succeeded.
    heads = min(
        attack_and_promote(
            target,
            tuple(sorted((active,) + bench[:i] + bench[i + 1 :])),
            catchers - 1
        )
        for i, target in enumerate(bench)
    )

    # On tails the Item is spent, but the player can still attack or try
    # another Item during the very same turn. The recursive state has NOT
    # advanced an attack or triggered an opponent promotion.
    tails = expected_attacks(active, bench, catchers - 1, prizes_needed)
    attempt_now = (heads + tails) / 2
    return min(no_attempt, attempt_now)


def census():
    """146 distinct prize-board geometries with zero, one and two Catchers."""
    return tuple(
        (
            active, bench,
            *(expected_attacks(active, bench, count) for count in range(3)),
            minimum_attacks(active, bench, 1),
            minimum_attacks(active, bench, 2),
        )
        for active, bench, _ in enumerate_boards()
    )
