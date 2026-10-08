"""Independent deadline oracle and structural census for mixed gust timing.

Run: python results/mixed_gust_prize_minimax/reproduce.py
"""
from collections import Counter
from functools import lru_cache

from tools.counter_catcher_prize_timing import counter_catcher_attacks
from tools.gust_prize_minimax import enumerate_boards, minimum_attacks
from tools.mixed_gust_prize_minimax import forced_first_gust, mixed_gust_attacks


@lru_cache(None)
def can_win_by(active, bench, bosses, catchers, own, opponent, turns):
    """Boolean existential attack / universal promotion game at a fixed deadline."""
    if own <= 0:
        return True
    if turns == 0:
        return False
    if not bench:
        return True

    actions = [(active, bench, bosses, catchers)]
    for i, prize in enumerate(bench):
        rest = tuple(sorted((active,) + bench[:i] + bench[i + 1 :]))
        if bosses:
            actions.append((prize, rest, bosses - 1, catchers))
        if catchers and own > opponent:
            actions.append((prize, rest, bosses, catchers - 1))

    for prize, rest, next_bosses, next_catchers in actions:
        if prize >= own or not rest:
            return True
        if all(
            can_win_by(p, rest[:i] + rest[i + 1 :], next_bosses,
                       next_catchers, own - prize, opponent, turns - 1)
            for i, p in enumerate(rest)
        ):
            return True
    return False


def run():
    boards = tuple((a, b) for a, b, _ in enumerate_boards())
    assert len(boards) == 146
    expected_sums = {
        1: (392, 392, 392),
        2: (398, 392, 392),
        3: (480, 392, 392),
        4: (516, 398, 392),
        5: (516, 398, 392),
    }
    expected_priority = {1: 0, 2: 0, 3: 73, 4: 94, 5: 100}
    checked = 0
    for opponent in range(1, 6):
        sums = [0, 0, 0]
        first_counter_strictly_better = 0
        rescue = 0
        loss = 0
        for active, bench in boards:
            values = (
                mixed_gust_attacks(active, bench, 0, 2, 6, opponent),
                mixed_gust_attacks(active, bench, 1, 1, 6, opponent),
                mixed_gust_attacks(active, bench, 2, 0, 6, opponent),
            )
            assert values[0] >= values[1] >= values[2]
            assert values[0] == counter_catcher_attacks(
                active, bench, 2, 6, opponent
            )
            assert values[2] == minimum_attacks(active, bench, 2, 6)
            for i, value in enumerate(values):
                assert can_win_by(active, bench, ((0, 2), (1, 1), (2, 0))[i][0],
                                  ((0, 2), (1, 1), (2, 0))[i][1],
                                  6, opponent, value)
                assert not can_win_by(active, bench, ((0, 2), (1, 1), (2, 0))[i][0],
                                      ((0, 2), (1, 1), (2, 0))[i][1],
                                      6, opponent, value - 1)
                sums[i] += value
                checked += 1
            counter_first = forced_first_gust(
                active, bench, 1, 1, 6, opponent, "C"
            )
            boss_first = forced_first_gust(
                active, bench, 1, 1, 6, opponent, "B"
            )
            assert counter_first <= boss_first
            first_counter_strictly_better += counter_first < boss_first
            rescue += values[0] > values[1]
            loss += values[1] > values[2]

        assert tuple(sums) == expected_sums[opponent]
        assert first_counter_strictly_better == expected_priority[opponent]
        print(f"opponent={opponent} sums={tuple(sums)} "
              f"mixed_better_than_two_catchers={rescue}/146 "
              f"mixed_worse_than_two_bosses={loss}/146 "
              f"force_counter_first_strict={first_counter_strictly_better}/146")

    assert checked == 2190
    assert tuple(
        mixed_gust_attacks(3, (1, 3), b, c, 6, 3)
        for b, c in ((0, 2), (1, 1), (2, 0))
    ) == (3, 2, 2)
    assert tuple(
        mixed_gust_attacks(2, (1, 2, 2), b, c, 6, 4)
        for b, c in ((0, 2), (1, 1), (2, 0))
    ) == (4, 4, 3)
    assert forced_first_gust(2, (1, 2, 2), 1, 1, 6, 3, "C") == 4
    assert mixed_gust_attacks(2, (1, 2, 2), 1, 1, 6, 3) == 3
    print(f"PASS: {checked} independent horizon checks; "
          "all source-priority, baseline, and witness assertions")


if __name__ == "__main__":
    run()
