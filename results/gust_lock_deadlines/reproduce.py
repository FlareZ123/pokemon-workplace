"""Independent finite-horizon test for gust expiration under typed locks.

Invoke with: python -m results.gust_lock_deadlines.reproduce
"""
from collections import Counter
from functools import lru_cache

from tools.gust_prize_minimax import enumerate_boards
from tools.gust_lock_deadlines import force_first_source, minimum_attacks_with_locks
from tools.mixed_gust_prize_minimax import mixed_gust_attacks


@lru_cache(None)
def possible_by(active, bench, bosses, catchers, own, opponent,
                turn, supporter_lock, item_lock, attacks_left):
    """Winning policy within attacks_left, testing every defensive promotion."""
    if own <= 0:
        return True
    if attacks_left <= 0:
        return False
    if not bench:
        return True
    actions = [(active, bench, bosses, catchers)]
    for i, prize in enumerate(bench):
        rest = tuple(sorted((active,) + bench[:i] + bench[i + 1 :]))
        if bosses and turn < supporter_lock:
            actions.append((prize, rest, bosses - 1, catchers))
        if catchers and turn < item_lock and own > opponent:
            actions.append((prize, rest, bosses, catchers - 1))
    for prize, rest, b, c in actions:
        if prize >= own or not rest:
            return True
        if all(possible_by(p, rest[:i] + rest[i + 1 :], b, c,
                           own - prize, opponent, turn + 1,
                           supporter_lock, item_lock, attacks_left - 1)
               for i, p in enumerate(rest)):
            return True
    return False


def run():
    boards = tuple((a, b) for a, b, _ in enumerate_boards())
    assert len(boards) == 146
    scenarios = {
        "none": (99, 99),
        "supporter_T2": (2, 99),
        "item_T2": (99, 2),
        "both_T2": (2, 2),
        "supporter_T3": (3, 99),
        "item_T3": (99, 3),
    }
    attack_sums = {
        "none": (392, 392, 392, 398, 398),
        "supporter_T2": (398, 398, 480, 516, 516),
        "item_T2": (398, 398, 398, 398, 398),
        "both_T2": (516, 516, 516, 516, 516),
        "supporter_T3": (392, 398, 398, 398, 398),
        "item_T3": (392, 392, 392, 398, 398),
    }
    forced_priority = {
        "none": ((0, 0), (0, 0), (73, 0), (94, 0), (100, 0)),
        "supporter_T2": ((0, 100), (0, 100), (0, 36), (0, 9), (0, 0)),
        "item_T2": ((100, 0),) * 5,
        "both_T2": ((0, 0),) * 5,
        "supporter_T3": ((0, 0), (0, 0), (73, 0), (94, 0), (100, 0)),
        "item_T3": ((0, 0), (0, 0), (73, 0), (94, 0), (100, 0)),
    }
    checked = 0
    for scenario, (supporter_lock, item_lock) in scenarios.items():
        row = []
        orders = []
        for opp in range(1, 6):
            total = 0
            better_c = better_b = 0
            for active, bench in boards:
                attacks = minimum_attacks_with_locks(
                    active, bench, 1, 1, 6, opp, 1,
                    supporter_lock, item_lock
                )
                if scenario == "none":
                    assert attacks == mixed_gust_attacks(
                        active, bench, 1, 1, 6, opp
                    )
                assert possible_by(active, bench, 1, 1, 6, opp, 1,
                                   supporter_lock, item_lock, attacks)
                assert not possible_by(active, bench, 1, 1, 6, opp, 1,
                                       supporter_lock, item_lock, attacks - 1)
                checked += 1
                total += attacks
                c_first = force_first_source(active, bench, 6, opp, "C",
                                             supporter_lock, item_lock)
                b_first = force_first_source(active, bench, 6, opp, "B",
                                             supporter_lock, item_lock)
                better_c += c_first < b_first
                better_b += b_first < c_first
            row.append(total)
            orders.append((better_c, better_b))
        assert tuple(row) == attack_sums[scenario], (scenario, row)
        assert tuple(orders) == forced_priority[scenario], (scenario, orders)
        print(f"{scenario}: total_attack_sums={row}, "
              f"forced_first_Cbetter_Bbetter={orders}")

    assert checked == 4380
    active, bench = 1, (1, 3, 3)
    assert minimum_attacks_with_locks(active, bench, 1, 1, 6, 1,
                                      1, 2, 99) == 2
    assert force_first_source(active, bench, 6, 1, "B", 2, 99) == 2
    assert force_first_source(active, bench, 6, 1, "C", 2, 99) == 4
    assert force_first_source(active, bench, 6, 1, "C", 99, 2) == 2
    assert force_first_source(active, bench, 6, 1, "B", 99, 2) == 4
    print(f"PASS: {checked} independent deadline checks, "
          "source priority reversals, and lock witnesses")


if __name__ == "__main__":
    run()
