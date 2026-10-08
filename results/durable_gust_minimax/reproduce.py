"""Independent finite-horizon proof of the damage-aware gust minimax census."""
from collections import Counter
from functools import lru_cache
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.durable_gust_minimax import enumerate_boards, minimum_attacks, must_gust_now
from tools.gust_prize_minimax import enumerate_boards as simple_boards
from tools.gust_prize_minimax import minimum_attacks as simple_minimum


@lru_cache(None)
def can_win(active, bench, gusts, prizes_needed, turns):
    if prizes_needed <= 0:
        return True
    if turns == 0:
        return False
    for i in range(-1, len(bench) if gusts else 0):
        if i == -1:
            target, others, tokens = active, bench, gusts
        else:
            target = bench[i]
            others = tuple(sorted((active,) + bench[:i] + bench[i + 1 :]))
            tokens = gusts - 1
        reward, hits = target
        if hits > 1:
            if can_win((reward, hits - 1), others, tokens, prizes_needed, turns - 1):
                return True
        elif reward >= prizes_needed or not others:
            return True
        elif all(
            can_win(p, others[:j] + others[j + 1 :], tokens, prizes_needed - reward, turns - 1)
            for j, p in enumerate(others)
        ):
            return True
    return False


def main():
    rows = []
    for active, bench, values in enumerate_boards():
        scores = tuple(minimum_attacks(active, bench, g) for g in range(3))
        assert scores[0] >= scores[1] >= scores[2]
        for g, cost in enumerate(scores):
            oracle = next(
                t for t in range(1, sum(hits for _, hits in values) + 1)
                if can_win(active, bench, g, 6, t)
            )
            assert oracle == cost, (active, bench, g, oracle, cost)
        rows.append((active, bench, values, scores, must_gust_now(active, bench, 1)))

    assert len(rows) == 390
    first = Counter(row[3][0] - row[3][1] for row in rows)
    two = Counter(row[3][0] - row[3][2] for row in rows)
    complement = sum(row[3][1] - row[3][2] > row[3][0] - row[3][1] for row in rows)
    early = sum(row[4] > row[3][1] for row in rows)
    assert first == {0: 224, 1: 94, 2: 56, 3: 12, 4: 4}
    assert two == {0: 122, 1: 105, 2: 126, 3: 30, 4: 7}
    assert complement == 107
    assert early == 141
    assert tuple(minimum_attacks((1, 2), ((1, 2), (3, 2), (3, 2)), g) for g in range(3)) == (8, 8, 4)
    assert tuple(minimum_attacks((3, 1), ((1, 2), (1, 2), (3, 1)), g) for g in range(3)) == (6, 2, 2)

    # A one-hit-durability Pokemon must reduce to the original model exactly.
    limit_checks = 0
    for a, b, values in simple_boards():
        if len(values) > 4:
            continue
        for g in range(3):
            assert minimum_attacks((a, 1), tuple((p, 1) for p in b), g) == simple_minimum(a, b, g)
            limit_checks += 1
    assert limit_checks == 117
    print("PASS:", len(rows) * 3, "independent horizon checks;", limit_checks, "one-hit reduction checks")
    print("One gust attack savings:", dict(sorted(first.items())))
    print("Two gust attack savings:", dict(sorted(two.items())))
    print("Increasing second marginal:", complement, "of", len(rows))
    print("First-turn forced-gust regret:", early, "of", len(rows))


if __name__ == "__main__":
    main()
