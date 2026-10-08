"""Exact mixed Boss's Orders / Counter Catcher six-Prize endgame minimax.

One Boss token is an unconditional targeted gust; one Counter Catcher token
is usable only when own remaining Prizes exceed the opponent's. The defender's
remaining Prize count is fixed through this bounded sequence.

Targets are one-hit KOs worth 1/2/3 Prizes. The defender chooses replacement
Active after each KO. Each attack turn offers at most one meaningful gust.
"""
from functools import lru_cache


@lru_cache(None)
def mixed_gust_attacks(
    active: int,
    bench: tuple[int, ...],
    bosses: int,
    catchers: int,
    own_prizes: int,
    opponent_prizes: int,
) -> int:
    if own_prizes <= 0:
        return 0
    if not bench:
        return 1

    choices = [_attack(active, bench, bosses, catchers, own_prizes, opponent_prizes)]
    for i, target in enumerate(bench):
        survivors = tuple(sorted((active,) + bench[:i] + bench[i + 1 :]))
        if bosses:
            choices.append(_attack(target, survivors, bosses - 1, catchers,
                                   own_prizes, opponent_prizes))
        if catchers and own_prizes > opponent_prizes:
            choices.append(_attack(target, survivors, bosses, catchers - 1,
                                   own_prizes, opponent_prizes))
    return min(choices)


def _attack(
    target: int,
    survivors: tuple[int, ...],
    bosses: int,
    catchers: int,
    own_prizes: int,
    opponent_prizes: int,
) -> int:
    if target >= own_prizes or not survivors:
        return 1
    return 1 + max(
        mixed_gust_attacks(
            promoted,
            survivors[:i] + survivors[i + 1 :],
            bosses,
            catchers,
            own_prizes - target,
            opponent_prizes,
        )
        for i, promoted in enumerate(survivors)
    )


def forced_first_gust(
    active: int,
    bench: tuple[int, ...],
    bosses: int,
    catchers: int,
    own_prizes: int,
    opponent_prizes: int,
    kind: str,
) -> int:
    """Best attack count after requiring a Boss (B) or Catcher (C) now."""
    if kind not in ("B", "C"):
        raise ValueError("kind must be B or C")
    if not bench or (kind == "B" and bosses == 0) or (
        kind == "C" and (catchers == 0 or own_prizes <= opponent_prizes)
    ):
        raise ValueError("requested first gust is unavailable")
    return min(
        _attack(
            target,
            tuple(sorted((active,) + bench[:i] + bench[i + 1 :])),
            bosses - (kind == "B"),
            catchers - (kind == "C"),
            own_prizes,
            opponent_prizes,
        )
        for i, target in enumerate(bench)
    )
