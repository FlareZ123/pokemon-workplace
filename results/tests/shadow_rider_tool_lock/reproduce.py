"""Exact tool-versus-Item effect permission; independent finite BFS check."""
from collections import deque
from itertools import product
from pathlib import Path
import json

from tools.shadow_rider_tool_lock import max_prizes

BASE=(5,2,1,0,0,0)


def card(set_code, cid):
    home=Path(__file__).resolve().parents[3]
    cards=json.loads((home/'resources'/'cards'/'en'/f'{set_code}.json').read_text('utf-8'))
    return next(x for x in cards if x['id']==cid)


def oracle(energy, source, stone_in_hand, item_allowed, tool_play_allowed,
           tool_effective, preattached, switch_held, target_hp):
    """Breadth-first physical turn search separate from memoized recursion."""
    retreat_cost=(2,2,2,1,1,1)
    start=(energy,0,False,False,False,False,preattached,stone_in_hand)
    queue=deque([start])
    seen=set()
    payout=0
    while queue:
        e,active,gusted,retreated,played_supporter,used_item,stone,held=queue.popleft()
        state=(e,active,gusted,retreated,played_supporter,used_item,stone,held)
        if state in seen: continue
        seen.add(state)
        if gusted and active < 3 and e[active]>=3 and 10+30*sum(e)>=target_hp:
            payout=2
        if held and tool_play_allowed and stone==-1:
            for target in range(6):
                queue.append((e,active,gusted,retreated,played_supporter,used_item,target,False))
        if not retreated:
            cost=0 if tool_effective and stone==active else retreat_cost[active]
            if e[active]>=cost:
                modified=list(e)
                modified[active]-=cost
                for target in range(6):
                    if target!=active:
                        queue.append((tuple(modified),target,gusted,True,played_supporter,used_item,stone,held))
        if switch_held and item_allowed and not used_item:
            for target in range(6):
                if target!=active:
                    queue.append((e,target,gusted,retreated,played_supporter,True,stone,held))
        if not played_supporter:
            own_targets=(active,) if source=='boss' else tuple(i for i in range(6) if i!=active)
            for target in own_targets:
                queue.append((e,target,True,retreated,True,used_item,stone,held))
    return payout


def main():
    vileplume=card('xy7','xy7-3')
    float_stone=card('xy8','xy8-137')
    tower=card('sv6','sv6-153')
    assert 'Each player can\'t play any Item cards' in vileplume['abilities'][0]['text']
    assert float_stone['subtypes']==['Pokémon Tool']
    assert 'has no Retreat Cost' in ' '.join(float_stone['rules'])
    assert tower['subtypes']==['Stadium']
    assert 'Pokémon Tools attached to each Pokémon' in ' '.join(tower['rules'])
    assert 'have no effect' in ' '.join(tower['rules'])

    # Item lock does not forbid Pokemon Tool attachment under current rules.
    assert max_prizes(BASE,tool_in_hand=True,item_allowed=False)[0]==2
    assert max_prizes(BASE,tool_in_hand=True,item_allowed=False,tool_play_allowed=False)[0]==0
    assert max_prizes(BASE,tool_in_hand=True,item_allowed=False,tool_effective=False)[0]==0
    assert max_prizes(BASE,tool_in_hand=False,item_allowed=False,preattached=0)[0]==2
    assert max_prizes(BASE,tool_in_hand=False,item_allowed=False,preattached=0,tool_effective=False)[0]==0
    assert max_prizes(BASE,tool_in_hand=False,item_allowed=False,switch_held=True)[0]==0
    assert max_prizes(BASE,tool_in_hand=False,item_allowed=True,switch_held=True)[0]==2

    comparisons=0
    for e0,e1,e2,ec in product((3,4,5),(0,1,2),(0,1,2),(0,1)):
        state=(e0,e1,e2,0,ec,0)
        for src in ('boss','guzma'):
            for item_allowed, tool_allowed, effective in product((False,True),repeat=3):
                for held,preattached in ((False,-1),(True,-1),(False,0),(False,1)):
                    for switch in (False,True):
                        observed=max_prizes(state,source=src,tool_in_hand=held,
                                            preattached=preattached,item_allowed=item_allowed,
                                            tool_play_allowed=tool_allowed,tool_effective=effective,
                                            switch_held=switch)[0]
                        expected=oracle(state,src,held,item_allowed,tool_allowed,
                                        effective,preattached,switch,210)
                        assert observed==expected, (state,src,held,preattached,item_allowed,tool_allowed,effective,switch)
                        comparisons+=1
    print('Card texts checked; exact independent BFS matches:',comparisons)
    print('Vileplume Item lock with Float Stone in hand -> KO; Jamming Tower -> no KO')


if __name__=='__main__':
    main()
