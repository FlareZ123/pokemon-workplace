"""Exact opposing mixed-source arrival race with reply-indexed Item/Supporter locks."""
from fractions import Fraction
from functools import lru_cache
from tools.multisource_opponent_gust_race import opening_zone_distribution


@lru_cache(None)
def win_probability(oa, ob, ea, eb, own_b, own_c, ours, theirs,
                    hand_b, hand_c, deck_b, deck_c, deck_size,
                    enemy_replies, boss_blocked, counter_blocked):
    """Our win chance, indexed by number of completed opponent replies."""
    if ours <= 0:
        return Fraction(1)
    if theirs <= 0:
        return Fraction(0)
    actions = [(ea, eb, own_b, own_c)]
    for i, prize in enumerate(eb):
        remain = tuple(sorted((ea,) + eb[:i] + eb[i + 1:]))
        if own_b:
            actions.append((prize, remain, own_b - 1, own_c))
        if own_c and ours > theirs:
            actions.append((prize, remain, own_b, own_c - 1))
    best = Fraction(0)
    for gained, remaining, b, c in actions:
        if gained >= ours or not remaining:
            return Fraction(1)
        worst = min(
            _opponent_draw(oa, ob, active, remaining[:j] + remaining[j + 1:],
                           b, c, ours - gained, theirs, hand_b, hand_c,
                           deck_b, deck_c, deck_size, enemy_replies + 1,
                           boss_blocked, counter_blocked)
            for j, active in enumerate(remaining))
        best = max(best, worst)
    return best


@lru_cache(None)
def _opponent_draw(oa, ob, ea, eb, b, c, ours, theirs,
                   hb, hc, db, dc, n, reply, boss_blocked, counter_blocked):
    if n == 0:
        return _opponent_action(oa, ob, ea, eb, b, c, ours, theirs,
                                hb, hc, db, dc, n, reply, boss_blocked, counter_blocked)
    terms = []
    if db:
        terms.append(Fraction(db, n) * _opponent_action(
            oa, ob, ea, eb, b, c, ours, theirs,
            hb + 1, hc, db - 1, dc, n - 1, reply, boss_blocked, counter_blocked))
    if dc:
        terms.append(Fraction(dc, n) * _opponent_action(
            oa, ob, ea, eb, b, c, ours, theirs,
            hb, hc + 1, db, dc - 1, n - 1, reply, boss_blocked, counter_blocked))
    if n > db + dc:
        terms.append(Fraction(n - db - dc, n) * _opponent_action(
            oa, ob, ea, eb, b, c, ours, theirs,
            hb, hc, db, dc, n - 1, reply, boss_blocked, counter_blocked))
    return sum(terms, Fraction(0))


@lru_cache(None)
def _opponent_action(oa, ob, ea, eb, b, c, ours, theirs,
                     hb, hc, db, dc, n, reply, boss_blocked, counter_blocked):
    # The opponent can pass. Locked source copies stay in hand for later turns.
    outcomes = [win_probability(oa, ob, ea, eb, b, c, ours, theirs,
                                hb, hc, db, dc, n, reply,
                                boss_blocked, counter_blocked)]
    attacks = [(oa, ob, hb, hc)]
    for i, reward in enumerate(ob):
        remaining = tuple(sorted((oa,) + ob[:i] + ob[i + 1:]))
        if hb and reply not in boss_blocked:
            attacks.append((reward, remaining, hb - 1, hc))
        if hc and theirs > ours and reply not in counter_blocked:
            attacks.append((reward, remaining, hb, hc - 1))
    for reward, remaining, new_b, new_c in attacks:
        if reward >= theirs or not remaining:
            outcomes.append(Fraction(0))
        else:
            outcomes.append(max(
                win_probability(active, remaining[:i] + remaining[i + 1:],
                                ea, eb, b, c, ours, theirs - reward,
                                new_b, new_c, db, dc, n, reply,
                                boss_blocked, counter_blocked)
                for i, active in enumerate(remaining)))
    return min(outcomes)


def initial_win_probability(oa, ob, ea, eb, own_b, own_c, theirs,
                            basics, bosses, counters, boss_blocked=(),
                            counter_blocked=(), total=60, hand_size=7,
                            prize_count=6):
    """Opening-conditioned game; locks list 1-based opponent reply numbers."""
    physical = opening_zone_distribution(basics, bosses, counters,
                                         total, hand_size, prize_count)
    deck_size = total - hand_size - prize_count
    return sum((weight * win_probability(
        oa, ob, ea, eb, own_b, own_c, 6, theirs,
        hb, hc, db, dc, deck_size, 0,
        tuple(boss_blocked), tuple(counter_blocked))
                for (hb, hc, db, dc), weight in physical.items()), Fraction(0))
