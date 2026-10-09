"""Two-sided immediate-KO Prize race with reciprocal finite gust sources.

Our player uses Boss and conditional Counter. The opponent has finite
unrestricted Boss gust tokens, can otherwise attack our natural Active,
and may voluntarily end its turn without attacking. Both participants
choose their own new Active after suffering a KO.
"""
from functools import lru_cache


@lru_cache(None)
def can_force_win(own_active, own_bench, enemy_active, enemy_bench,
                  bosses, catchers, enemy_bosses, own_prizes,
                  enemy_prizes, enemy_can_pass):
    if own_prizes <= 0:
        return True
    if enemy_prizes <= 0:
        return False

    moves = [(enemy_active, enemy_bench, bosses, catchers)]
    for idx, target in enumerate(enemy_bench):
        survivors = tuple(sorted((enemy_active,) + enemy_bench[:idx] + enemy_bench[idx+1:]))
        if bosses:
            moves.append((target, survivors, bosses-1, catchers))
        if catchers and own_prizes > enemy_prizes:
            moves.append((target, survivors, bosses, catchers-1))

    for earned, survivors, b, c in moves:
        if earned >= own_prizes or not survivors:
            return True
        if all(_enemy_reply(own_active, own_bench, prom,
                            survivors[:i]+survivors[i+1:], b, c, enemy_bosses,
                            own_prizes-earned, enemy_prizes, enemy_can_pass)
               for i, prom in enumerate(survivors)):
            return True
    return False


@lru_cache(None)
def _enemy_reply(own_active, own_bench, enemy_active, enemy_bench,
                 bosses, catchers, enemy_bosses, own_prizes,
                 enemy_prizes, enemy_can_pass):
    if enemy_can_pass and not can_force_win(
        own_active, own_bench, enemy_active, enemy_bench,
        bosses, catchers, enemy_bosses, own_prizes, enemy_prizes,
        enemy_can_pass,
    ):
        return False

    moves = [(own_active, own_bench, enemy_bosses)]
    if enemy_bosses:
        for idx, target in enumerate(own_bench):
            survivors = tuple(sorted((own_active,) + own_bench[:idx] + own_bench[idx+1:]))
            moves.append((target, survivors, enemy_bosses-1))
    for earned, survivors, eb in moves:
        if earned >= enemy_prizes or not survivors:
            return False
        if not any(can_force_win(
            promoted, survivors[:i]+survivors[i+1:],
            enemy_active, enemy_bench, bosses, catchers, eb,
            own_prizes, enemy_prizes-earned, enemy_can_pass,
        ) for i, promoted in enumerate(survivors)):
            return False
    return True
