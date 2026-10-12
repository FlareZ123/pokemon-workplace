"""Source-print and independent bounded action enumeration for Max Geist."""

from collections import deque
from itertools import product
from pathlib import Path
import json

from tools.shadow_rider_guzma_damage import max_geist_damage, max_prizes


BASE = (5, 2, 1, 0, 0, 0)


def card(set_id, card_id):
    home = Path(__file__).resolve().parents[3]
    items = json.loads((home/'resources'/'cards'/'en'/f'{set_id}.json').read_text(encoding='utf-8'))
    return next(c for c in items if c['id'] == card_id)


def oracle(energies, source, hp, tool=-1, held=False, allowed=True):
    """Independent BFS world-transition search; no production recursion."""
    retreat_costs = [2,2,2,1,1,1]
    queue = deque([(energies,0,False,False,False,False)])
    seen=set()
    maximum=0
    while queue:
        e, active, gusted, used_retreat, used_supporter, used_item = queue.popleft()
        key=(e,active,gusted,used_retreat,used_supporter,used_item)
        if key in seen: continue
        seen.add(key)
        if gusted and active < 3 and e[active] >= 3 and 10+30*sum(e) >= hp:
            maximum=2
        if not used_retreat:
            cost = 0 if active == tool else retreat_costs[active]
            if e[active] >= cost:
                changed=list(e)
                changed[active]-=cost
                for promoted in range(6):
                    if promoted != active:
                        queue.append((tuple(changed),promoted,gusted,True,used_supporter,used_item))
        if held and allowed and not used_item:
            for promoted in range(6):
                if promoted != active:
                    queue.append((e,promoted,gusted,used_retreat,used_supporter,True))
        if not used_supporter:
            options = (active,) if source == 'boss' else tuple(i for i in range(6) if i!=active)
            for promoted in options:
                queue.append((e,promoted,True,used_retreat,True,used_item))
    return maximum


def main():
    vmax=card('swsh6','swsh6-75')
    v=card('swsh6','swsh6-74')
    stone=card('xy8','xy8-137')
    clefairy=card('sv9','sv9-56')
    tapu=card('sm2','sm2-60')
    mimikyu=card('sm2','sm2-58')
    assert vmax['hp']=='320' and vmax['retreatCost']==['Colorless','Colorless']
    geist=next(a for a in vmax['attacks'] if a['name']=='Max Geist')
    assert geist['cost']==['Colorless']*3 and geist['damage']=='10+'
    assert '30 more damage for each Psychic Energy attached to all of your Pokémon' in geist['text']
    assert v['hp']=='210' and any('takes 2 Prize cards' in r for r in v['rules'])
    assert 'has no Retreat Cost' in ' '.join(stone['rules'])
    assert clefairy['attacks'][0]['cost']==['Psychic','Colorless']
    assert tapu['retreatCost']==['Colorless'] and mimikyu['retreatCost']==['Colorless']
    assert max_geist_damage(BASE)==250
    assert max_geist_damage((3,2,1,0,0,0))==190

    assert max_prizes(BASE,'boss')[0]==2
    assert max_prizes(BASE,'guzma')[0]==0
    assert max_prizes(BASE,'guzma',target_hp=190)[0]==2
    assert max_prizes(BASE,'guzma',target_hp=200)[0]==0
    assert max_prizes(BASE,'guzma',float_stone_on=0)[0]==2
    assert max_prizes(BASE,'guzma',float_stone_on=1)[0]==2
    assert max_prizes(BASE,'guzma',switch_held=True)[0]==2
    assert max_prizes(BASE,'guzma',switch_held=True,items_allowed=False)[0]==0
    with_nine=(5,2,1,0,1,0)
    assert max_prizes(with_nine,'guzma')[0]==2
    assert max_geist_damage((3,2,1,0,1,0))==220

    checks=0
    for energy in product(range(3,6),range(3),range(3),(0,1)):
        board=(energy[0],energy[1],energy[2],0,energy[3],0)
        for hp in (190,200,210,220,230,250):
            for supporter in ('boss','guzma'):
                for tool in (-1,0,1):
                    for held,allowed in ((False,True),(True,True),(True,False)):
                        found=max_prizes(board,supporter,target_hp=hp,float_stone_on=tool,
                                         switch_held=held,items_allowed=allowed)[0]
                        assert found==oracle(board,supporter,hp,tool,held,allowed)
                        checks+=1
    print('source-print checks passed; BFS vs dynamic tree comparisons:',checks)
    print('8 Psychic: Boss 2, Guzma 0; 9 Psychic: Guzma 2')

if __name__ == '__main__':
    main()
