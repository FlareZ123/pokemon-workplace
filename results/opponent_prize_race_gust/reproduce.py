"""Independent finite-deadline verifier for opponent Prize race gust minimax.

Run as: python -m results.opponent_prize_race_gust.reproduce
"""
from functools import lru_cache
from math import isinf

from tools.gust_prize_minimax import enumerate_boards
from tools.opponent_prize_race_gust import attacks_to_win, forced_first_source


@lru_cache(maxsize=None)
def feasible_by(active, bench, bosses, catchers, own, opponent,
                turn, clock, deadline):
    """Independent existence of a strategy: exists action, forall promotions."""
    if own == 0:
        return True
    if opponent == 0 or deadline == 0:
        return False

    moves = [(active, bench, bosses, catchers)]
    for target_index in range(len(bench)):
        target = bench[target_index]
        pending = tuple(sorted(bench[:target_index] + bench[target_index + 1:] + (active,)))
        if bosses > 0:
            moves.append((target, pending, bosses - 1, catchers))
        if catchers > 0 and own > opponent:
            moves.append((target, pending, bosses, catchers - 1))

    for taken, remaining, b, c in moves:
        if taken >= own or not remaining:
            return True
        after = opponent - clock[turn % len(clock)]
        if after <= 0:
            continue
        if all(feasible_by(new_active, remaining[:j] + remaining[j+1:],
                           b, c, max(0, own - taken), after,
                           turn + 1, clock, deadline - 1)
               for j, new_active in enumerate(remaining)):
            return True
    return False


def verify():
    boards = [(a, b) for a, b, _ in enumerate_boards()]
    assert len(boards) == 146
    clocks = ((0,), (1,), (2,), (0, 1), (1, 0), (0, 2),
              (2, 0), (1, 2), (2, 1))
    inventories = ((0, 2), (1, 1), (2, 0))
    checked = 0
    reports = {}
    source_checks = 0
    for clock in clocks:
        for opponent in range(1, 7):
            num_winnable = [0, 0, 0]
            attack_sum = [0, 0, 0]
            strict = 0
            for a, bench in boards:
                previous = []
                for index, (bosses, catchers) in enumerate(inventories):
                    value = attacks_to_win(a, bench, bosses, catchers,
                                           6, opponent, 0, clock)
                    previous.append(value)
                    possible = [feasible_by(a, bench, bosses, catchers,
                                            6, opponent, 0, clock, d)
                                for d in range(1, len(bench) + 2)]
                    expected = next((d for d, ok in enumerate(possible, 1)
                                     if ok), float("inf"))
                    assert value == expected, (clock, opponent, a, bench,
                                               index, value, expected)
                    assert all(not possible[j] or possible[j+1]
                               for j in range(len(possible)-1))
                    if not isinf(value):
                        num_winnable[index] += 1
                        attack_sum[index] += value
                    checked += 1
                assert previous[0] >= previous[1] >= previous[2]
                if opponent < 6:
                    forced_c = forced_first_source(a, bench, 6, opponent, clock, "C")
                    forced_b = forced_first_source(a, bench, 6, opponent, clock, "B")
                    assert forced_c <= forced_b, (clock, opponent, a, bench,
                                                  forced_c, forced_b)
                    strict += forced_c < forced_b
                    source_checks += 1
            reports[(clock, opponent)] = (
                tuple(num_winnable), tuple(attack_sum), strict)
    assert checked == len(clocks) * 6 * len(boards) * len(inventories)
    assert source_checks == len(clocks) * 5 * len(boards)

    old_sums = {1: (392, 392, 392), 2: (398, 392, 392),
                3: (480, 392, 392), 4: (516, 398, 392),
                5: (516, 398, 392)}
    old_priority = {1: 0, 2: 0, 3: 73, 4: 94, 5: 100}
    for opponent, sums in old_sums.items():
        assert reports[((0,), opponent)] == ((146, 146, 146),
                                              sums, old_priority[opponent])

    witness = [(0,), (1,)]
    assert [attacks_to_win(2, (1, 2, 2), b, c, 6, 4, 0, witness[0])
            for b, c in inventories] == [4, 4, 3]
    assert [attacks_to_win(2, (1, 2, 2), b, c, 6, 4, 0, witness[1])
            for b, c in inventories] == [4, 3, 3]

    print('clock    opponent    winnable (2C, B+C, 2B)    sum attacks on winnable    strict C-first')
    for clock in ((0,), (1,), (2,)):
        for opponent in (3, 4, 5, 6):
            n, s, c = reports[(clock, opponent)]
            print(f'{str(clock):9} {opponent:>3}  {str(n):>24}  {str(s):>23}  {c}')
    print(f'PASS: {checked} independent deadline oracles, {source_checks} first-source exchanges, old baseline and live-race witness')


if __name__ == '__main__':
    verify()
