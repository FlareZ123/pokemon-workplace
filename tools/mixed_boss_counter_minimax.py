"""Exact six-Prize minimax for one Boss plus one or more Counter Catchers.

Counter Catcher is an Item with a dynamic own-Prize-lead eligibility gate.
Boss is an unrestricted Supporter gust. A source choice matters because
consuming Counter first preserves broad Boss for a later Prize threshold.

The turn's only objective is selecting and KOing one target in one attack;
thus playing multiple targeted switch effects on the same turn is dominated
by one correctly chosen final target in this bounded game. No additional
switching triggers or Supporter opportunity effects are represented.
"""
from functools import lru_cache


@lru_cache(None)
def minimum_attacks(
    active: int,
    bench: tuple[int, ...],
    bosses: int,
    catchers: int,
    own_prizes_remaining: int = 6,
    opponent_prizes_remaining: int = 3,
) -> int:
    if own_prizes_remaining <= 0:
        return 0
    if not bench:
        return 1

    actions = [(active, bench, bosses, catchers)]
    for i, reward in enumerate(bench):
        survivors = tuple(sorted((active,) + bench[:i] + bench[i + 1:]))
        if bosses:
            actions.append((reward, survivors, bosses - 1, catchers))
        if catchers and own_prizes_remaining > opponent_prizes_remaining:
            actions.append((reward, survivors, bosses, catchers - 1))

    costs = []
    for reward, others, b, c in actions:
        if reward >= own_prizes_remaining or not others:
            costs.append(1)
        else:
            costs.append(
                1 + max(
                    minimum_attacks(
                        replacement, others[:j] + others[j + 1:],
                        b, c, own_prizes_remaining - reward,
                        opponent_prizes_remaining,
                    )
                    for j, replacement in enumerate(others)
                )
            )
    return min(costs)


def forced_first_source(
    active: int,
    bench: tuple[int, ...],
    opponent_prizes_remaining: int,
    source: str,
    target_prizes: int,
    own_prizes_remaining: int = 6,
) -> int | None:
    """One Boss plus one Counter, forced first target/source, optimize afterward."""
    if source not in ("boss", "counter"):
        raise ValueError("source must be boss or counter")
    if source == "counter" and own_prizes_remaining <= opponent_prizes_remaining:
        return None

    boss_left, counter_left = (
        (0, 1) if source == "boss" else (1, 0)
    )
    options = []
    for i, reward in enumerate(bench):
        if reward != target_prizes:
            continue
        survivors = tuple(sorted((active,) + bench[:i] + bench[i + 1:]))
        if reward >= own_prizes_remaining or not survivors:
            options.append(1)
        else:
            options.append(
                1 + max(
                    minimum_attacks(
                        promoted, survivors[:j] + survivors[j + 1:],
                        boss_left, counter_left,
                        own_prizes_remaining - reward,
                        opponent_prizes_remaining,
                    )
                    for j, promoted in enumerate(survivors)
                )
            )
    return min(options) if options else None
