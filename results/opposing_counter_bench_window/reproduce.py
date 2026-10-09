"""Validate reciprocal Boss/Counter Prize gates and Bench-addition outcomes."""
from functools import lru_cache
from tools.gust_prize_minimax import enumerate_boards
from tools.two_sided_mutual_gust import can_force_win as prior_boss_only
from tools.two_sided_bidirectional_gust import can_force_win


@lru_cache(None)
def deadline_possible(own_active, own_bench, enemy_active, enemy_bench,
                      b, c, eb, ec, ours, theirs, may_pass, deadline):
    if ours <= 0: return True
    if theirs <= 0 or deadline <= 0: return False
    targets=[(enemy_active,enemy_bench,b,c)]
    for j,t in enumerate(enemy_bench):
        remain=tuple(sorted((enemy_active,)+enemy_bench[:j]+enemy_bench[j+1:]))
        if b: targets.append((t,remain,b-1,c))
        if c and ours>theirs: targets.append((t,remain,b,c-1))

    for reward,surv,nb,nc in targets:
        if reward>=ours or not surv:return True
        all_choices_safe=True
        for j,prom in enumerate(surv):
            rb=surv[:j]+surv[j+1:]
            if may_pass and not deadline_possible(own_active,own_bench,prom,rb,
                                                   nb,nc,eb,ec,ours-reward,theirs,
                                                   may_pass,deadline-1):
                all_choices_safe=False;break
            replies=[(own_active,own_bench,eb,ec)]
            for k,t in enumerate(own_bench):
                remaining=tuple(sorted((own_active,)+own_bench[:k]+own_bench[k+1:]))
                if eb:replies.append((t,remaining,eb-1,ec))
                if ec and theirs>ours-reward:replies.append((t,remaining,eb,ec-1))
            for gift,own_surv,next_eb,next_ec in replies:
                if gift>=theirs or not own_surv:
                    all_choices_safe=False;break
                if not any(deadline_possible(a,own_surv[:x]+own_surv[x+1:],prom,rb,
                                             nb,nc,next_eb,next_ec,ours-reward,
                                             theirs-gift,may_pass,deadline-1)
                           for x,a in enumerate(own_surv)):
                    all_choices_safe=False;break
            if not all_choices_safe:break
        if all_choices_safe:return True
    return False


def verify():
    boards=[(a,b) for a,b,_ in enumerate_boards()]
    inv=((0,2),(1,1),(2,0))
    enemy_src=((0,0),(0,1),(1,0),(1,1),(0,2),(2,0))
    assert len(boards)==146
    oracle_checks=0
    backward_checks=0
    for own_active,own_bench in ((1,(1,)),(1,(1,3)),(2,(2,2))):
        for enemy_remaining in (3,4,6):
            for enemy_active,enemy_bench in boards:
                for b,c in inv:
                    for eb,ec in enemy_src[:4]:
                        for can_pass in (False,True):
                            result=can_force_win(own_active,own_bench,
                                                 enemy_active,enemy_bench,b,c,eb,ec,
                                                 6,enemy_remaining,can_pass)
                            expected=deadline_possible(own_active,own_bench,
                                                       enemy_active,enemy_bench,
                                                       b,c,eb,ec,6,enemy_remaining,
                                                       can_pass,len(enemy_bench)+1)
                            assert result==expected
                            oracle_checks+=1
                            if not ec:
                                assert result==prior_boss_only(own_active,own_bench,
                                                               enemy_active,enemy_bench,
                                                               b,c,eb,6,enemy_remaining,can_pass)
                                backward_checks+=1
    assert oracle_checks==3*3*146*3*4*2
    assert backward_checks==oracle_checks//2
    # Opponent Counter is conditional; opponent Boss is its unconditional upper bound.
    for own_active,own_bench in ((1,(1,3)),(2,(2,2))):
        for opponent_prizes in range(2,7):
            for enemy_active,enemy_bench in boards:
                for b,c in inv:
                    catch=can_force_win(own_active,own_bench,enemy_active,enemy_bench,
                                        b,c,0,1,6,opponent_prizes,True)
                    boss=can_force_win(own_active,own_bench,enemy_active,enemy_bench,
                                       b,c,1,0,6,opponent_prizes,True)
                    assert catch>=boss
    # Quantify nonmonotonic value of adding a Bench body.
    bases=((1,),(2,),(3,),(1,1),(1,2),(1,3),(2,2),(2,3))
    lost=[0]*6;gained=[0]*6;compared=0
    for own_active in (1,2):
        for old_bench in bases:
            for new_prize in (1,2,3):
                new_bench=tuple(sorted(old_bench+(new_prize,)))
                for enemy_prizes in range(2,7):
                    for enemy_active,enemy_bench in boards:
                        for b,c in inv:
                            for i,(eb,ec) in enumerate(enemy_src):
                                old=can_force_win(own_active,old_bench,enemy_active,
                                                  enemy_bench,b,c,eb,ec,6,enemy_prizes,True)
                                new=can_force_win(own_active,new_bench,enemy_active,
                                                  enemy_bench,b,c,eb,ec,6,enemy_prizes,True)
                                lost[i]+=old and not new
                                gained[i]+=new and not old
                            compared+=1
    assert compared==105120
    assert lost==[0,1831,4914,6151,2552,6286]
    assert gained==[15467,12213,10378,7852,10102,7558]
    # Opponent Counter closed on first reply; Boss could KO three-Prize Bench now.
    boss_wins=0;counter_wins=0
    for enemy_active,enemy_bench in boards:
        boss_wins+=can_force_win(1,(1,3),enemy_active,enemy_bench,1,1,1,0,6,3,True)
        counter_wins+=can_force_win(1,(1,3),enemy_active,enemy_bench,1,1,0,1,6,3,True)
    assert (counter_wins,boss_wins)==(96,0)
    # Minimal opposing Counter exposed-Bench counterexample.
    for own_bench,win in (((1,1),True),((1,1,3),False)):
        assert can_force_win(1,own_bench,2,(2,2),1,1,0,1,6,3,True)==win
    print(f'PASS: {oracle_checks} independent deadline checks; {backward_checks} prior solver checks; {compared*6} Bench additions')
    for x,l,g in zip(enemy_src,lost,gained):
        print(f'opponent (Boss,Counter)={x}: harmed {l}, helped {g} / {compared}')
    print(f'opponent3, own A1 Bench(1,3), our mixed: wins vs one opponent Counter {counter_wins}/146; versus one Boss {boss_wins}/146')


if __name__=='__main__':verify()
