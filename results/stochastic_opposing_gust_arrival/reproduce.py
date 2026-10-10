"""Regression checks for exact opposing-gust arrival probabilities."""
from fractions import Fraction
from itertools import combinations_with_replacement
from tools.stochastic_opponent_gust_arrival import win_probability
from tools.two_sided_bidirectional_gust import can_force_win


def all_boards(max_count=4):
    for count in range(2,max_count+1):
        for vals in combinations_with_replacement((1,2,3),count):
            if sum(vals)<6:
                continue
            for active in sorted(set(vals)):
                bench=list(vals)
                bench.remove(active)
                yield active,tuple(bench)


def verify():
    boards=list(all_boards())
    assert len(boards)==39
    # When the sole opposing source is certain to be drawn on its first reply,
    # arrival exactly matches the earlier initially-held adversarial engine.
    checks=0
    for oa,ob in ((1,(1,)),(1,(1,2)),(1,(1,1,3)),(2,(2,2))):
        for ea,eb in boards:
            for ep in (2,3,4,5):
                for b,c in ((0,2),(1,1),(2,0)):
                    for source in ('boss','counter','none'):
                        observed=win_probability(oa,ob,ea,eb,b,c,6,ep,source,1)
                        expected=can_force_win(oa,ob,ea,eb,b,c,
                                               int(source=='boss'),int(source=='counter'),
                                               6,ep,True)
                        assert observed == int(expected)
                        checks+=1
    assert checks==5616

    # Two physically interpretable endpoint witnesses with independent
    # closed-form draw-order checks: source is uniformly placed at 1..N.
    for n in range(1,17):
        assert win_probability(1,(1,),3,(3,),0,2,6,2,'boss',n)==1
        assert win_probability(1,(1,2),3,(3,),0,2,6,2,'boss',n)==Fraction(n-1,n)
        assert win_probability(1,(1,2),3,(3,),0,2,6,2,'counter',n)==1
        for source in ('boss','counter'):
            assert win_probability(1,(1,1),2,(2,2),1,1,6,3,source,n)==1
            assert win_probability(1,(1,1,3),2,(2,2),1,1,6,3,source,n)==Fraction(max(0,n-2),n)

    # Bounded 39-board cross-section, exactly same structural board support
    # for every source and unseen-draw horizon.
    expected_counts={
        'boss':(52,26),
        'counter':(9,69),
    }
    evaluated=0
    for source in ('boss','counter'):
        for n in (1,2,4,8):
            loss=gain=equal=partial=0
            for ea,eb in boards:
                for ep in (2,3):
                    old=win_probability(1,(1,1),ea,eb,1,1,6,ep,source,n)
                    new=win_probability(1,(1,1,3),ea,eb,1,1,6,ep,source,n)
                    if new<old:
                        loss+=1
                        partial+=0<new<old
                    elif new>old:
                        gain+=1
                    else:
                        equal+=1
                    evaluated+=1
            assert (loss,equal)==expected_counts[source], (source,n,loss,equal)
            assert gain==0
            assert partial=={'boss':{1:0,2:36,4:52,8:52},
                             'counter':{1:0,2:0,4:9,8:9}}[source][n]

    # A drawn restricted source never exceeds an equally timed Boss in power.
    # This follows by action-set inclusion and is checked on the cross-section.
    for ea,eb in boards:
        for ep in (2,3):
            for n in (1,2,4,8):
                for bench in ((1,1),(1,1,3)):
                    boss=win_probability(1,bench,ea,eb,1,1,6,ep,'boss',n)
                    counter=win_probability(1,bench,ea,eb,1,1,6,ep,'counter',n)
                    assert boss<=counter
    print(f'PASS: {checks} deterministic-engine parity checks, '
          f'{evaluated} fixed-support stochastic Bench comparisons, '
          '80 analytic witness checks and source inclusion checks')


if __name__=='__main__':
    verify()
