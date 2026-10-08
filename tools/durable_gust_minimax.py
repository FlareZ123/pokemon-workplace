"""Exact gust Prize-race minimax with persistent damage and two-hit targets.

A Pokemon is (Prize reward, number of attacks remaining to KO). Every attack
removes one hit; surviving targets remain Active with damage preserved, even
after a later switch. Only KO triggers adversarial promotion. No healing,
opponent retreats, new Bench entries, or other Supporter uses are modeled.
"""
from functools import lru_cache
from itertools import combinations_with_replacement
from typing import Iterator

Pokemon = tuple[int, int]


@lru_cache(None)
def minimum_attacks(
    active: Pokemon,
    bench: tuple[Pokemon, ...],
    gusts: int,
    prizes_needed: int = 6,
) -> int:
    actions = [(active, bench, gusts)]
    if gusts:
        for i, target in enumerate(bench):
            survivors = tuple(sorted((active,) + bench[:i] + bench[i + 1 :]))
            actions.append((target, survivors, gusts - 1))
    scores = []
    for target, other, remaining_gusts in actions:
        reward, hits = target
        if hits > 1:
            scores.append(
                1 + minimum_attacks((reward, hits - 1), other, remaining_gusts, prizes_needed)
            )
        elif reward >= prizes_needed or not other:
            scores.append(1)
        else:
            scores.append(
                1 + max(
                    minimum_attacks(
                        promoted,
                        other[:i] + other[i + 1 :],
                        remaining_gusts,
                        prizes_needed - reward,
                    )
                    for i, promoted in enumerate(other)
                )
            )
    return min(scores)


def must_gust_now(
    active: Pokemon,
    bench: tuple[Pokemon, ...],
    gusts: int,
    prizes_needed: int = 6,
) -> int:
    if not gusts or not bench:
        return minimum_attacks(active, bench, gusts, prizes_needed)
    scores = []
    for i, target in enumerate(bench):
        remaining = tuple(sorted((active,) + bench[:i] + bench[i + 1 :]))
        reward, hits = target
        if hits > 1:
            scores.append(
                1 + minimum_attacks((reward, hits - 1), remaining, gusts - 1, prizes_needed)
            )
        elif reward >= prizes_needed:
            scores.append(1)
        else:
            scores.append(
                1 + max(
                    minimum_attacks(
                        promoted,
                        remaining[:j] + remaining[j + 1 :],
                        gusts - 1,
                        prizes_needed - reward,
                    )
                    for j, promoted in enumerate(remaining)
                )
            )
    return min(scores)


def enumerate_boards() -> Iterator[tuple[Pokemon, tuple[Pokemon, ...], tuple[Pokemon, ...]]]:
    kinds = tuple((reward, hits) for reward in (1, 2, 3) for hits in (1, 2))
    for count in range(2, 5):
        for values in combinations_with_replacement(kinds, count):
            if sum(reward for reward, _ in values) < 6:
                continue
            for active in sorted(set(values)):
                bench = list(values)
                bench.remove(active)
                yield active, tuple(sorted(bench)), values
