"""Independent explicit-action oracle for Latias Ability lock and Guzma."""
from collections import deque
from itertools import product
from pathlib import Path
import json

from tools.shadow_rider_latias_lock import max_two_prize_gust
BASE=(5,2,1,0,0,0)


def card(s, cid):
    home=Path(__file__).resolve().parents[3]
    j=json.loads((home/'resources'/'cards'/'en'/f'{s}.json').read_text('utf-8'))
    return next(x for x in j if x['id']==cid)


def oracle(energy, latias, source, lock, hp):
    q=deque([(energy,0,False,False,False)])
    seen=set()
    ans=0
    while q:
        e, active, gusted, retreated, supported=q.popleft()
        state=(e,active,gusted,retreated,supported)
        if state in seen:continue
        seen.add(state)
        if gusted and active < 3 and e[active] >= 3 and 10+30*sum(e) >= hp:
            ans=2
        if not retreated:
            ability_live=latias and (lock=='none' or (lock=='active_weezing' and gusted))
            cost=0 if ability_live and active >= 3 else (2 if active < 3 or (latias and active==5) else 1)
            if e[active]>=cost:
                remaining=list(e)
                remaining[active]-=cost
                for other in range(6):
                    if other!=active:
                        q.append((tuple(remaining),other,gusted,True,supported))
        if not supported:
            own=(active,) if source=='boss' else tuple(i for i in range(6) if i!=active)
            for other in own:q.append((e,other,True,retreated,True))
    return ans


def main():
    latias=card('sv8','sv8-76')
    weezing=card('swsh2','swsh2-113')
    path=card('swsh6','swsh6-148')
    assert latias['abilities'][0]['name']=='Skyliner'
    assert latias['abilities'][0]['text']=='Your Basic Pokémon in play have no Retreat Cost.'
    assert 'As long as this Pokémon is in the Active Spot' in weezing['abilities'][0]['text']
    assert "your opponent's Pokémon in play have no Abilities" in weezing['abilities'][0]['text']
    assert 'Pokémon with a Rule Box in play' in ' '.join(path['rules'])
    assert 'have no Abilities' in ' '.join(path['rules'])
    assert 'ex' in latias['subtypes']
    assert latias['retreatCost']==['Colorless','Colorless']

    # The sixth own slot is a powered-off Basic Latias ex rather than Mimikyu.
    assert max_two_prize_gust(BASE,latias_on_bench=True,lock='none')[0]==2
    assert max_two_prize_gust(BASE,latias_on_bench=True,lock='active_weezing')[0]==2
    assert max_two_prize_gust(BASE,latias_on_bench=True,lock='path_to_peak')[0]==0
    assert max_two_prize_gust(BASE,latias_on_bench=False,lock='none')[0]==0
    assert max_two_prize_gust(BASE,latias_on_bench=False,lock='active_weezing')[0]==0
    assert max_two_prize_gust(BASE,latias_on_bench=True,lock='path_to_peak',source='boss')[0]==2
    assert max_two_prize_gust(BASE,latias_on_bench=True,lock='active_weezing')[1][0].startswith('guzma')

    checks=0
    for e0,e1,e2,basicenergy in product((3,4,5),(0,1,2),(0,1,2),(0,1,2)):
        state=(e0,e1,e2,0,0,basicenergy)
        for latias in (False,True):
            for source in ('guzma','boss'):
                for lock in ('none','active_weezing','path_to_peak'):
                    for hp in (190,200,210,220):
                        obtained=max_two_prize_gust(state,latias_on_bench=latias,source=source,
                                                       lock=lock,target_hp=hp)[0]
                        assert obtained==oracle(state,latias,source,lock,hp)
                        checks+=1
    assert checks==3888
    print('Ability source text verified; dynamic lock/action BFS checked:',checks)
    print('Latias active / active-only Weezing removed: 2-Prize KO; Path to Peak: no KO')


if __name__=='__main__':
    main()
