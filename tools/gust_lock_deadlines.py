"""A fixed lock-onset schedule changes Boss/Counter Catcher source priority.

The turn number is the attacker's turn index (1-based). Supporter and Item
locks begin at their specified turn and remain active thereafter. They are
exogenous to opponent board state and do not turn off after KOs in this model.
"""
from functools import lru_cache


@lru_cache(None)
def minimum_attacks_with_locks(
    active: int,
    bench: tuple[int, ...],
    bosses: int,
    catchers: int,
    own_prizes: int,
    opponent_prizes: int,
    turn: int,
    supporter_locked_from: int,
    item_locked_from: int,
) -> int:
    if own_prizes <= 0:
        return 0
    if not bench:
        return 1

    moves = [(active, bench, bosses, catchers)]
    for i, prize in enumerate(bench):
        survivors = tuple(sorted((active,) + bench[:i] + bench[i + 1 :]))
        if bosses and turn < supporter_locked_from:
            moves.append((prize, survivors, bosses - 1, catchers))
        if catchers and turn < item_locked_from and own_prizes > opponent_prizes:
            moves.append((prize, survivors, bosses, catchers - 1))

    return min(
        _take_attack(prize, survivors, next_bosses, next_catchers,
                     own_prizes, opponent_prizes, turn,
                     supporter_locked_from, item_locked_from)
        for prize, survivors, next_bosses, next_catchers in moves
    )


def _take_attack(
    prize: int,
    survivors: tuple[int, ...],
    bosses: int,
    catchers: int,
    own_prizes: int,
    opponent_prizes: int,
    turn: int,
    supporter_locked_from: int,
    item_locked_from: int,
) -> int:
    if prize >= own_prizes or not survivors:
        return 1
    return 1 + max(
        minimum_attacks_with_locks(
            promoted,
            survivors[:i] + survivors[i + 1 :],
            bosses,
            catchers,
            own_prizes - prize,
            opponent_prizes,
            turn + 1,
            supporter_locked_from,
            item_locked_from,
        )
        for i, promoted in enumerate(survivors)
    )


def force_first_source(
    active: int,
    bench: tuple[int, ...],
    own_prizes: int,
    opponent_prizes: int,
    kind: str,
    supporter_locked_from: int,
    item_locked_from: int,
) -> int:
    """One Boss and one Catcher initially; first-turn gust source fixed."""
    if kind not in ("B", "C"):
        raise ValueError("kind must be B or C")
    if not bench or (kind == "B" and supporter_locked_from <= 1) or (
        kind == "C" and (item_locked_from <= 1 or own_prizes <= opponent_prizes)
    ):
        raise ValueError("first-turn source cannot gust")
    bosses, catchers = (0, 1) if kind == "B" else (1, 0)
    return min(
        _take_attack(
            prize, tuple(sorted((active,) + bench[:i] + bench[i + 1 :])),
            bosses, catchers, own_prizes, opponent_prizes, 1,
            supporter_locked_from, item_locked_from
        )
        for i, prize in enumerate(bench)
    )
