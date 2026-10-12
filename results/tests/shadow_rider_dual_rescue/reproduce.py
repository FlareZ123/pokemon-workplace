"""Independent reachability check for complementing Latias and Float Stone."""
from collections import deque
from itertools import product
from pathlib import Path
import json

from tools.shadow_rider_dual_rescue import max_two_prize_ko
BASE=(5,2,1,0,0,0)


def card(s,cid):
    root=Path(__file__).resolve().parents[3]
    data=json.loads((root/'resources'/'cards'/'en'/f'{s}.json').read_text('utf-8'))
    return next(c for c in data if c['id']==cid)


def oracle(energy,latias,garbotoxin,stadium,held,owner,tool_allowed,hp):
    pending=deque([(energy,0,False,False,False,held,owner)])
    seen=set()
    res=0
    while pending:
        e,active,gusted,retreated,supported,stone_in_hand,stone_owner=pending.popleft()
        st=(e,active,gusted,retreated,supported,stone_in_hand,stone_owner)
        if st in seen:continue
        seen.add(st)
        if gusted and active<3 and e[active]>=3 and 10+30*sum(e)>=hp:
            res=2
        if stone_in_hand and tool_allowed and stone_owner<0:
            for i in range(6):pending.append((e,active,gusted,retreated,supported,False,i))
        if not retreated:
            basic_free=latias and not garbotoxin and stadium!='path_to_peak'
            stone_free=active==stone_owner and stadium!='jamming_tower'
            cost=0 if stone_free or (basic_free and active>=3) else (
                2 if active<3 or (latias and active==5) else 1)
            if e[active]>=cost:
                updated=list(e)
                updated[active]-=cost
                for i in range(6):
                    if i!=active:pending.append((tuple(updated),i,gusted,True,supported,stone_in_hand,stone_owner))
        if not supported:
            for i in range(6):
                if i!=active:pending.append((e,i,True,retreated,True,stone_in_hand,stone_owner))
    return res


def main():
    garb=card('bw11','bw11-68')
    path=card('swsh6','swsh6-148')
    tower=card('sv6','sv6-153')
    latias=card('sv8','sv8-76')
    stone=card('xy8','xy8-137')
    assert garb['abilities'][0]['name']=='Garbotoxin'
    assert 'has a Pokémon Tool card attached to it' in garb['abilities'][0]['text']
    assert 'each Pokémon in play' in garb['abilities'][0]['text']
    assert tower['subtypes']==['Stadium']
    assert 'Pokémon Tools attached' in ' '.join(tower['rules'])
    assert 'have no effect' in ' '.join(tower['rules'])
    assert 'Pokémon with a Rule Box' in ' '.join(path['rules'])
    assert latias['retreatCost']==['Colorless','Colorless']
    assert stone['subtypes']==['Pokémon Tool']

    # With both rescue channels present, each Stadium alone is insufficient.
    for stadium in ('none','path_to_peak','jamming_tower'):
        assert max_two_prize_ko(BASE,latias_present=True,garbotoxin_active=False,
                                stadium=stadium,float_owner=0)[0]==2
    # Garbotoxin persists with a Tool attached despite Jamming suppressing its effect.
    assert max_two_prize_ko(BASE,latias_present=True,garbotoxin_active=True,
                            stadium='jamming_tower',float_owner=0)[0]==0
    for stadium in ('none','path_to_peak'):
        assert max_two_prize_ko(BASE,latias_present=True,garbotoxin_active=True,
                                stadium=stadium,float_owner=0)[0]==2
    assert max_two_prize_ko(BASE,latias_present=True,garbotoxin_active=True,
                            stadium='jamming_tower',float_held=True)[0]==0
    assert max_two_prize_ko(BASE,latias_present=True,garbotoxin_active=False,
                            stadium='jamming_tower',float_held=False)[0]==2
    assert max_two_prize_ko(BASE,latias_present=True,garbotoxin_active=False,
                            stadium='path_to_peak',float_held=False)[0]==0

    checks=0
    for e0,e1,e2,eb in product((3,4,5),(0,1,2),(0,1,2),(0,1)):
        e=(e0,e1,e2,0,0,eb)
        for latias in (False,True):
            for garbo in (False,True):
                for stadium in ('none','path_to_peak','jamming_tower'):
                    for held,owner in ((False,-1),(True,-1),(False,0),(False,1)):
                        for tool_allowed in (False,True):
                            got=max_two_prize_ko(e,latias_present=latias,garbotoxin_active=garbo,
                                                 stadium=stadium,float_held=held,float_owner=owner,
                                                 tool_play_allowed=tool_allowed)[0]
                            exp=oracle(e,latias,garbo,stadium,held,owner,tool_allowed,210)
                            assert got==exp,(e,latias,garbo,stadium,held,owner,tool_allowed)
                            checks+=1
    assert checks==5184
    print('Full source-print checks and independent BFS comparisons:',checks)
    print('Path or Jamming alone leaves a rescue; Garbotoxin+Jamming disables both')


if __name__=='__main__':
    main()
