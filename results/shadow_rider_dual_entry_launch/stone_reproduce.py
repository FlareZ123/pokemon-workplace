"""Labeled physical verification of a Forest Seal Stone one-output fallback."""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations,product
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[2]))

from tools.shadow_rider_dual_entry_launch import ShadowRiderDualEntry
from tools.shadow_rider_stone_dual_entry import ShadowRiderStoneDualEntry


def physical(model:ShadowRiderStoneDualEntry,bonus:int,*,payment:str,
             require_wonder_tag:bool)->tuple[Fraction,Fraction]:
    base=model.base
    names = (
        ['basic']*(base.other_basics-model.v_hosts)
        + ['vhost']*model.v_hosts + ['radiant'] + ['lele']*base.lele
        + ['vmax']*base.vmax + ['treasure']*base.treasure
        + ['quick']*base.quick_ball + ['heavy']*base.heavy_ball
        + ['energy']*base.energy + ['stone']
        + ['filler']*(base.capacities[-1]-1)
    )
    assert len(names)==base.deck_size
    ids=set(range(len(names)))
    favorable_base=favorable_extension=all_worlds=0

    for opening in combinations(range(len(names)),base.opening_size):
        opener=[names[i] for i in opening]
        if not any(name in ('basic','vhost','lele','radiant') for name in opener):
            continue
        active_name=next((name for name in ('basic','vhost','lele','radiant')
                          if name in opener))
        active=next(i for i in opening if names[i]==active_name)
        remaining=ids-set(opening)
        for prize in combinations(sorted(remaining),base.prizes):
            deck=remaining-set(prize)
            for bonus_cards in combinations(sorted(deck),bonus):
                before_draw=deck-set(bonus_cards)
                for natural in before_draw:
                    observed=set((*opening,*bonus_cards,natural))
                    hand=observed-{active}
                    available_deck=before_draw-{natural}
                    if sum(names[i]=='vmax' for i in available_deck)<base.required_vmax:
                        all_worlds+=1
                        continue
                    stone=next((i for i in hand if names[i]=='stone'),None)
                    hosts=any(names[i]=='vhost' for i in observed)
                    usable_stone=stone is not None and hosts
                    def routes(target:str):
                        if target=='lele' and not require_wonder_tag:
                            return [('held',None)]
                        if any(names[i]==target for i in hand):
                            return [('held',None)]
                        choices=[]
                        if any(names[i]==target for i in available_deck):
                            choices += [('normal',i) for i in hand
                                        if names[i] in ('treasure','quick')]
                            if usable_stone:
                                choices.append(('stone',stone))
                        if any(names[i]==target for i in prize):
                            choices += [('heavy',i) for i in hand
                                        if names[i]=='heavy']
                            if usable_stone and any(names[i]=='heavy' for i in available_deck):
                                choices.append(('stone_heavy',stone))
                        return choices
                    before=after=False
                    for r,l in product(routes('radiant'),routes('lele')):
                        moves=(r,l)
                        selected=[which for how,which in moves if which is not None]
                        if len(selected)!=len(set(selected)):
                            continue
                        regular=sum(how=='normal' for how,_ in moves)
                        energy_count=sum(names[i]=='energy' for i in hand)
                        needs_stone=any(how in ('stone','stone_heavy') for how,_ in moves)
                        if payment=='energy':
                            if regular>energy_count:
                                continue
                        else:
                            retained=sum(bool(any(names[i]==target for i in hand))
                                         for target in (('radiant','lele') if require_wonder_tag else ('radiant',)))
                            reserved=retained + len(selected) + int(needs_stone and stone not in selected)
                            if len(hand)-reserved<regular:
                                continue
                        if not needs_stone:
                            before=True
                        else:
                            after=True
                    favorable_base+=int(before)
                    favorable_extension+=int(not before and after)
                    all_worlds+=1
    return (Fraction(favorable_base,all_worlds),
            Fraction(favorable_extension,all_worlds))


def test_physical():
    samples=(
        ShadowRiderStoneDualEntry(ShadowRiderDualEntry(12,3,1,2,1,2,1,1,1,1,1),1),
        ShadowRiderStoneDualEntry(ShadowRiderDualEntry(13,3,1,3,2,2,1,0,1,1,1),2),
    )
    for model in samples:
        for bonus,policy,wonder in product((0,1),('energy','mechanical'),(False,True)):
            analytical=model.probability(bonus,payment=policy,require_wonder_tag=wonder)
            observed=physical(model,bonus,payment=policy,require_wonder_tag=wonder)
            assert analytical==observed,(model,bonus,policy,wonder,analytical,observed)
    print('PASS: 2 labeled reduced-deck physical oracles, bonus/payment/role variants')


def benchmark():
    model=ShadowRiderStoneDualEntry()
    expected_radiant={
        'mechanical': 0.5310672402944376,
        'energy': 0.45643268335527415,
    }
    for policy in ('energy','mechanical'):
        without_stone,increment=model.probability(payment=policy,require_wonder_tag=True)
        assert without_stone==model.base.probability(payment=policy)
        old_radiant,stone_radiant=model.probability(payment=policy,require_wonder_tag=False)
        assert abs(float(old_radiant+stone_radiant)-expected_radiant[policy])<1e-12
        assert increment>0
        print(policy, 'dual without Stone',f'{float(without_stone):.12%}',
              'Stone increment',f'{float(increment):.12%}',
              'total',f'{float(without_stone+increment):.12%}',
              'Radiant-only Stone included',f'{float(old_radiant+stone_radiant):.12%}')


if __name__=='__main__':
    test_physical()
    benchmark()
