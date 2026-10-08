"""Independent finite-attack-deadline oracle for Counter Catcher's live Prize gate."""
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.counter_catcher_prize_timing import census, counter_catcher_attacks
from tools.gust_prize_minimax import minimum_attacks


@lru_cache(None)
def can_win(a, b, available, need, opponent_remaining, turns):
    """Can attacker force a win within t attacks under adversarial promotions?"""
    if need <= 0:
        return True
    if turns == 0:
        return False
    targets = [(a, b, available)]
    if available and need > opponent_remaining:
        for i, prize in enumerate(b):
            targets.append((prize, tuple(sorted((a,) + b[:i] + b[i + 1:])), available - 1))

    for reward, survivors, tokens in targets:
        if reward >= need or not survivors:
            return True
        if all(
            can_win(
                promoted, survivors[:j] + survivors[j + 1:],
                tokens, need - reward, opponent_remaining, turns - 1
            )
            for j, promoted in enumerate(survivors)
        ):
            return True
    return False


def main():
    rows = census()
    assert len(rows) == 730
    by_opponent = defaultdict(list)
    checks = 0
    for opp, active, bench, boss_two, cc_one, cc_two in rows:
        for count in range(3):
            actual = counter_catcher_attacks(active, bench, count, 6, opp)
            oracle = next(
                t for t in range(1, len(bench) + 2)
                if can_win(active, bench, count, 6, opp, t)
            )
            assert actual == oracle, (opp, active, bench, count, actual, oracle)
            checks += 1
        assert boss_two <= cc_two <= cc_one
        assert cc_one >= minimum_attacks(active, bench, 1, 6)
        by_opponent[opp].append((active, bench, boss_two, cc_one, cc_two))

    assert checks == 2190
    expected_gaps = {
        1: {0: 146},
        2: {0: 140, 1: 6},
        3: {0: 70, 1: 64, 2: 12},
        4: {0: 47, 1: 74, 2: 25},
        5: {0: 47, 1: 74, 2: 25},
    }
    expected_attack_sums = {
        1: (541, 457, 392),
        2: (541, 457, 398),
        3: (541, 503, 480),
        4: (541, 516, 516),
        5: (541, 516, 516),
    }
    for opp, group in by_opponent.items():
        diff = Counter(cc_two - boss_two for _, _, boss_two, cc_one, cc_two in group)
        sums = tuple(
            sum(counter_catcher_attacks(a, b, n, 6, opp) for a, b, *_ in group)
            for n in range(3)
        )
        assert diff == expected_gaps[opp], (opp, diff)
        assert sums == expected_attack_sums[opp], (opp, sums)
        print(f"Opp Prizes {opp}: 2 CC vs 2 Boss attack penalty {dict(sorted(diff.items()))};"
              f" costs sum {sums}")

    # Opponent has three Prizes left: taking a three-Prize KO moves us from
    # six to three remaining Prizes and makes later Counter Catcher unusable.
    assert minimum_attacks(3, (1, 3), 1, 6) == 2
    assert counter_catcher_attacks(3, (1, 3), 1, 6, 3) == 3
    assert counter_catcher_attacks(3, (1, 3), 2, 6, 3) == 3

    # With opponent on two Prizes, the first three-Prize KO still leaves us behind.
    assert counter_catcher_attacks(3, (1, 3), 1, 6, 2) == 2

    assert minimum_attacks(1, (1, 3, 3), 2, 6) == 2
    assert [counter_catcher_attacks(1, (1, 3, 3), 2, 6, opp)
            for opp in range(1, 6)] == [2, 2, 4, 4, 4]
    print(f"PASS {checks} independent horizon checks; 730 direct Boss comparisons")


if __name__ == "__main__":
    main()
