"""Exact Bernoulli opponent Prize clock."""
from functools import lru_cache
from fractions import Fraction

@lru_cache(None)
def optimal_win_probability(active, bench, bosses, catchers, own_prizes, opponent_prizes, p: Fraction):
    if own_prizes <= 0: return Fraction(1)
    if opponent_prizes <= 0: return Fraction(0)
    moves = [(active, bench, bosses, catchers)]
    for i, target in enumerate(bench):
        rest = tuple(sorted((active,) + bench[:i] + bench[i+1:]))
        if bosses: moves.append((target, rest, bosses-1, catchers))
        if catchers and own_prizes > opponent_prizes: moves.append((target, rest, bosses, catchers-1))
    outcomes = []
    for reward, rest, b, c in moves:
        if reward >= own_prizes or not rest:
            outcomes.append(Fraction(1))
            continue
        candidates = []
        for i, promoted in enumerate(rest):
            next_bench = rest[:i] + rest[i+1:]
            miss = optimal_win_probability(promoted,next_bench,b,c,own_prizes-reward,opponent_prizes,p)
            hit = optimal_win_probability(promoted,next_bench,b,c,own_prizes-reward,max(0,opponent_prizes-2),p)
            candidates.append((1-p)*miss + p*hit)
        outcomes.append(min(candidates))
    return max(outcomes)

@lru_cache(None)
def robust_win_against_score_choice(active, bench, bosses, catchers, own_prizes, opponent_prizes):
    if own_prizes <= 0: return True
    if opponent_prizes <= 0: return False
    moves = [(active, bench, bosses, catchers)]
    for i, target in enumerate(bench):
        rest = tuple(sorted((active,) + bench[:i] + bench[i+1:]))
        if bosses: moves.append((target, rest, bosses-1, catchers))
        if catchers and own_prizes > opponent_prizes: moves.append((target, rest, bosses, catchers-1))
    for reward, rest, b, c in moves:
        if reward >= own_prizes or not rest: return True
        if all(robust_win_against_score_choice(p, rest[:i] + rest[i+1:], b,c,own_prizes-reward,max(0,opponent_prizes-gain)) for i,p in enumerate(rest) for gain in (0,2)):
            return True
    return False
