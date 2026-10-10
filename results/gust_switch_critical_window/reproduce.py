"""Gust–Switch complementarity theorem for a two-high-one-low Prize endgame."""
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from itertools import combinations
from math import comb
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from tools.two_sided_stochastic_escape import attacker_draw

ACTIVE=(3,2)
BENCH=((2,2),(3,2))


def formula(boss_deck_size: int, defender_size: int, switches: int) -> Fraction:
    assert boss_deck_size >= 6 and defender_size >= 5
    assert 0 <= switches <= defender_size
    def miss(k):
        return Fraction(comb(defender_size-k,switches), comb(defender_size,switches)) if switches <= defender_size-k else Fraction(0)
    return 6 - Fraction(6,boss_deck_size)*miss(3) - Fraction(1,boss_deck_size)*miss(4)


def verify_exact():
    count=0
    for boss_deck_size in range(6,15):
        for defender_size in range(5,15):
            for switches in range(5):
                observed=attacker_draw(ACTIVE,BENCH,0,1,boss_deck_size-1,
                                       0,switches,defender_size-switches)
                assert observed==formula(boss_deck_size,defender_size,switches)
                count+=1
    assert count==450
    for switches in range(5):
        assert attacker_draw(ACTIVE,BENCH,0,0,12,0,switches,12-switches)==6
    assert formula(12,12,0)==Fraction(65,12)
    assert formula(12,12,1)==Fraction(401,72)
    assert formula(12,12,2)==Fraction(1127,198)
    assert formula(12,12,4)==Fraction(17407,2970)
    print(f'Exact one-Boss multi-Switch formula: {count} parameter cases, no-Boss invariance and four landmarks passed')


def multiple_boss_nonmonotonicity():
    gains = []
    for bosses in range(5):
        without = attacker_draw(ACTIVE, BENCH, 0, bosses, 12-bosses, 0, 0, 12)
        with_switch = attacker_draw(ACTIVE, BENCH, 0, bosses, 12-bosses, 0, 1, 11)
        gains.append(with_switch - without)
    assert gains == [Fraction(0), Fraction(11, 72), Fraction(5, 24),
                     Fraction(9, 44), Fraction(28, 165)], gains
    assert gains[0] < gains[1] < gains[2] > gains[3] > gains[4]
    print('One-Switch marginal value vs 0..4 Boss: ' + str(gains))


@lru_cache(None)
def physical_attacker(active,bench,hand,boss_order,switch_hand,switch_order,needed):
    hand+=boss_order[0]=='G'
    boss_order=boss_order[1:]
    options=[(active,bench,hand)]
    if hand:
        for i,target in enumerate(bench):
            options.append((target,tuple(sorted((active,)+bench[:i]+bench[i+1:])),hand-1))
    answers=[]
    for (reward,hits),survivors,held in options:
        if hits==1:
            if reward>=needed or not survivors:
                answers.append(1)
            else:
                answers.append(1+max(physical_defender(
                    p,survivors[:i]+survivors[i+1:],held,boss_order,
                    switch_hand,switch_order,needed-reward
                ) for i,p in enumerate(survivors)))
        else:
            answers.append(1+physical_defender(
                (reward,hits-1),survivors,held,boss_order,
                switch_hand,switch_order,needed))
    return min(answers)


@lru_cache(None)
def physical_defender(active,bench,hand,boss_order,switch_hand,switch_order,needed):
    switch_hand+=switch_order[0]=='S'
    switch_order=switch_order[1:]
    options=[physical_attacker(active,bench,hand,boss_order,switch_hand,switch_order,needed)]
    if switch_hand:
        for i,p in enumerate(bench):
            rest=tuple(sorted((active,)+bench[:i]+bench[i+1:]))
            options.append(physical_attacker(p,rest,hand,boss_order,switch_hand-1,switch_order,needed))
    return max(options)


def independent_orders():
    cases=0
    for switches in range(1,4):
        counts=Counter()
        for boss_position in range(12):
            boss_order=tuple('G' if i==boss_position else 'F' for i in range(12))
            for switch_positions in combinations(range(12),switches):
                switch_order=tuple('S' if i in switch_positions else 'F' for i in range(12))
                outcome=physical_attacker(ACTIVE,BENCH,0,boss_order,0,switch_order,6)
                earliest_switch=min(switch_positions)
                expected=(6 if (boss_position>=4 or (boss_position<3 and earliest_switch<3)
                                 or (boss_position==3 and earliest_switch<4))
                          else (4 if boss_position<3 else 5))
                assert outcome==expected,(boss_position,switch_positions,outcome,expected)
                counts[outcome]+=1
        n=12*comb(12,switches)
        avg=sum(Fraction(k*v,n) for k,v in counts.items())
        assert avg==formula(12,12,switches)
        cases+=n
    assert cases==3576, cases
    print(f'Independent full physical-order oracle: {cases} paired worlds across Switch=1..3, exact match')


def source_card_types():
    for set_name,card_id,card_name,subtype in (
        ('swsh2','swsh2-154',"Boss's Orders",'Supporter'),
        ('sv1','sv1-194','Switch','Item'),
    ):
        with (ROOT/'resources'/'cards'/'en'/f'{set_name}.json').open(encoding='utf-8') as f:
            card=next(c for c in json.load(f) if c['id']==card_id)
        assert card['name']==card_name and subtype in card['subtypes']
    print('Source checks: Boss Supporter, Switch Item')


if __name__=='__main__':
    source_card_types()
    verify_exact()
    multiple_boss_nonmonotonicity()
    independent_orders()
    print('All gust–Switch critical-window theorem tests passed.')
