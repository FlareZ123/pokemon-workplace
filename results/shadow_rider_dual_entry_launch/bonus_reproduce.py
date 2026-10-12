"""Physical two-draw paired oracle for VMAX attrition vs access gains."""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations,product
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[2]))

from tools.shadow_rider_dual_entry_launch import ShadowRiderDualEntry
from tools.shadow_rider_bonus_vmax_competition import transition


def physical(model:ShadowRiderDualEntry, *, stone:bool,payment:str,v_hosts:int)->tuple[Fraction,Fraction,Fraction,Fraction]:
    names=(
        ['basic']*(model.other_basics-v_hosts)+['vhost']*v_hosts
        +['radiant']+['lele']*model.lele+['vmax']*model.vmax
        +['treasure']*model.treasure+['quick']*model.quick_ball
        +['heavy']*model.heavy_ball+['energy']*model.energy
        +['stone']+['filler']*(model.capacities[-1]-1)
    )
    assert len(names)==model.deck_size
    ids=set(range(len(names)))
    totals=[0,0,0,0]
    count=0

    def success(opening,active,prize,seen,deck)->bool:
        hand=seen-{active}
        if sum(names[i]=='vmax' for i in deck)<2:
            return False
        stone_id=next((i for i in hand if names[i]=='stone'),None)
        stone_ok=stone and stone_id is not None and any(names[i]=='vhost' for i in seen)
        def routes(target:str):
            if any(names[i]==target for i in hand):
                return [('held',None)]
            possible=[]
            if any(names[i]==target for i in deck):
                possible += [('normal',i) for i in hand if names[i] in ('treasure','quick')]
                if stone_ok:possible.append(('stone',stone_id))
            if any(names[i]==target for i in prize):
                possible += [('heavy',i) for i in hand if names[i]=='heavy']
                if stone_ok and any(names[i]=='heavy' for i in deck):
                    possible.append(('stone_heavy',stone_id))
            return possible
        for rr,ll in product(routes('radiant'),routes('lele')):
            selected=[i for _,i in (rr,ll) if i is not None]
            if len(selected)!=len(set(selected)):
                continue
            normals=int(rr[0]=='normal')+int(ll[0]=='normal')
            if payment=='energy':
                if normals>sum(names[i]=='energy' for i in hand):
                    continue
            else:
                reserved=(sum(any(names[i]==target for i in hand)
                              for target in ('radiant','lele'))
                          +len(selected))
                if normals>len(hand)-reserved:
                    continue
            return True
        return False

    for opener in combinations(range(model.deck_size),model.opening_size):
        opener_names=[names[i] for i in opener]
        if not any(x in ('basic','vhost','radiant','lele') for x in opener_names):
            continue
        lead=next(x for x in ('basic','vhost','lele','radiant') if x in opener_names)
        active=next(i for i in opener if names[i]==lead)
        remaining=ids-set(opener)
        for prize in combinations(sorted(remaining),model.prizes):
            after_prize=remaining-set(prize)
            for first in after_prize:
                rest=after_prize-{first}
                original=success(opener,active,prize,set(opener)|{first},rest)
                for second in rest:
                    follow=success(opener,active,prize,
                                   set(opener)|{first,second},rest-{second})
                    totals[0]+=int(original)
                    totals[1]+=int(follow)
                    totals[2]+=int((not original) and follow)
                    totals[3]+=int(original and (not follow))
                    count+=1
    return tuple(Fraction(value,count) for value in totals)


def test_toys():
    models=(
        (ShadowRiderDualEntry(13,3,1,2,1,3,1,1,1,1,2),1),
        (ShadowRiderDualEntry(14,3,1,2,2,3,1,0,1,1,2),1),
    )
    for m,hosts in models:
        for stone,payment in product((False,True),('energy','mechanical')):
            outcome=transition(m,stone=stone,payment=payment,v_hosts=hosts)
            brute=physical(m,stone=stone,payment=payment,v_hosts=hosts)
            assert (outcome.before,outcome.after,outcome.gain,outcome.loss)==brute,(
                m,stone,payment,outcome,brute)
    print('PASS: two independent coupled labeled-card decks, with Stone/no-Stone policies')


def benchmark():
    model=ShadowRiderDualEntry()
    for stone,payment in product((False,True),('energy','mechanical')):
        x=transition(model,stone=stone,payment=payment)
        assert x.before+x.gain-x.loss==x.after
        assert x.gain>x.loss>0
        print('Stone',stone,'payment',payment,
              'before',f'{float(x.before):.9%}',
              'gain',f'{float(x.gain):.9%}',
              'loss',f'{float(x.loss):.9%}',
              'after',f'{float(x.after):.9%}')


if __name__=='__main__':
    test_toys()
    benchmark()
