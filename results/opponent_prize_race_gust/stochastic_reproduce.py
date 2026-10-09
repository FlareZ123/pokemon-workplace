"""Reproduce stochastic opponent Prize clock and score-choice census."""
from fractions import Fraction
from math import isinf
from tools.gust_prize_minimax import enumerate_boards
from tools.opponent_prize_race_gust import attacks_to_win
from tools.stochastic_opponent_prize_gust import (
    optimal_win_probability as win, robust_win_against_score_choice as robust,
)


def verify():
    boards = tuple((a, b) for a, b, _ in enumerate_boards())
    assert len(boards) == 146
    inventories = ((0, 2), (1, 1), (2, 0))
    grid = tuple(Fraction(i, 4) for i in range(5))
    anomalies = {op: [0, 0, 0] for op in range(1, 7)}
    withheld = {op: [0, 0, 0] for op in range(1, 7)}
    checked = 0
    for op in range(1, 7):
        for active, bench in boards:
            curves = []
            for index, (bosses, catchers) in enumerate(inventories):
                curve = tuple(win(active, bench, bosses, catchers, 6, op, p)
                              for p in grid)
                assert all(0 <= v <= 1 for v in curve)
                for i, clock in ((0, (0,)), (4, (2,))):
                    baseline = attacks_to_win(active, bench, bosses, catchers,
                                              6, op, 0, clock)
                    assert curve[i] == (0 if isinf(baseline) else 1)
                certain = robust(active, bench, bosses, catchers, 6, op)
                assert not certain or all(v == 1 for v in curve)
                anomalies[op][index] += any(x < y for x, y in zip(curve, curve[1:]))
                withheld[op][index] += (curve[-1] == 1 and not certain)
                curves.append(curve)
                checked += 5
            assert all(curves[0][i] <= curves[1][i] <= curves[2][i]
                       for i in range(5))
    assert checked == 13140
    assert anomalies == withheld
    assert anomalies[4] == [24, 0, 0]
    assert anomalies[6] == [7, 0, 0]
    assert all(anomalies[x] == [0, 0, 0] for x in (1, 2, 3, 5))
    for j in range(21):
        p = Fraction(j, 20)
        assert win(3, (1, 1, 3), 0, 2, 6, 4, p) == 1 - (1-p)*p*p
    assert win(3, (1, 1, 3), 0, 2, 6, 4, Fraction(3, 4)) == Fraction(55, 64)
    assert all(win(3, (1, 1, 3), b, c, 6, 4, Fraction(3, 4)) == 1
               for b, c in ((1, 1), (2, 0)))
    print("PASS: 13,140 rational states, 2,628 adversarial score choices, 21 witness points")
    for op, row in anomalies.items():
        print("opponent", op, "nonmonotone 2C/mixed/2B", row)


if __name__ == "__main__":
    verify()
