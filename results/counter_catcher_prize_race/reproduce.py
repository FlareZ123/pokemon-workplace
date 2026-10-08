"""Independent Boolean deadline and cross-kernel tests for Prize-clock scenarios."""
from collections import Counter
from functools import lru_cache
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.counter_catcher_prize_race import IMPOSSIBLE, attacks_to_win
from tools.counter_catcher_prize_timing import counter_catcher_attacks
from tools.gust_prize_minimax import enumerate_boards, minimum_attacks


@lru_cache(None)
def can_win(active, bench, gusts, mine, theirs, pace, source, turns):
    """Exact adversarial win feasibility with a fixed attack deadline."""
    if mine <= 0:
        return True
    if theirs <= 0 or turns == 0:
        return False
    moves = [(active, bench, gusts)]
    if gusts and (source == "boss" or mine > theirs):
        for i, reward in enumerate(bench):
            remainder = tuple(sorted((active,) + bench[:i] + bench[i + 1:]))
            moves.append((reward, remainder, gusts - 1))
    for reward, rest, left in moves:
        if reward >= mine or not rest:
            return True
        if theirs <= pace:
            continue
        if all(
            can_win(
                promoted, rest[:j] + rest[j + 1:],
                left, mine - reward, theirs - pace,
                pace, source, turns - 1
            )
            for j, promoted in enumerate(rest)
        ):
            return True
    return False


def main():
    boards = tuple(enumerate_boards())
    assert len(boards) == 146

    validated = 0
    for active, bench, values in boards:
        for pace in range(3):
            for opponent in range(1, 7):
                for g in range(3):
                    for source in ("boss", "counter_catcher"):
                        value = attacks_to_win(active, bench, g, 6, opponent, pace, source)
                        possible = next(
                            (
                                t for t in range(1, len(values) + 1)
                                if can_win(active, bench, g, 6, opponent, pace, source, t)
                            ),
                            IMPOSSIBLE,
                        )
                        assert value == possible, (active, bench, pace, opponent, g, source)
                        if pace == 0:
                            if source == "counter_catcher":
                                assert value == counter_catcher_attacks(
                                    active, bench, g, 6, opponent
                                )
                            else:
                                assert value == minimum_attacks(active, bench, g, 6)
                        validated += 1

    assert validated == 15768
    expected = {
        (0, 3): (146, 0, 70, 64, 12),
        (1, 3): (123, 23, 123, 0, 0),
        (1, 4): (141, 5, 65, 64, 12),
        (2, 6): (85, 23, 35, 50, 0),
    }

    for (pace, opp), wanted in expected.items():
        both_won = both_lost = equal = plus1 = plus2 = 0
        boss_only = 0
        for a, b, _ in boards:
            c = attacks_to_win(a, b, 2, 6, opp, pace, "counter_catcher")
            B = attacks_to_win(a, b, 2, 6, opp, pace, "boss")
            if c < IMPOSSIBLE and B < IMPOSSIBLE:
                both_won += 1
                equal += (c == B)
                plus1 += (c == B + 1)
                plus2 += (c == B + 2)
            elif c >= IMPOSSIBLE and B >= IMPOSSIBLE:
                both_lost += 1
            elif c >= IMPOSSIBLE and B < IMPOSSIBLE:
                boss_only += 1
            else:
                raise AssertionError("Counter Catcher exceeds unrestricted Boss")
        assert (both_won, both_lost, equal, plus1, plus2) == wanted
        assert boss_only == (38 if (pace, opp) == (2, 6) else 0)
        assert both_won + both_lost + boss_only == 146
        print(f"Pace {pace}, opp Prizes {opp}: both win {both_won}, "
              f"both lose {both_lost}, Boss-only wins {boss_only}, "
              f"shared-win attack delta {equal}/{plus1}/{plus2} (0/1/2)")

    # Opponent taking one Prize between attacks reopens a Catcher gate after
    # the initial three-Prize KO, restoring the two-turn line.
    assert attacks_to_win(3, (1, 3), 2, 6, 3, 0, "counter_catcher") == 3
    assert attacks_to_win(3, (1, 3), 2, 6, 3, 1, "counter_catcher") == 2
    assert attacks_to_win(3, (1, 3), 2, 6, 3, 1, "boss") == 2

    # Initially tied on six Prizes and against an opponent taking two per
    # turn, the Catcher route cannot force the otherwise available 2-turn win.
    assert attacks_to_win(1, (1, 3, 3), 2, 6, 6, 2, "boss") == 2
    assert attacks_to_win(1, (1, 3, 3), 2, 6, 6, 2, "counter_catcher") == IMPOSSIBLE
    print("PASS", validated, "independent turn-deadline checks + pace-zero reductions")


if __name__ == "__main__":
    main()
