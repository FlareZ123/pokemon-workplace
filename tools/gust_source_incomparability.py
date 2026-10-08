"""Compare Boss+Serena and Boss+Counter in a typed, Prize-gated endgame.

Serena: unrestricted time but only V2/V3 Bench targets.
Counter Catcher: all Bench classes, but only while own remaining Prizes exceed
opponent remaining Prizes. Boss: any Bench class without that Prize restriction.

Other Item/Supporter restrictions and Serena's draw mode are out of scope.
"""
from functools import lru_cache
from tools.target_restricted_gust_minimax import PRIZE_VALUE


@lru_cache(None)
def minimum_gust_attacks(
    active: str,
    bench: tuple[str, ...],
    bosses: int,
    serenas: int,
    catchers: int,
    own_prizes: int,
    opponent_prizes: int,
) -> int:
    if own_prizes <= 0:
        return 0
    if not bench:
        return 1

    actions = [(active, bench, bosses, serenas, catchers)]
    for i, target in enumerate(bench):
        rest = tuple(sorted((active,) + bench[:i] + bench[i + 1 :]))
        if bosses:
            actions.append((target, rest, bosses - 1, serenas, catchers))
        if serenas and target.startswith("V"):
            actions.append((target, rest, bosses, serenas - 1, catchers))
        if catchers and own_prizes > opponent_prizes:
            actions.append((target, rest, bosses, serenas, catchers - 1))

    scores = []
    for target, rest, b, s, c in actions:
        if PRIZE_VALUE[target] >= own_prizes or not rest:
            scores.append(1)
        else:
            scores.append(
                1 + max(
                    minimum_gust_attacks(
                        p, rest[:i] + rest[i + 1 :],
                        b, s, c,
                        own_prizes - PRIZE_VALUE[target],
                        opponent_prizes,
                    )
                    for i, p in enumerate(rest)
                )
            )
    return min(scores)
