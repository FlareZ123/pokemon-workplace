"""Exact joint Boss/Counter source availability with Basic-valid openings."""
from fractions import Fraction
from tools.gust_copy_opening_access import choose, at_least_one


def joint_distribution(basics,bosses,counters,replies,total=60,
                       hand_size=7,prize_count=6):
    """Joint PMF for Boss and Counter copies in hand plus k normal draws."""
    if not (1<=basics<=total and 0<=bosses and 0<=counters and
            basics+bosses+counters<=total):
        raise ValueError('invalid source composition')
    if not (0<hand_size<total and 0<=prize_count<=total-hand_size and
            0<=replies<=total-hand_size-prize_count):
        raise ValueError('invalid hand, prizes or draws')
    accepted=choose(total,hand_size)-choose(total-basics,hand_size)
    denom=accepted*choose(total-hand_size,replies)
    filler=total-basics-bosses-counters
    mass={}
    for hboss in range(min(bosses,hand_size)+1):
        for hcounter in range(min(counters,hand_size-hboss)+1):
            for hbasic in range(1,min(basics,hand_size-hboss-hcounter)+1):
                hands=(choose(bosses,hboss)*choose(counters,hcounter)*
                       choose(basics,hbasic)*
                       choose(filler,hand_size-hboss-hcounter-hbasic))
                if not hands:continue
                rb=bosses-hboss
                rc=counters-hcounter
                for db in range(min(rb,replies)+1):
                    for dc in range(min(rc,replies-db)+1):
                        draws=(choose(rb,db)*choose(rc,dc)*
                               choose(total-hand_size-rb-rc,replies-db-dc))
                        key=(hboss+db,hcounter+dc)
                        mass[key]=mass.get(key,0)+hands*draws
    result={key:Fraction(v,denom) for key,v in mass.items()}
    assert sum(result.values())==1
    return result


def access_profile(basics,bosses,counters,replies,total=60,hand_size=7,
                   prize_count=6):
    """Any gust, Boss legal when Counter closed, and joint-type access."""
    args=(total,hand_size,prize_count)
    b=at_least_one(basics,bosses,replies,*args)
    c=at_least_one(basics,counters,replies,*args)
    either=at_least_one(basics,bosses+counters,replies,*args)
    return {'any':either,'boss':b,'counter':c,'both':b+c-either,
            'counter_gate_closed':b,'counter_gate_open':either}
