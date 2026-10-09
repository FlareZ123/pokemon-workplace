"""Finite two-sided six-Prize minimax with Boss and Counter on either team."""
from functools import lru_cache


@lru_cache(None)
def can_force_win(own_active, own_bench, enemy_active, enemy_bench,
                  own_bosses, own_catchers, enemy_bosses, enemy_catchers,
                  own_prizes, enemy_prizes, enemy_can_pass):
    if own_prizes <= 0: return True
    if enemy_prizes <= 0: return False
    candidates = [(enemy_active, enemy_bench, own_bosses, own_catchers)]
    for i, reward in enumerate(enemy_bench):
        remaining = tuple(sorted((enemy_active,) + enemy_bench[:i] + enemy_bench[i+1:]))
        if own_bosses: candidates.append((reward,remaining,own_bosses-1,own_catchers))
        if own_catchers and own_prizes > enemy_prizes:
            candidates.append((reward,remaining,own_bosses,own_catchers-1))
    for gained, remaining, b, c in candidates:
        if gained >= own_prizes or not remaining: return True
        if all(_opponent_turn(own_active,own_bench,p,remaining[:i]+remaining[i+1:],
                              b,c,enemy_bosses,enemy_catchers,
                              own_prizes-gained,enemy_prizes,enemy_can_pass)
               for i,p in enumerate(remaining)): return True
    return False


@lru_cache(None)
def _opponent_turn(own_active,own_bench,enemy_active,enemy_bench,
                   own_bosses,own_catchers,enemy_bosses,enemy_catchers,
                   own_prizes,enemy_prizes,enemy_can_pass):
    if enemy_can_pass and not can_force_win(own_active,own_bench,enemy_active,enemy_bench,
                                           own_bosses,own_catchers,enemy_bosses,enemy_catchers,
                                           own_prizes,enemy_prizes,enemy_can_pass):return False
    candidates=[(own_active,own_bench,enemy_bosses,enemy_catchers)]
    for i,reward in enumerate(own_bench):
        remaining=tuple(sorted((own_active,)+own_bench[:i]+own_bench[i+1:]))
        if enemy_bosses: candidates.append((reward,remaining,enemy_bosses-1,enemy_catchers))
        if enemy_catchers and enemy_prizes>own_prizes:
            candidates.append((reward,remaining,enemy_bosses,enemy_catchers-1))
    for conceded,remaining,eb,ec in candidates:
        if conceded>=enemy_prizes or not remaining:return False
        if not any(can_force_win(p,remaining[:i]+remaining[i+1:],enemy_active,enemy_bench,
                                 own_bosses,own_catchers,eb,ec,own_prizes,
                                 enemy_prizes-conceded,enemy_can_pass)
                   for i,p in enumerate(remaining)):return False
    return True
