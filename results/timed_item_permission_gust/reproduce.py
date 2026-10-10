"""Timed Item permission can have off-window strategic effects through proactive Switch."""
from collections import Counter, defaultdict
from fractions import Fraction
from functools import lru_cache
from itertools import product
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from tools.timed_item_lock_gust import attacker_draw
from tools.two_sided_stochastic_escape import attacker_draw as static_draw

ACTIVE=(3,2)
BENCH=((2,2),(3,2))
EXPECTED={
  '000':Fraction(65,12), '001':Fraction(49,9),
  '010':Fraction(11,2), '011':Fraction(401,72),
  '100':Fraction(787,144), '101':Fraction(395,72),
  '110':Fraction(199,36), '111':Fraction(401,72),
}


def verify_exact_masks():
    observations=defaultdict(set)
    n=0
    for bits in product((False,True),repeat=5):
        observed=attacker_draw(ACTIVE,BENCH,0,1,11,0,1,11,bits)
        signature=''.join('1' if bits[i] else '0' for i in (0,2,3))
        assert observed==EXPECTED[signature],(bits,signature,observed)
        observations[signature].add(observed)
        n+=1
    assert n==32 and len(observations)==8
    assert all(len(outcomes)==1 for outcomes in observations.values())
    assert attacker_draw(ACTIVE,BENCH,0,1,11,0,1,11,(False,)*5) == static_draw(
        ACTIVE,BENCH,0,1,11,0,1,11,6,False)
    assert attacker_draw(ACTIVE,BENCH,0,1,11,0,1,11,(True,)*5) == static_draw(
        ACTIVE,BENCH,0,1,11,0,1,11,6,True)
    print('Exact 32-mask table: only turns 1, 3 and 4 are relevant in the fixture')
    print('Masked outcomes:', EXPECTED)


@lru_cache(None)
def oracle_attack(active,bench,hand,boss_order,held_switch,switch_order,mask,elapsed,needed):
    hand+=boss_order[0]=='G'
    future=boss_order[1:]
    options=[(active,bench,hand)]
    if hand:
        for i,p in enumerate(bench):
            rest=tuple(sorted((active,)+bench[:i]+bench[i+1:]))
            options.append((p,rest,hand-1))
    costs=[]
    for (prize,hits),survivors,held in options:
        if hits==1:
            if prize>=needed or not survivors:
                costs.append(1)
            else:
                costs.append(1+max(oracle_defend(
                    p,survivors[:i]+survivors[i+1:],held,future,
                    held_switch,switch_order,mask,elapsed+1,needed-prize
                ) for i,p in enumerate(survivors)))
        else:
            costs.append(1+oracle_defend(
                (prize,hits-1),survivors,held,future,
                held_switch,switch_order,mask,elapsed+1,needed))
    return min(costs)


@lru_cache(None)
def oracle_defend(active,bench,boss_hand,boss_future,held_switch,
                  switch_order,mask,elapsed,needed):
    held_switch+=switch_order[0]=='S'
    future=switch_order[1:]
    values=[oracle_attack(active,bench,boss_hand,boss_future,
                          held_switch,future,mask,elapsed,needed)]
    if held_switch and (elapsed>len(mask) or mask[elapsed-1]):
        for i,p in enumerate(bench):
            rest=tuple(sorted((active,)+bench[:i]+bench[i+1:]))
            values.append(oracle_attack(p,rest,boss_hand,boss_future,
                                        held_switch-1,future,mask,elapsed,needed))
    return max(values)


def physical_oracle():
    num=0
    counterexamples=[]
    divergent=[]
    for mask in product((False,True),repeat=5):
        histogram=Counter()
        for boss_pos in range(12):
            boss_order=tuple('G' if i==boss_pos else 'F' for i in range(12))
            for switch_pos in range(12):
                switch_order=tuple('S' if i==switch_pos else 'F' for i in range(12))
                val=oracle_attack(ACTIVE,BENCH,0,boss_order,0,switch_order,mask,0,6)
                histogram[val]+=1
                if mask==(True,False,False,False,False) and val==6 and boss_pos<3 and switch_pos==0:
                    counterexamples.append((boss_pos,switch_pos,val))
        total=sum(Fraction(count*value,144) for value,count in histogram.items())
        signature=''.join('1' if mask[i] else '0' for i in (0,2,3))
        gap=total-EXPECTED[signature]
        expected_gap=Fraction(-1,48) if mask[2] and not mask[3] else Fraction(0)
        assert gap==expected_gap,(mask,histogram,total,EXPECTED[signature])
        if gap:
            divergent.append(mask)
        num+=144
    assert num==4608 and len(divergent)==8
    assert counterexamples, 'Need a concrete proactive first-turn Switch success'
    print(f'Full-order two-player oracle: {num} worlds; {len(divergent)} masks diverge by -1/48, demonstrating future knowledge sensitivity')
    print(f'Proactive first-turn Switch witness: {counterexamples[:2]}')


def verify_source():
    with (ROOT/'resources'/'cards'/'en'/'sv1.json').open(encoding='utf-8') as f:
        card=next(c for c in json.load(f) if c['id']=='sv1-194')
    assert card['name']=='Switch' and 'Item' in card['subtypes']
    print('Verified Switch is an Item; mask is an exogenous per-turn Item permission overlay')


if __name__=='__main__':
    verify_source()
    verify_exact_masks()
    physical_oracle()
    print('All temporal Item permission tests passed.')
