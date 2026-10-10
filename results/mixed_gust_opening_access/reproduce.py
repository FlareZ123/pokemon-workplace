"""Physically enumerated Boss/Counter joint opening access verifier."""
from collections import Counter
from fractions import Fraction
from itertools import combinations
from tools.mixed_gust_opening_access import access_profile,joint_distribution
from tools.gust_copy_opening_access import at_least_one


def physical_distribution(basics,bosses,counters,prizes,replies,total=10,hand_size=3):
    universe=tuple(range(total))
    boss_ids=set(range(basics,basics+bosses))
    counter_ids=set(range(basics+bosses,basics+bosses+counters))
    counts=Counter()
    for hand in combinations(universe,hand_size):
        hs=set(hand)
        if not any(i in hs for i in range(basics)):
            continue
        remaining=[i for i in universe if i not in hs]
        for prize in combinations(remaining,prizes):
            pr=set(prize)
            drawable=[i for i in remaining if i not in pr]
            for draw in combinations(drawable,replies):
                visible=hs|set(draw)
                counts[(len(visible&boss_ids),len(visible&counter_ids))]+=1
    denom=sum(counts.values())
    return {key:Fraction(x,denom) for key,x in counts.items() if x}


def verify():
    toy=0
    for basics in (2,3):
        for bosses in (0,1,2):
            for counters in (0,1,2):
                if bosses+counters==0:
                    continue
                for prizes in (1,2):
                    for k in (1,2):
                        physical=physical_distribution(basics,bosses,counters,prizes,k)
                        exact=joint_distribution(basics,bosses,counters,k,10,3,prizes)
                        assert physical==exact,(basics,bosses,counters,prizes,k)
                        profile=access_profile(basics,bosses,counters,k,10,3,prizes)
                        assert profile['any']==sum(v for (b,c),v in exact.items() if b+c>0)
                        assert profile['boss']==sum(v for (b,c),v in exact.items() if b>0)
                        assert profile['both']==sum(v for (b,c),v in exact.items() if b>0 and c>0)
                        toy+=1
    assert toy==64
    normal=0
    for basics in (4,8,12,16,20):
        for k in (1,2):
            profiles=[]
            for bosses in range(5):
                counters=4-bosses
                p=access_profile(basics,bosses,counters,k)
                d=joint_distribution(basics,bosses,counters,k)
                assert p['any']==sum(v for (b,c),v in d.items() if b+c>=1)
                assert p['both']==sum(v for (b,c),v in d.items() if b>=1 and c>=1)
                assert p['counter_gate_closed']==p['boss']
                assert p['counter_gate_open']==p['any']
                assert p['any']==at_least_one(basics,4,k)
                profiles.append(p)
                normal+=1
            assert profiles[2]['both']>profiles[1]['both']==profiles[3]['both']
            assert profiles[0]['both']==profiles[4]['both']==0
            assert all(profiles[i]['boss']<profiles[i+1]['boss'] for i in range(4))
    assert normal==50
    print(f'PASS: {toy} physical joint source oracles and '
          f'{normal} full 60-card mixed-source distributions')


if __name__=='__main__':
    verify()
