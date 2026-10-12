"""Exact Aichi first-turn dual Bench-entry study and independent physical oracle."""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations,product
from pathlib import Path
import json
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[2]))

from tools.shadow_rider_dual_entry_launch import ShadowRiderDualEntry


def physical(model:ShadowRiderDualEntry,bonus:int,*,payment:str,
             require_wonder_tag:bool,role_aware:bool)->Fraction:
    names=('other','r','l','v','t','q','h','e','f')
    cards=[name for name,count in zip(names,model.capacities) for _ in range(count)]
    success=total=0
    universe=set(range(len(cards)))
    for op in combinations(range(len(cards)),model.opening_size):
        opening=[cards[i] for i in op]
        if not any(x in ('other','r','l') for x in opening):continue
        active=('other' if 'other' in opening else 'l' if 'l' in opening else 'r')
        active_id=next(i for i in op if cards[i]==active)
        rest=universe-set(op)
        for prize in combinations(sorted(rest),model.prizes):
            p=[cards[i] for i in prize]
            deck=rest-set(prize)
            for extras in combinations(sorted(deck),bonus):
                after=deck-set(extras)
                for natural in after:
                    observed=[cards[i] for i in (*op,*extras,natural)]
                    hand=[cards[i] for i in (*op,*extras,natural) if (i!=active_id or not role_aware)]
                    if not role_aware:
                        # Role-blind projection deliberately credits Active
                        # target identities as if they remained in hand.
                        pass
                    seen_v=observed.count('v')
                    deck_v=model.vmax-seen_v-p.count('v')
                    ok=False
                    if deck_v>=model.required_vmax:
                        rheld='r' in hand
                        lheld='l' in hand
                        r_paths=['held'] if rheld else (['deck'] if 'r' in [cards[i] for i in deck-set(extras)-{natural}] else [])+(['prize'] if 'r' in p else [])
                        l_paths=['held'] if lheld or not require_wonder_tag else (['deck'] if 'l' in [cards[i] for i in deck-set(extras)-{natural}] else [])+(['prize'] if 'l' in p else [])
                        for rp,lp in product(r_paths,l_paths):
                            regular=int(rp=='deck')+int(lp=='deck')
                            recovered=int(rp=='prize')+int(lp=='prize')
                            if regular>observed.count('t')+observed.count('q') or recovered>observed.count('h'):
                                continue
                            if payment=='energy':
                                enough=observed.count('e')>=regular
                            else:
                                effective_hand=model.opening_size+1+bonus-1
                                enough=effective_hand-int(rheld)-int(lheld and require_wonder_tag)-regular-recovered>=regular
                            if enough:
                                ok=True
                                break
                    success+=ok
                    total+=1
    return Fraction(success,total)


def test_small()->None:
    models=(
        ShadowRiderDualEntry(10,3,1,1,2,2,1,1,1,1,1),
        ShadowRiderDualEntry(11,3,2,2,2,2,2,0,1,1,1),
    )
    for model in models:
        for bonus in (0,1):
            for policy,wonder,roles in product(('energy','mechanical'),(False,True),(False,True)):
                got=model.probability(bonus,payment=policy,require_wonder_tag=wonder,role_aware=roles)
                brute=physical(model,bonus,payment=policy,require_wonder_tag=wonder,role_aware=roles)
                assert got==brute,(model,bonus,policy,wonder,roles,got,brute)


def test_published_counts()->None:
    from results.competitive_deck_baselines.shadow_rider_reproduce import (
        POKEMON, TRAINERS, ENERGY,
    )
    model = ShadowRiderDualEntry()
    assert sum(POKEMON.values()) + sum(TRAINERS.values()) + sum(ENERGY.values()) == 60
    assert POKEMON['Radiant Eternatus'] == 1
    assert POKEMON['Tapu Lele-GX'] == model.lele
    assert POKEMON['Shadow Rider Calyrex VMAX'] == model.vmax
    assert sum(POKEMON.values()) - model.vmax - 1 - model.lele == model.other_basics
    assert TRAINERS['Mysterious Treasure'] == model.treasure
    assert TRAINERS['Quick Ball'] == model.quick_ball
    assert TRAINERS['Hisuian Heavy Ball'] == model.heavy_ball
    assert ENERGY['Psychic Energy'] == model.energy
    assert sum(model.capacities) == 60


def test_card_text()->None:
    root=Path(__file__).resolve().parents[2]
    names={
        'swsh12pt5':{'swsh12pt5-105':('Radiant Eternatus','Climactic Gate')},
        'sm2':{'sm2-60':('Tapu Lele-GX','Wonder Tag')},
        'sm6':{'sm6-113':('Mysterious Treasure',None)},
        'swsh1':{'swsh1-179':('Quick Ball',None)},
        'swsh10':{'swsh10-146':('Hisuian Heavy Ball',None)},
        'swsh6':{'swsh6-75':('Shadow Rider Calyrex VMAX','Underworld Door')},
    }
    for set_id,prints in names.items():
        cards=json.loads((root/'resources'/'cards'/'en'/f'{set_id}.json').read_text('utf-8'))
        for pid,(name,ability) in prints.items():
            card=next(c for c in cards if c['id']==pid)
            assert card['name']==name and card['legalities']['expanded']=='Legal',(pid,card)
            if ability:
                assert any(a['name']==ability for a in card.get('abilities',[])),(pid,card)
    required_rules = {
        'sm6-113': ('Discard a card from your hand.',
                     'Psychic or Dragon Pokémon'),
        'swsh1-179': ('discard another card from your hand',
                      'Basic Pokémon'),
        'swsh10-146': ('face-down Prize cards', 'Basic Pokémon'),
    }
    for identifier, fragments in required_rules.items():
        cards=json.loads((root/'resources'/'cards'/'en'/
                          f"{identifier.rsplit('-',1)[0]}.json").read_text('utf-8'))
        card=next(x for x in cards if x['id']==identifier)
        assert all(any(frag in text for text in card['rules'])
                   for frag in fragments),(identifier,card['rules'])
    print('PASS: published print identities and action text')


def benchmark()->None:
    model=ShadowRiderDualEntry()
    expected={
        ('mechanical',False,True):'0.5065943762478146',
        ('energy',False,True):'0.4270345819604528',
    }
    print('payment | role blind dual | role-aware dual | role-aware Radiant')
    for policy in ('energy','mechanical'):
        naive=model.probability(0,payment=policy,role_aware=False)
        actual=model.probability(0,payment=policy)
        radiant=model.probability(0,payment=policy,require_wonder_tag=False)
        if (policy,False,True) in expected:
            assert abs(float(radiant)-float(expected[(policy,False,True)]))<1e-13
        assert actual<=radiant
        assert actual<=naive
        print(policy,float(naive),float(actual),float(radiant))
    # Keep total Basic starters unchanged while swapping individual
    # Lele entries for unrelated starting Basics.
    print('Lele | other Basic | energy dual | mechanical dual')
    previous=Fraction()
    for lele in range(1,5):
        adjusted=ShadowRiderDualEntry(lele=lele,other_basics=13-lele)
        energy=adjusted.probability(0,payment='energy')
        mechanical=adjusted.probability(0,payment='mechanical')
        assert energy > previous
        previous=energy
        assert abs(float(adjusted.probability(0,payment='mechanical',require_wonder_tag=False)) - 0.5065943762478146) < 1e-13
        print(lele, 13-lele, f'{float(energy):.9%}', f'{float(mechanical):.9%}')


if __name__=='__main__':
    test_small()
    test_published_counts()
    test_card_text()
    benchmark()
    print('PASS: physical dual-entry conditional exactness and baseline reduction')
