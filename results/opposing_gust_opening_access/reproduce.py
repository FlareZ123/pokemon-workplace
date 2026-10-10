"""Physical labeled-card oracle for source location after Basic-valid openings."""
from fractions import Fraction
from itertools import combinations
from tools.opposing_gust_opening_access import (
    opening_access, chance_accessible_by_reply, opening_mixture_win_probability,
)


def physical_oracle(total,basics,hand_size,prize_count,replies):
    """Enumerate all accepted hand, Prize, and next-k-draw subsets."""
    source=basics
    deck=range(total)
    checked=held=prized=remaining=available=0
    for hand in combinations(deck,hand_size):
        hs=set(hand)
        if not any(i in hs for i in range(basics)):
            continue
        leftover=[i for i in deck if i not in hs]
        for prizes in combinations(leftover,prize_count):
            ps=set(prizes)
            cards=[i for i in leftover if i not in ps]
            for drawn in combinations(cards,replies):
                checked+=1
                held+=source in hs
                prized+=source in ps
                remaining+=source not in hs and source not in ps
                available+=source in hs or source in drawn
    return tuple(Fraction(k,checked) for k in (held,prized,remaining,available))


def verify():
    toy_tests=0
    for basics in (2,3,4):
        for prizes in (1,2,3):
            for k in (1,2):
                expected=opening_access(total=10,basics=basics,
                                        hand_size=3,prize_count=prizes)
                got=physical_oracle(10,basics,3,prizes,k)
                assert got[:3]==expected[1:],(basics,prizes,k,got,expected)
                assert got[3]==chance_accessible_by_reply(
                    basics,k,total=10,hand_size=3,prize_count=prizes)
                toy_tests+=1
    assert toy_tests==18
    for basics in (4,8,12,16,20,24):
        valid,held,prized,deck=opening_access(basics=basics)
        assert valid>0 and held+prized+deck==1
        for k in (1,2):
            access=chance_accessible_by_reply(basics,k)
            # Conditional layout: either source was held already, or it is
            # one of k distinct natural draws among the 53 post-hand cards.
            assert access==held+(1-held)*Fraction(k,53)
        one=opening_mixture_win_probability(
            1,(1,2),3,(3,),0,2,2,'boss',basics)
        two_boss=opening_mixture_win_probability(
            1,(1,1,3),2,(2,2),1,1,3,'boss',basics)
        two_counter=opening_mixture_win_probability(
            1,(1,1,3),2,(2,2),1,1,3,'counter',basics)
        assert one==1-chance_accessible_by_reply(basics,1)
        assert two_boss==two_counter==1-chance_accessible_by_reply(basics,2)
    # Lower-Basic valid-opener conditioning suppresses non-Basic source
    # access relative to naive unconditional 8/60 and 9/60.
    for basics in (4,8,12,16,20,24):
        assert chance_accessible_by_reply(basics,1)<Fraction(8,60)
        assert chance_accessible_by_reply(basics,2)<Fraction(9,60)
    print('PASS: 18 physical toy oracle populations, six exact 60-card '
          'opening/Prize mixtures, 18 stochastic witness integrations')


if __name__=='__main__':
    verify()
