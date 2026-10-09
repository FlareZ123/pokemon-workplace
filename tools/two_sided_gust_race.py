"""Two-sided exact gust race with physical Prize-valued boards and optional opponent pass.

Every attack is an automatic single-target Knock Out. The acting player may
use at most one of their already available Boss / Counter Catcher tokens.
The defender promotes after our KO; the opponent then either attacks our
Active or passes (if allowed). We choose the promotion after our own KO.
Both players begin with existing boards. Neither may bench more Pokemon.
"""
from functools import lru_cache


@lru_cache(maxsize=None)
def can_force_win(own_active: int, own_bench: tuple[int, ...],
                  enemy_active: int, enemy_bench: tuple[int, ...],
                  bosses: int, catchers: int, own_prizes: int,
                  enemy_prizes: int, allow_enemy_pass: bool) -> bool:
    """Exact minimax from our attack turn; True means a forced victory."""
    if own_prizes <= 0:
        return True
    if enemy_prizes <= 0:
        return False

    actions = [(enemy_active, enemy_bench, bosses, catchers)]
    for i, target in enumerate(enemy_bench):
        rest = tuple(sorted((enemy_active,) + enemy_bench[:i] + enemy_bench[i + 1:]))
        if bosses:
            actions.append((target, rest, bosses - 1, catchers))
        if catchers and own_prizes > enemy_prizes:
            actions.append((target, rest, bosses, catchers - 1))

    for earned, survivors, next_bosses, next_catchers in actions:
        if earned >= own_prizes or not survivors:
            return True
        if all(_after_enemy_promotion(
            own_active, own_bench, promoted,
            survivors[:i] + survivors[i + 1:], next_bosses, next_catchers,
            own_prizes - earned, enemy_prizes, allow_enemy_pass,
        ) for i, promoted in enumerate(survivors)):
            return True
    return False


@lru_cache(maxsize=None)
def _after_enemy_promotion(own_active: int, own_bench: tuple[int, ...],
                           enemy_active: int, enemy_bench: tuple[int, ...],
                           bosses: int, catchers: int, own_prizes: int,
                           enemy_prizes: int, allow_enemy_pass: bool) -> bool:
    """Opponent minimizes our outcome; choose pass or KO, then we promote."""
    if allow_enemy_pass and not can_force_win(
        own_active, own_bench, enemy_active, enemy_bench,
        bosses, catchers, own_prizes, enemy_prizes, allow_enemy_pass,
    ):
        return False
    if own_active >= enemy_prizes or not own_bench:
        return False
    return any(can_force_win(
        promoted, own_bench[:i] + own_bench[i + 1:],
        enemy_active, enemy_bench, bosses, catchers, own_prizes,
        enemy_prizes - own_active, allow_enemy_pass,
    ) for i, promoted in enumerate(own_bench))
