"""Exact public-reveal draw model for one hidden opposing Boss or Counter Catcher.

Conditional tactical model: every attack KOs one active Pokemon, both sides know
when the opposing gust source is drawn, and the opponent can pass.
"""
from fractions import Fraction
from functools import lru_cache


@lru_cache(None)
def win_probability(own_active, own_bench, enemy_active, enemy_bench,
                    own_bosses, own_catchers, own_prizes, enemy_prizes,
                    source, unseen, state="unseen"):
    """Optimal probability of our eventual win before our next attack.

    state: unseen (one source in unseen pile), held, spent.
    unseen: physical remaining unknown draw slots, including source if unseen.
    source: 'boss', 'counter', or 'none'.
    """
    if own_prizes <= 0:
        return Fraction(1)
    if enemy_prizes <= 0:
        return Fraction(0)
    outcomes = [(enemy_active, enemy_bench, own_bosses, own_catchers)]
    for i, prize in enumerate(enemy_bench):
        rest = tuple(sorted((enemy_active,) + enemy_bench[:i] + enemy_bench[i + 1:]))
        if own_bosses:
            outcomes.append((prize, rest, own_bosses-1, own_catchers))
        if own_catchers and own_prizes > enemy_prizes:
            outcomes.append((prize, rest, own_bosses, own_catchers-1))
    values = []
    for gained, remaining, bosses, catchers in outcomes:
        if gained >= own_prizes or not remaining:
            values.append(Fraction(1))
            continue
        values.append(min(
            _before_enemy_draw(own_active, own_bench, active,
                               remaining[:i]+remaining[i+1:],
                               bosses,catchers,own_prizes-gained,enemy_prizes,
                               source,unseen,state)
            for i, active in enumerate(remaining)))
    return max(values)


@lru_cache(None)
def _before_enemy_draw(oa,ob,ea,eb,b,c,op,ep,source,unseen,state):
    if source == "none" or state != "unseen":
        return _enemy_action(oa,ob,ea,eb,b,c,op,ep,source,unseen,state)
    if unseen <= 0:
        raise ValueError("undrawn source requires a positive remaining deck size")
    hit = _enemy_action(oa,ob,ea,eb,b,c,op,ep,source,unseen-1,"held")
    miss = _enemy_action(oa,ob,ea,eb,b,c,op,ep,source,unseen-1,"unseen") if unseen>1 else hit
    return (hit + (unseen-1)*miss)/unseen


@lru_cache(None)
def _enemy_action(oa,ob,ea,eb,b,c,op,ep,source,unseen,state):
    # Enemy can pass, forcing us to take another attack on the same target state.
    candidates = [win_probability(oa,ob,ea,eb,b,c,op,ep,source,unseen,state)]
    choices = [(oa,ob,state)]
    for i, reward in enumerate(ob):
        if state == "held" and (source == "boss" or (source == "counter" and ep > op)):
            choices.append((reward,tuple(sorted((oa,)+ob[:i]+ob[i+1:])),"spent"))
    for conceded, remaining, following in choices:
        if conceded >= ep or not remaining:
            candidates.append(Fraction(0))
        else:
            candidates.append(max(
                win_probability(active,remaining[:i]+remaining[i+1:],ea,eb,
                                b,c,op,ep-conceded,source,unseen,following)
                for i,active in enumerate(remaining)))
    return min(candidates)
