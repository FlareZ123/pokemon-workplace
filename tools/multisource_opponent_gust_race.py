"""Exact opponent multiple Boss/Counter arrival and endgame Prize race."""
from fractions import Fraction
from functools import lru_cache
from math import comb
from tools.gust_copy_opening_access import choose


@lru_cache(None)
def win_probability(oa,ob,ea,eb,own_b,own_c,ours,theirs,
                    hand_b,hand_c,deck_b,deck_c,deck_size):
    """Perfect-public-source-state optimal chance we eventually win."""
    if ours<=0:return Fraction(1)
    if theirs<=0:return Fraction(0)
    actions=[(ea,eb,own_b,own_c)]
    for i,prize in enumerate(eb):
        remaining=tuple(sorted((ea,)+eb[:i]+eb[i+1:]))
        if own_b:actions.append((prize,remaining,own_b-1,own_c))
        if own_c and ours>theirs:actions.append((prize,remaining,own_b,own_c-1))
    best=Fraction(0)
    for gained,remain,b,c in actions:
        if gained>=ours or not remain:return Fraction(1)
        worst=min(_opponent_draw(oa,ob,active,remain[:i]+remain[i+1:],
                                 b,c,ours-gained,theirs,hand_b,hand_c,
                                 deck_b,deck_c,deck_size)
                  for i,active in enumerate(remain))
        best=max(best,worst)
    return best


@lru_cache(None)
def _opponent_draw(oa,ob,ea,eb,b,c,ours,theirs,hb,hc,db,dc,n):
    if n==0:return _opponent_action(oa,ob,ea,eb,b,c,ours,theirs,hb,hc,db,dc,n)
    values=[]
    if db:
        values.append(Fraction(db,n)*_opponent_action(
            oa,ob,ea,eb,b,c,ours,theirs,hb+1,hc,db-1,dc,n-1))
    if dc:
        values.append(Fraction(dc,n)*_opponent_action(
            oa,ob,ea,eb,b,c,ours,theirs,hb,hc+1,db,dc-1,n-1))
    fillers=n-db-dc
    if fillers:
        values.append(Fraction(fillers,n)*_opponent_action(
            oa,ob,ea,eb,b,c,ours,theirs,hb,hc,db,dc,n-1))
    return sum(values,Fraction(0))


@lru_cache(None)
def _opponent_action(oa,ob,ea,eb,b,c,ours,theirs,hb,hc,db,dc,n):
    # Opponent chooses to pass or KO active or gust a bench target.
    outcomes=[win_probability(oa,ob,ea,eb,b,c,ours,theirs,hb,hc,db,dc,n)]
    attacks=[(oa,ob,hb,hc)]
    for i,prize in enumerate(ob):
        remain=tuple(sorted((oa,)+ob[:i]+ob[i+1:]))
        if hb:attacks.append((prize,remain,hb-1,hc))
        if hc and theirs>ours:attacks.append((prize,remain,hb,hc-1))
    for reward,remain,nb,nc in attacks:
        if reward>=theirs or not remain:
            outcomes.append(Fraction(0))
        else:
            outcomes.append(max(
                win_probability(active,remain[:i]+remain[i+1:],ea,eb,b,c,
                                ours,theirs-reward,nb,nc,db,dc,n)
                for i,active in enumerate(remain)))
    return min(outcomes)


def opening_zone_distribution(basics,bosses,counters,total=60,
                              hand_size=7,prize_count=6):
    """Exact accepted-hand/Prize mixture keyed by (HB,HC,DB,DC)."""
    accepted=choose(total,hand_size)-choose(total-basics,hand_size)
    den=accepted*choose(total-hand_size,prize_count)
    other=total-bosses-counters
    result={}
    for hb in range(min(bosses,hand_size)+1):
        for hc in range(min(counters,hand_size-hb)+1):
            n=hand_size-hb-hc
            handways=(choose(bosses,hb)*choose(counters,hc)*
                      (choose(other,n)-choose(other-basics,n)))
            for pb in range(min(bosses-hb,prize_count)+1):
                for pc in range(min(counters-hc,prize_count-pb)+1):
                    deck_b=bosses-hb-pb
                    deck_c=counters-hc-pc
                    non_sources=total-hand_size-(bosses-hb)-(counters-hc)
                    prizeways=(choose(bosses-hb,pb)*choose(counters-hc,pc)*
                               choose(non_sources,prize_count-pb-pc))
                    key=(hb,hc,deck_b,deck_c)
                    result[key]=result.get(key,0)+handways*prizeways
    ans={key:Fraction(value,den) for key,value in result.items() if value}
    assert sum(ans.values())==1
    return ans


def initial_win_probability(oa,ob,ea,eb,own_b,own_c,theirs,
                            basics,bosses,counters,total=60,
                            hand_size=7,prize_count=6):
    """Opening-conditioned game with public zone/draw revelation."""
    states=opening_zone_distribution(basics,bosses,counters,total,hand_size,prize_count)
    n=total-hand_size-prize_count
    return sum((prob*win_probability(oa,ob,ea,eb,own_b,own_c,6,theirs,
                                     hb,hc,db,dc,n)
                for (hb,hc,db,dc),prob in states.items()),Fraction(0))
