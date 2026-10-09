"""Finite-horizon gust minimax with a specified opponent Prize-taking clock.

An opponent clock is a nonempty tuple of 0..3 Prize cards taken after each
nonterminal attacking turn. The tuple repeats cyclically. This is an exogenous
scenario, not a claim that the opponent is guaranteed to take those Prizes.

The attacker starts with six Prizes. A one-hit KO gains the target's 1/2/3
Prizes, or wins immediately if it removes the opponent's final Pokemon.
The opponent chooses every promoted Active. If the opponent's clock takes
its final Prize before the attacker's next turn, the attacker loses.

Boss (Supporter) can target any opposing Bench Pokemon. Counter Catcher
(Item) does so only while own remaining Prizes > opponent remaining Prizes.
Other source-class restrictions and action interactions are deliberately absent.
"""
from functools import lru_cache

LOSS = float("inf")


@lru_cache(maxsize=None)
def attacks_to_win(
    active: int,
    bench: tuple[int, ...],
    bosses: int,
    catchers: int,
    own_prizes: int,
    opponent_prizes: int,
    turn: int,
    opponent_clock: tuple[int, ...],
) -> int | float:
    """Attacker's minimum worst-case attacks to win; inf means cannot force a win."""
    if own_prizes <= 0:
        return 0
    if opponent_prizes <= 0:
        return LOSS

    actions = [(active, bench, bosses, catchers)]
    for i, prize in enumerate(bench):
        survivors = tuple(sorted((active,) + bench[:i] + bench[i + 1 :]))
        if bosses:
            actions.append((prize, survivors, bosses - 1, catchers))
        if catchers and own_prizes > opponent_prizes:
            actions.append((prize, survivors, bosses, catchers - 1))

    return min(
        _after_attack(prize, survivors, b, c, own_prizes,
                      opponent_prizes, turn, opponent_clock)
        for prize, survivors, b, c in actions
    )


def _after_attack(
    prize: int,
    survivors: tuple[int, ...],
    bosses: int,
    catchers: int,
    own_prizes: int,
    opponent_prizes: int,
    turn: int,
    opponent_clock: tuple[int, ...],
) -> int | float:
    if prize >= own_prizes or not survivors:
        return 1
    next_opponent = opponent_prizes - opponent_clock[turn % len(opponent_clock)]
    if next_opponent <= 0:
        return LOSS
    return 1 + max(
        attacks_to_win(
            promoted,
            survivors[:i] + survivors[i + 1 :],
            bosses, catchers, own_prizes - prize,
            next_opponent, turn + 1, opponent_clock,
        )
        for i, promoted in enumerate(survivors)
    )


def forced_first_source(
    active: int,
    bench: tuple[int, ...],
    own_prizes: int,
    opponent_prizes: int,
    opponent_clock: tuple[int, ...],
    source: str,
) -> int | float:
    """Force first-turn use of Boss (B) or Counter Catcher (C), one each held."""
    if source not in ("B", "C"):
        raise ValueError("source must be B or C")
    if not bench or (source == "C" and own_prizes <= opponent_prizes):
        raise ValueError("forced source unavailable")
    b, c = (0, 1) if source == "B" else (1, 0)
    return min(
        _after_attack(
            prize, tuple(sorted((active,) + bench[:i] + bench[i + 1 :])),
            b, c, own_prizes, opponent_prizes, 0, opponent_clock,
        )
        for i, prize in enumerate(bench)
    )
