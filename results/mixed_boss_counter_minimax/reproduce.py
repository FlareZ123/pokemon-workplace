"""Independent attack-deadline oracle for mixed Boss/Counter source timing."""
from collections import Counter
from functools import lru_cache
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.counter_catcher_prize_timing import counter_catcher_attacks
from tools.gust_prize_minimax import enumerate_boards, minimum_attacks as boss_only
from tools.mixed_boss_counter_minimax import minimum_attacks, forced_first_source


@lru_cache(None)
def guaranteed_win(active, bench, b, c, ours, theirs, attacks_left):
    if ours <= 0:
        return True
    if attacks_left <= 0:
        return False
    actions = [(active, bench, b, c)]
    for i in range(len(bench)):
        reward = bench[i]
        rest = tuple(sorted((active,) + bench[:i] + bench[i + 1:]))
        if b:
            actions.append((reward, rest, b - 1, c))
        if c and ours > theirs:
            actions.append((reward, rest, b, c - 1))

    for reward, rest, remaining_b, remaining_c in actions:
        if reward >= ours or not rest:
            return True
        if all(
            guaranteed_win(
                promoted, rest[:j] + rest[j + 1:],
                remaining_b, remaining_c, ours - reward,
                theirs, attacks_left - 1
            )
            for j, promoted in enumerate(rest)
        ):
            return True
    return False


def main():
    boards = tuple(enumerate_boards())
    assert len(boards) == 146
    expected_mixed_gap = {
        1: {0: 146},
        2: {0: 146},
        3: {0: 146},
        4: {0: 140, 1: 6},
        5: {0: 140, 1: 6},
    }
    expected_counter_gap = {
        1: {0: 146},
        2: {0: 140, 1: 6},
        3: {0: 70, 1: 64, 2: 12},
        4: {0: 52, 1: 70, 2: 24},
        5: {0: 52, 1: 70, 2: 24},
    }
    expected_source_waste = {
        1: (0, 292),
        2: (0, 292),
        3: (82, 210),
        4: (130, 162),
        5: (162, 130),
    }
    checks = 0
    for opponent_prizes in range(1, 6):
        mixed_gap = Counter()
        pure_counter_minus_mixed = Counter()
        strict = equal = 0
        for a, bench, values in boards:
            for b in range(3):
                for c in range(3):
                    cost = minimum_attacks(a, bench, b, c, 6, opponent_prizes)
                    deadline = next(
                        t for t in range(1, len(values) + 1)
                        if guaranteed_win(a, bench, b, c, 6, opponent_prizes, t)
                    )
                    assert cost == deadline, (
                        opponent_prizes, a, bench, b, c, cost, deadline
                    )
                    if c == 0:
                        assert cost == boss_only(a, bench, b)
                    if b == 0:
                        assert cost == counter_catcher_attacks(
                            a, bench, c, 6, opponent_prizes
                        )
                    checks += 1

            boss2 = minimum_attacks(a, bench, 2, 0, 6, opponent_prizes)
            mixed = minimum_attacks(a, bench, 1, 1, 6, opponent_prizes)
            counter2 = minimum_attacks(a, bench, 0, 2, 6, opponent_prizes)
            assert boss2 <= mixed <= counter2
            mixed_gap[mixed - boss2] += 1
            pure_counter_minus_mixed[counter2 - mixed] += 1

            for target in sorted(set(bench)):
                use_boss = forced_first_source(
                    a, bench, opponent_prizes, "boss", target
                )
                use_counter = forced_first_source(
                    a, bench, opponent_prizes, "counter", target
                )
                assert use_boss is not None and use_counter is not None
                assert use_counter <= use_boss
                strict += use_counter < use_boss
                equal += use_counter == use_boss
        assert mixed_gap == expected_mixed_gap[opponent_prizes]
        assert pure_counter_minus_mixed == expected_counter_gap[opponent_prizes]
        assert (strict, equal) == expected_source_waste[opponent_prizes]
        print(
            f"Opponent Prizes {opponent_prizes}: mixed-vs-2Boss "
            f"{dict(sorted(mixed_gap.items()))}, "
            f"2Counter-vs-mixed {dict(sorted(pure_counter_minus_mixed.items()))}, "
            f"costly Boss-first choices {strict}/292"
        )

    assert checks == 6570
    assert [minimum_attacks(1, (1, 3, 3), b, c, 6, 3)
            for b, c in ((2, 0), (1, 1), (0, 2))] == [2, 2, 4]
    assert forced_first_source(1, (1, 3, 3), 3, "counter", 3) == 2
    assert forced_first_source(1, (1, 3, 3), 3, "boss", 3) == 4
    assert minimum_attacks(2, (1, 2, 2), 2, 0, 6, 4) == 3
    assert minimum_attacks(2, (1, 2, 2), 1, 1, 6, 4) == 4
    print("PASS 6,570 independently checked source/board/Prize scenarios")


if __name__ == "__main__":
    main()
