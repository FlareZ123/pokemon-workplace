"""Exact Arc/Shoes Prize policy with a uniformly exchangeable deck tail.

The full posterior stores Prize position identities, one uncertain deck top,
and remaining deck counts. This avoids materializing deck-tail permutations.
"""
from collections import Counter, defaultdict
from fractions import Fraction
from functools import lru_cache
from itertools import permutations

GROUPS = ('T', 'A', 'S', 'F')


def normalize(worlds):
    mass = sum(worlds.values(), Fraction())
    if not mass:
        raise ValueError('empty belief')
    return tuple(sorted(((s, p / mass) for s, p in worlds.items() if p),
                        key=lambda x: repr(x[0])))


def initial(prizes, deck):
    arrangements = set(permutations(prizes))
    counts = Counter(deck)
    size = len(deck)
    worlds = defaultdict(Fraction)
    for slots in arrangements:
        for g in GROUPS:
            if counts[g]:
                tail = tuple(counts[x] - int(x == g) for x in GROUPS)
                worlds[(slots, g, tail)] += Fraction(counts[g],size*len(arrangements))
    return normalize(worlds)


def advance(belief):
    worlds = defaultdict(Fraction)
    for (slots, _top, tail), p in belief:
        size = sum(tail)
        if not size:
            worlds[(slots,None,tail)] += p
            continue
        for i, n in enumerate(tail):
            if n:
                next_tail = list(tail)
                next_tail[i] -= 1
                worlds[(slots,GROUPS[i],tuple(next_tail))] += p * Fraction(n,size)
    return normalize(worlds)


def swap(belief, slot):
    worlds = defaultdict(Fraction)
    for (prizes, top, tail), p in belief:
        out = prizes[slot]
        replaced = prizes[:slot] + (top,) + prizes[slot+1:]
        worlds[(replaced,out,tail)] += p
    return normalize(worlds)


def observe(belief):
    groups = defaultdict(lambda:defaultdict(Fraction))
    for state, p in belief:
        groups[state[1]][state] += p
    return {card:(sum(m.values(),Fraction()),normalize(m))
            for card,m in groups.items()}


@lru_cache(None)
def optimize(belief, arcs, shoes, allow_discard=True):
    """Optimal finite-horizon probability of taking target T into hand."""
    if not belief[0][0][1] or not (arcs or shoes):
        return Fraction()
    events = observe(belief)
    actions = [Fraction()]
    if arcs:
        total = Fraction()
        for _, (p, seen) in events.items():
            choices = [optimize(seen,arcs-1,shoes,allow_discard)]
            choices.extend(optimize(swap(seen,slot),arcs-1,shoes,allow_discard)
                           for slot in range(len(seen[0][0][0])))
            total += p * max(choices)
        actions.append(total)
    if shoes:
        total = Fraction()
        for top, (p, seen) in events.items():
            take = Fraction(1) if top == 'T' else optimize(
                advance(seen),arcs+int(top == 'A'),
                shoes-1+int(top == 'S'),allow_discard)
            if allow_discard and sum(seen[0][0][2]) > 0:
                discarded = Fraction()
                for drawn, (q, conditioned) in observe(advance(seen)).items():
                    next_value = Fraction(1) if drawn == 'T' else optimize(
                        advance(conditioned),arcs+int(drawn == 'A'),
                        shoes-1+int(drawn == 'S'),allow_discard)
                    discarded += q * next_value
                take = max(take,discarded)
            total += p * take
        actions.append(total)
    return max(actions)
