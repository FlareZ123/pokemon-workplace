"""Exact stochastic Boss draws with physically paid Retreat and oracle counterexample."""
from collections import Counter
from dataclasses import replace
from fractions import Fraction
from functools import lru_cache
from itertools import combinations, product
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from tools.typed_retreat_gust import Target, minimum_attacks, retreat_payment_remainders
from tools.two_sided_typed_retreat_draw import attacker_draw
from tools.two_sided_stochastic_escape import attacker_draw as no_retreat_draw


@lru_cache(None)
def fully_known_attacker(active, bench, held, sequence, prizes_needed=6):
    """Both players see the complete ordered future draw sequence in this oracle."""
    held += sequence[0] == 'G'
    tail = sequence[1:]
    actions = [(active, bench, held)]
    if held:
        for i, selected in enumerate(bench):
            actions.append((selected, tuple(sorted((active,) + bench[:i] + bench[i+1:])), held-1))
    outcomes=[]
    for target, rest, hand in actions:
        if target.hits==1:
            if target.prize>=prizes_needed or not rest:
                outcomes.append(1)
            else:
                outcomes.append(1 + max(fully_known_defender(
                    p,rest[:i]+rest[i+1:],hand,tail,prizes_needed-target.prize
                ) for i,p in enumerate(rest)))
        else:
            outcomes.append(1+fully_known_defender(replace(target,hits=target.hits-1),
                                                    rest,hand,tail,prizes_needed))
    return min(outcomes)


@lru_cache(None)
def fully_known_defender(active, bench, hand, sequence, prizes_needed):
    options=[fully_known_attacker(active,bench,hand,sequence,prizes_needed)]
    if not active.retreat_blocked:
        # The project's physical Retreat-payment kernel retains distinct legal remainders.
        for remainder in retreat_payment_remainders(active.energy_cards,active.retreat_cost):
            outgoing=replace(active,energy_cards=remainder)
            for i,promoted in enumerate(bench):
                newbench=tuple(sorted((outgoing,) + bench[:i] + bench[i+1:]))
                options.append(fully_known_attacker(promoted,newbench,hand,sequence,prizes_needed))
    return max(options)


def verify_sources():
    expected=[('bw11','bw11-113','Double Colorless Energy','ColorlessColorless'),
              ('sv1','sv1-194','Switch','Switch your Active Pokémon')]
    for setid,cardid,name,fragment in expected:
        cards=json.loads((ROOT/'resources'/'cards'/'en'/f'{setid}.json').read_text(encoding='utf8'))
        card=next(c for c in cards if c['id']==cardid)
        assert card['name']==name and any(fragment in rule for rule in card['rules'])
    assert retreat_payment_remainders((2,),1)==((),)
    assert retreat_payment_remainders((1,1),1)==((1,),)
    print('Bundled card texts and whole-card Retreat payment properties: passed')


def state_results():
    dce=Target(3,3,1,(2,))
    basics=Target(3,3,1,(1,1))
    for target,expected in ((dce,Fraction(493,66)),(basics,Fraction(169,22))):
        assert attacker_draw(target,(target,target),0,2,10,0,0,12,6,False)==expected
        assert attacker_draw(target,(target,target),0,2,10,0,1,11,6,False)==expected
        assert attacker_draw(target,(target,target),0,0,12,0,0,12,6,False)==8
    assert attacker_draw(dce,(dce,dce),0,2,10,0,1,11,6,True)==Fraction(749,99)
    assert attacker_draw(basics,(basics,basics),0,2,10,0,1,11,6,True)==Fraction(169,22)
    assert Fraction(169,22)-Fraction(493,66)==Fraction(7,33)
    print('Retreat granularity: DCE=493/66, two Basic Energy cards=169/22, gap=7/33 attacks')
    print('Item-allowed one-Switch: DCE=749/99, two Basics=169/22')


def deterministic_bridge():
    # Fully held resources make deck draws inert. Compare an independent, older typed model.
    n=0
    for num in (2,3):
        for prizes in product((1,3),repeat=num):
            if sum(prizes)<6:
                continue
            for hits in product((1,2,3),repeat=num):
                for energy in ((),(1,),(2,),(1,1)):
                    for cost in (1,2):
                        cards=tuple(Target(prizes[i],hits[i],cost,energy) for i in range(num))
                        active,bench=cards[0],tuple(sorted(cards[1:]))
                        for item in (False,True):
                            for bosses in (0,1,2):
                                for switches in (0,1):
                                    actual=attacker_draw(active,bench,bosses,0,12,switches,0,12,6,item)
                                    reference=minimum_attacks(active,bench,bosses,switches,item)
                                    assert actual==reference,(cards,item,bosses,switches,actual,reference)
                                    n+=1
    assert n==11232
    # With no payable Retreat, the source-free two-deck model must agree.
    blank=Target(3,2,1,())
    for item in (False,True):
        for bosses in range(3):
            for switches in range(3):
                actual=attacker_draw(blank,(blank,blank),0,bosses,12-bosses,
                                     0,switches,12-switches,6,item)
                reference=no_retreat_draw((3,2),((3,2),(3,2)),0,bosses,12-bosses,
                                          0,switches,12-switches,6,item)
                assert actual==reference
    print(f'Deterministic-limit cross-model regression: {n} cases; zero-retreat limit: 18 cases')


def clairvoyant_draw_counterexample():
    seen={}
    for cards in ((2,),(1,1)):
        target=Target(3,3,1,cards)
        outcomes=Counter()
        for boss_positions in combinations(range(12),2):
            future=tuple('G' if ix in boss_positions else 'F' for ix in range(12))
            attacks=fully_known_attacker(target,(target,target),0,future)
            outcomes[attacks]+=1
        mean=sum(Fraction(k*v,66) for k,v in outcomes.items())
        seen[cards]=(mean,outcomes)
    assert seen[(2,)][0]==Fraction(83,11)
    assert seen[(2,)][1]=={8:45,7:12,6:9}
    assert seen[(1,1)][0]==Fraction(169,22)
    assert seen[(1,1)][1]=={8:45,7:21}
    assert seen[(2,)][0]-Fraction(493,66)==Fraction(5,66)
    print('Clairvoyant BOTH-player known-order model: DCE=83/11 vs hidden-order=493/66')
    print('The physical oracle is NOT equivalent to a nonclairvoyant chance/minimax solver.')


if __name__=='__main__':
    verify_sources()
    state_results()
    deterministic_bridge()
    clairvoyant_draw_counterexample()
    print('All stochastic Retreat-payment bridge regressions passed.')
