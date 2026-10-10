"""Independent physical opening and prior-solver checks for multi-source gust race."""
from collections import Counter
from fractions import Fraction
from itertools import combinations,combinations_with_replacement
from tools.multisource_opponent_gust_race import (
    opening_zone_distribution,initial_win_probability,win_probability,
)
from tools.gust_copy_opening_access import at_least_one
from tools.two_sided_bidirectional_gust import can_force_win
from tools.stochastic_opponent_gust_arrival import win_probability as prior_stochastic
from tools.opposing_gust_opening_access import opening_mixture_win_probability


def physical_zones(basics,bosses,counters,prizes,total=10,hand_size=3):
    cards=tuple(range(total))
    boss=set(range(basics,basics+bosses))
    counter=set(range(basics+bosses,basics+bosses+counters))
    occurrences=Counter()
    for hand in combinations(cards,hand_size):
        hs=set(hand)
        if not hs.intersection(range(basics)):continue
        rest=[x for x in cards if x not in hs]
        for prize in combinations(rest,prizes):
            ps=set(prize)
            db=boss-hs-ps
            dc=counter-hs-ps
            key=(len(boss&hs),len(counter&hs),len(db),len(dc))
            occurrences[key]+=1
    denom=sum(occurrences.values())
    return {key:Fraction(value,denom) for key,value in occurrences.items()}


def boards():
    for size in range(2,5):
        for values in combinations_with_replacement((1,2,3),size):
            if sum(values)<6:continue
            for active in sorted(set(values)):
                remain=list(values)
                remain.remove(active)
                yield active,tuple(remain)


def verify():
    toy=0
    for basic in (2,3):
        for boss in (0,1,2):
            for counter in (0,1,2):
                for prize in (1,2):
                    expected=physical_zones(basic,boss,counter,prize)
                    observed=opening_zone_distribution(basic,boss,counter,10,3,prize)
                    assert observed==expected,(basic,boss,counter,prize)
                    toy+=1
    assert toy==36

    cases=0
    for oa,ob in ((1,(1,)),(1,(1,1,3))):
        for ea,eb in boards():
            for ep in (2,3):
                for hb in (0,1,2):
                    for hc in (0,1,2):
                        got=win_probability(oa,ob,ea,eb,1,1,6,ep,
                                            hb,hc,0,0,0)
                        ref=can_force_win(oa,ob,ea,eb,1,1,hb,hc,6,ep,True)
                        assert got==int(ref)
                        cases+=1
    assert cases==1404

    for source in ('boss','counter'):
        for ea,eb in ((3,(3,)),(2,(2,2)),(1,(2,3))):
            for ep in (2,3):
                got=win_probability(1,(1,1,3),ea,eb,1,1,6,ep,
                                    0,0,int(source=='boss'),int(source=='counter'),7)
                old=prior_stochastic(1,(1,1,3),ea,eb,1,1,6,ep,source,7)
                assert got==old
                got_open=initial_win_probability(1,(1,1,3),ea,eb,1,1,ep,4,
                                                 int(source=='boss'),int(source=='counter'))
                old_open=opening_mixture_win_probability(1,(1,1,3),ea,eb,1,1,
                                                          ep,source,4)
                assert got_open==old_open

    witnesses=0
    for basic in (4,8,12,16,20,24):
        for boss in range(5):
            counter=4-boss
            a=initial_win_probability(1,(1,2),3,(3,),0,2,2,basic,boss,counter)
            b=initial_win_probability(1,(1,1,3),2,(2,2),1,1,3,basic,boss,counter)
            assert a==1-at_least_one(basic,boss,1)
            assert b==1-at_least_one(basic,boss+counter,2)
            witnesses+=2
    assert witnesses==60
    print(f'PASS: {toy} physical zone distributions, {cases} held-source '
          f'deterministic parity checks, 24 one-source regressions, '
          f'{witnesses} physical four-copy tactical witness formulas')


if __name__=='__main__':
    verify()
