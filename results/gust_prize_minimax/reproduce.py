"""Independent Boolean turn-horizon validation for the gust minimax solver."""
from collections import Counter
from functools import lru_cache
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.gust_prize_minimax import enumerate_boards, minimum_attacks, must_gust_now


@lru_cache(None)
def can_win(a: int, b: tuple[int, ...], g: int, need: int, turns: int) -> bool:
    if need <= 0:
        return True
    if turns == 0:
        return False
    for i in range(-1, len(b) if g else 0):
        if i == -1:
            prize, remaining, tokens = a, b, g
        else:
            prize = b[i]
            remaining = tuple(sorted((a,) + b[:i] + b[i + 1:]))
            tokens = g - 1
        if prize >= need or not remaining:
            return True
        if all(
            can_win(p, remaining[:j] + remaining[j + 1:], tokens, need - prize, turns - 1)
            for j, p in enumerate(remaining)
        ):
            return True
    return False


def main() -> None:
    rows = []
    for active, bench, values in enumerate_boards():
        scores = tuple(minimum_attacks(active, bench, g, 6) for g in range(3))
        assert scores[0] >= scores[1] >= scores[2]
        assert scores[0] <= len(values)
        for g in range(3):
            oracle = next(
                k for k in range(1, len(values) + 1)
                if can_win(active, bench, g, 6, k)
            )
            assert oracle == scores[g], (active, bench, g, oracle, scores[g])
        rows.append((active, bench, values, scores, must_gust_now(active, bench, 1, 6)))

    assert len(rows) == 146
    first = Counter(r[3][0] - r[3][1] for r in rows)
    both = Counter(r[3][0] - r[3][2] for r in rows)
    complement = sum(r[3][1] - r[3][2] > r[3][0] - r[3][1] for r in rows)
    eager_regret = Counter(r[4] - r[3][1] for r in rows if r[4] > r[3][1])
    assert first == {0: 77, 1: 54, 2: 15}, first
    assert both == {0: 38, 1: 70, 2: 35, 3: 3}, both
    assert complement == 41, complement
    assert eager_regret == {1: 41, 2: 14}, eager_regret
    assert tuple(minimum_attacks(1, (1, 3, 3), g) for g in range(3)) == (4, 4, 2)
    assert (minimum_attacks(3, (1, 3), 1), must_gust_now(3, (1, 3), 1)) == (2, 3)

    print(f"PASS: {len(rows)} boards; {len(rows) * 3} independent horizon checks")
    print("One-gust reduction:", dict(sorted(first.items())))
    print("Two-gust reduction:", dict(sorted(both.items())))
    print("Increasing second marginal:", complement)
    print("Forced first-turn gust regret:", dict(sorted(eager_regret.items())))


if __name__ == "__main__":
    main()
