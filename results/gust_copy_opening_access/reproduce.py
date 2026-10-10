"""Independent physical labeled-card enumerator for multi-source access PMFs."""
from fractions import Fraction
from itertools import combinations
from tools.gust_copy_opening_access import at_least_one, source_count_distribution
from tools.opposing_gust_opening_access import chance_accessible_by_reply


def physical_pmf(total,basics,sources,hand_size,prize_count,replies):
    cards=tuple(range(total))
    source_ids=set(range(basics,basics+sources))
    counts=[0]*(sources+1)
    for hand in combinations(cards,hand_size):
        hs=set(hand)
        if not hs.intersection(range(basics)):
            continue
        remaining=[c for c in cards if c not in hs]
        for prizes in combinations(remaining,prize_count):
            ps=set(prizes)
            drawable=[c for c in remaining if c not in ps]
            for drawn in combinations(drawable,replies):
                present=len(source_ids.intersection(hs.union(drawn)))
                counts[present]+=1
    total_outcomes=sum(counts)
    return tuple(Fraction(v,total_outcomes) for v in counts)


def verify():
    physical_cases=0
    for basics in (2,3,4):
        for sources in (1,2,3):
            for prizes in (1,2,3):
                for k in (1,2):
                    pmf=source_count_distribution(basics,sources,k,10,3,prizes)
                    assert pmf==physical_pmf(10,basics,sources,3,prizes,k)
                    assert 1-pmf[0]==at_least_one(basics,sources,k,10,3,prizes)
                    physical_cases+=1
    assert physical_cases==54
    normal_cases=0
    for basics in (4,8,12,16,20):
        for k in (1,2):
            previous=Fraction(0)
            increments=[]
            for copies in (1,2,3,4):
                pmf=source_count_distribution(basics,copies,k)
                p=at_least_one(basics,copies,k)
                assert p==1-pmf[0]
                assert sum(j*x for j,x in enumerate(pmf))==copies*chance_accessible_by_reply(basics,k)
                for prizes in (0,3,6,10):
                    assert pmf==source_count_distribution(basics,copies,k,prize_count=prizes)
                increments.append(p-previous)
                previous=p
                normal_cases+=1
            assert all(increments[i]>increments[i+1] for i in range(3))
    assert normal_cases==40
    print(f'PASS: {physical_cases} exhaustive toy multi-copy physical oracles, '
          f'{normal_cases} exact 60-card PMFs, Prize invariance and diminishing gains')


if __name__=='__main__':
    verify()
