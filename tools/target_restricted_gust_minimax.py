"""Gust target typing: Boss unrestricted versus Serena's Pokemon V family.

Five abstract opposing classes:
  N1, N2, N3: non-Pokemon-V, worth 1/2/3 Prize cards;
  V2, V3: Pokemon V family, worth 2/3 Prize cards.

Target class is fixed and public. All Pokemon are one-hit KOs. Each source
is a Supporter-like gust token, used at most once per attack turn.
"""
from functools import lru_cache
from itertools import combinations_with_replacement


PRIZE_VALUE = {"N1": 1, "N2": 2, "N3": 3, "V2": 2, "V3": 3}


def enumerate_typed_boards():
    """Distinct 2..6-Pokemon boards with six or more total Prize rewards."""
    kinds = tuple(sorted(PRIZE_VALUE))
    for n in range(2, 7):
        for values in combinations_with_replacement(kinds, n):
            if sum(PRIZE_VALUE[value] for value in values) < 6:
                continue
            for active in sorted(set(values)):
                bench = list(values)
                bench.remove(active)
                yield active, tuple(bench), values


@lru_cache(None)
def minimum_typed_attacks(
    active: str,
    bench: tuple[str, ...],
    bosses: int,
    serenas: int,
    prizes_needed: int = 6,
) -> int:
    """Min attacker turns against worst-case defender promotion."""
    if prizes_needed <= 0:
        return 0
    if not bench:
        return 1

    actions = [(active, bench, bosses, serenas)]
    for i, target in enumerate(bench):
        survivors = tuple(sorted((active,) + bench[:i] + bench[i + 1 :]))
        if bosses:
            actions.append((target, survivors, bosses - 1, serenas))
        if serenas and target.startswith("V"):
            actions.append((target, survivors, bosses, serenas - 1))

    costs = []
    for target, survivors, next_bosses, next_serenas in actions:
        if PRIZE_VALUE[target] >= prizes_needed or not survivors:
            costs.append(1)
        else:
            costs.append(
                1 + max(
                    minimum_typed_attacks(
                        promoted, survivors[:i] + survivors[i + 1 :],
                        next_bosses, next_serenas,
                        prizes_needed - PRIZE_VALUE[target],
                    )
                    for i, promoted in enumerate(survivors)
                )
            )
    return min(costs)
