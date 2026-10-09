"""Independent bounded deadline oracle and two-sided gust structural census.

Run: python -m results.two_sided_gust_race.reproduce
"""
from functools import lru_cache
from math import isinf
from tools.gust_prize_minimax import enumerate_boards
from tools.opponent_prize_race_gust import attacks_to_win
from tools.stochastic_opponent_prize_gust import robust_win_against_score_choice
from tools.two_sided_gust_race import can_force_win


@lru_cache(maxsize=None)
def win_by_deadline(own_active, own_bench, enemy_active, enemy_bench,
                    bosses, catchers, own_prizes, enemy_prizes,
                    allow_pass, turns):
    """Existential our attack, universal next Active and opposing action."""
    if own_prizes <= 0:
        return True
    if enemy_prizes <= 0 or turns <= 0:
        return False

    options = [(enemy_active, enemy_bench, bosses, catchers)]
    for index, prize in enumerate(enemy_bench):
        after_gust = tuple(sorted(enemy_bench[:index] + enemy_bench[index+1:] + (enemy_active,)))
        if bosses:
            options.append((prize, after_gust, bosses - 1, catchers))
        if catchers and own_prizes > enemy_prizes:
            options.append((prize, after_gust, bosses, catchers - 1))

    for prize, post_attack, b, c in options:
        if prize >= own_prizes or not post_attack:
            return True
        our_remaining = own_prizes - prize
        all_responses_survived = True
        for enemy_index, enemy_promote in enumerate(post_attack):
            left = post_attack[:enemy_index] + post_attack[enemy_index+1:]
            # Opponent may pass, and must fail to force our loss using that choice.
            if allow_pass and not win_by_deadline(
                own_active, own_bench, enemy_promote, left, b, c,
                our_remaining, enemy_prizes, allow_pass, turns - 1,
            ):
                all_responses_survived = False
                break
            # Opponent wins by taking its last Prize or clearing our side.
            if own_active >= enemy_prizes or not own_bench:
                all_responses_survived = False
                break
            if not any(win_by_deadline(
                new_active, own_bench[:i] + own_bench[i+1:],
                enemy_promote, left, b, c, our_remaining,
                enemy_prizes - own_active, allow_pass, turns - 1,
            ) for i, new_active in enumerate(own_bench)):
                all_responses_survived = False
                break
        if all_responses_survived:
            return True
    return False


def verify():
    enemy_boards = [(a, bench) for a, bench, _ in enumerate_boards()]
    assert len(enemy_boards) == 146
    own_boards = ((2, (2, 2)), (1, (1, 2, 2)), (2, (1, 1, 2)),
                  (1, (1, 1, 1, 2)), (1, (2, 2)), (2, (1, 3)),
                  (1, (1, 3)))
    inventories = ((0, 2), (1, 1), (2, 0))
    checked = 0
    census = {}
    crosschecks = 0
    for own_active, own_bench in own_boards:
        for enemy_prizes in range(3, 7):
            force = [0, 0, 0]
            option = [0, 0, 0]
            for enemy_active, enemy_bench in enemy_boards:
                fv = []
                ov = []
                for i, (b, c) in enumerate(inventories):
                    deadline = len(enemy_bench) + 1
                    forced = can_force_win(own_active, own_bench,
                                           enemy_active, enemy_bench,
                                           b, c, 6, enemy_prizes, False)
                    optional = can_force_win(own_active, own_bench,
                                             enemy_active, enemy_bench,
                                             b, c, 6, enemy_prizes, True)
                    assert forced == win_by_deadline(
                        own_active, own_bench, enemy_active, enemy_bench,
                        b, c, 6, enemy_prizes, False, deadline,
                    )
                    assert optional == win_by_deadline(
                        own_active, own_bench, enemy_active, enemy_bench,
                        b, c, 6, enemy_prizes, True, deadline,
                    )
                    assert not optional or forced
                    force[i] += forced
                    option[i] += optional
                    fv.append(forced)
                    ov.append(optional)
                    checked += 2
                    if (own_active, own_bench) == (2, (2, 2)):
                        base = attacks_to_win(enemy_active, enemy_bench,
                                              b, c, 6, enemy_prizes, 0, (2,))
                        assert forced == (not isinf(base))
                        assert optional == robust_win_against_score_choice(
                            enemy_active, enemy_bench, b, c, 6, enemy_prizes,
                        )
                        crosschecks += 2
                assert fv[0] <= fv[1] <= fv[2]
                assert ov[0] <= ov[1] <= ov[2]
            census[(own_active, own_bench, enemy_prizes)] = (tuple(force), tuple(option))
    assert checked == 7 * 4 * 146 * 3 * 2
    assert crosschecks == 4 * 146 * 3 * 2
    assert census[(2, (2, 2), 4)] == ((75, 75, 75), (51, 75, 75))
    assert census[(2, (2, 2), 6)] == ((85, 117, 123), (78, 117, 123))
    assert census[(1, (1, 3), 6)] == ((75, 111, 123), (72, 107, 123))
    assert can_force_win(1, (1, 3), 1, (1, 1, 2, 3), 1, 1, 6, 6, False)
    assert not can_force_win(1, (1, 3), 1, (1, 1, 2, 3), 1, 1, 6, 6, True)
    assert can_force_win(1, (1, 3), 1, (1, 1, 2, 3), 2, 0, 6, 6, True)
    print(f'PASS: {checked} independent finite deadline checks, {crosschecks} older solver comparisons')
    for own in own_boards:
        for enemy_prizes in (4, 6):
            f, o = census[(*own, enemy_prizes)]
            print(f'own={own}, enemyPrizes={enemy_prizes}: forced={f}, passAllowed={o}, denial={tuple(x-y for x,y in zip(f,o))}')


if __name__ == '__main__':
    verify()
