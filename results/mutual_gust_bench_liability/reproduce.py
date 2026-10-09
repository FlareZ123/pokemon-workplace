"""Two-sided gust and bench-add liability: independent deadline checks and census."""
from functools import lru_cache
from tools.gust_prize_minimax import enumerate_boards
from tools.two_sided_gust_race import can_force_win as no_opposing_gust
from tools.two_sided_mutual_gust import can_force_win


@lru_cache(None)
def victory_by(own_active, own_bench, enemy_active, enemy_bench,
               own_bosses, own_catchers, enemy_bosses,
               own_prizes, enemy_prizes, can_pass, attacks_left):
    if own_prizes <= 0:
        return True
    if enemy_prizes <= 0 or attacks_left == 0:
        return False

    our_targets = [(enemy_active, enemy_bench, own_bosses, own_catchers)]
    for i, target in enumerate(enemy_bench):
        rest = tuple(sorted(enemy_bench[:i] + (enemy_active,) + enemy_bench[i+1:]))
        if own_bosses:
            our_targets.append((target, rest, own_bosses - 1, own_catchers))
        if own_catchers and own_prizes > enemy_prizes:
            our_targets.append((target, rest, own_bosses, own_catchers - 1))

    for reward, remaining, b, c in our_targets:
        if reward >= own_prizes or not remaining:
            return True
        opponent_wins_some_branch = False
        for j, promoted in enumerate(remaining):
            bench_now = remaining[:j] + remaining[j+1:]
            enemy_targets = [(own_active, own_bench, enemy_bosses)]
            if enemy_bosses:
                for k, target in enumerate(own_bench):
                    own_remaining = tuple(sorted(own_bench[:k] + (own_active,) + own_bench[k+1:]))
                    enemy_targets.append((target, own_remaining, enemy_bosses-1))
            if can_pass and not victory_by(own_active, own_bench,
                                           promoted, bench_now, b, c,
                                           enemy_bosses, own_prizes-reward,
                                           enemy_prizes, can_pass, attacks_left-1):
                opponent_wins_some_branch = True
                break
            for conceded, surviving, eb in enemy_targets:
                if conceded >= enemy_prizes or not surviving:
                    opponent_wins_some_branch = True
                    break
                if not any(victory_by(new_active, surviving[:idx] + surviving[idx+1:],
                                      promoted, bench_now, b, c, eb,
                                      own_prizes-reward, enemy_prizes-conceded,
                                      can_pass, attacks_left-1)
                           for idx, new_active in enumerate(surviving)):
                    opponent_wins_some_branch = True
                    break
            if opponent_wins_some_branch:
                break
        if not opponent_wins_some_branch:
            return True
    return False


def verify():
    boards = [(a,b) for a,b,_ in enumerate_boards()]
    inventories = ((0,2),(1,1),(2,0))
    assert len(boards) == 146
    checked = 0
    cross = 0
    for own_active, own_bench in ((1,(1,)), (1,(1,3)), (2,(2,2))):
        for opp_prizes in range(2,7):
            for op_a,op_b in boards:
                for b,c in inventories:
                    for enemy_bosses in (0,1):
                        for pass_ok in (False,True):
                            result=can_force_win(own_active,own_bench,op_a,op_b,
                                                 b,c,enemy_bosses,6,opp_prizes,pass_ok)
                            independently=victory_by(own_active,own_bench,op_a,op_b,
                                                     b,c,enemy_bosses,6,opp_prizes,
                                                     pass_ok,len(op_b)+1)
                            assert result == independently, (own_active,own_bench,op_a,op_b,b,c,enemy_bosses,pass_ok)
                            checked+=1
                            if not enemy_bosses:
                                assert result == no_opposing_gust(own_active,own_bench,
                                                                   op_a,op_b,b,c,6,opp_prizes,pass_ok)
                                cross+=1
    assert checked == 3*5*146*3*2*2
    assert cross == checked//2

    # Bench addition: 2 Active values, 8 Bench layouts, 3 rewards,
    # 5 opponent Prize counts, 146 opponents, 3 inventories.
    bases = ((1,), (2,), (3,), (1,1), (1,2), (1,3), (2,2), (2,3))
    cases = 0
    hurt = [0,0,0]
    benefit = [0,0,0]
    for own_active in (1,2):
        for old_bench in bases:
            for new_reward in (1,2,3):
                newer_bench = tuple(sorted(old_bench + (new_reward,)))
                for opp_prizes in range(2,7):
                    for op_a,op_b in boards:
                        for b,c in inventories:
                            for opposing_bosses in range(3):
                                old = can_force_win(own_active,old_bench,op_a,op_b,b,c,
                                                    opposing_bosses,6,opp_prizes,True)
                                new = can_force_win(own_active,newer_bench,op_a,op_b,b,c,
                                                    opposing_bosses,6,opp_prizes,True)
                                hurt[opposing_bosses] += old and not new
                                benefit[opposing_bosses] += new and not old
                            cases += 1
    assert cases == 105120
    assert hurt == [0, 4914, 6286], hurt
    assert benefit == [15467,10378,7558], benefit
    witness = (1,(1,),3,(3,),0,2,6,2)
    assert can_force_win(*witness[:2], *witness[2:4], *witness[4:6], 0,*witness[6:],True)
    assert can_force_win(1,(1,2),3,(3,),0,2,0,6,2,True)
    assert can_force_win(*witness[:2], *witness[2:4], *witness[4:6], 1,*witness[6:],True)
    assert not can_force_win(1,(1,2),3,(3,),0,2,1,6,2,True)
    print(f'PASS: {checked} independent finite-deadline checks, {cross} prior engine crosschecks, {cases*3} bench-add comparisons')
    for i in range(3):
        print(f'opponent Boss tokens {i}: bench-add reduces wins {hurt[i]}, increases wins {benefit[i]} / {cases}')


if __name__ == '__main__':
    verify()
