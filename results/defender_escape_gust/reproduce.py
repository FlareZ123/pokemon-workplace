"""Independent finite-horizon game tree for defensive switching of wounded Active."""
from collections import Counter
from functools import lru_cache
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.durable_gust_minimax import enumerate_boards
from tools.durable_gust_minimax import minimum_attacks as no_escape
from tools.defender_escape_gust import minimum_attacks


@lru_cache(None)
def guaranteed_win(a, b, g, e, need, turns):
    if need <= 0:
        return True
    if turns == 0:
        return False
    for i in range(-1, len(b) if g else 0):
        if i == -1:
            target, others, tokens = a, b, g
        else:
            target = b[i]
            others = tuple(sorted((a,) + b[:i] + b[i + 1 :]))
            tokens = g - 1

        prize, hits = target
        if hits > 1:
            wounded = (prize, hits - 1)
            defender = [(wounded, others, e)]
            if e:
                defender.extend(
                    (p, tuple(sorted((wounded,) + others[:j] + others[j + 1 :])), e - 1)
                    for j, p in enumerate(others)
                )
            if all(guaranteed_win(p, bb, tokens, ee, need, turns - 1)
                   for p, bb, ee in defender):
                return True
        elif prize >= need or not others:
            return True
        elif all(
            guaranteed_win(p, others[:j] + others[j + 1 :], tokens, e, need - prize, turns - 1)
            for j, p in enumerate(others)
        ):
            return True
    return False


def main():
    classes = []
    checks = 0
    for active, bench, values in enumerate_boards():
        layers = []
        for e in range(3):
            scores = []
            for g in range(3):
                answer = minimum_attacks(active, bench, g, e)
                deadline = next(
                    t for t in range(1, sum(h for _, h in values) + 1)
                    if guaranteed_win(active, bench, g, e, 6, t)
                )
                assert answer == deadline, (active, bench, g, e, answer, deadline)
                if e == 0:
                    assert answer == no_escape(active, bench, g)
                if e:
                    assert answer >= layers[e - 1][g]
                scores.append(answer)
                checks += 1
            assert scores[0] >= scores[1] >= scores[2]
            layers.append(tuple(scores))
        classes.append(tuple(layers))

    assert len(classes) == 390 and checks == 3510
    hist = []
    complements = []
    for e in range(3):
        one = Counter(s[e][0] - s[e][1] for s in classes)
        both = Counter(s[e][0] - s[e][2] for s in classes)
        inc = sum(s[e][1] - s[e][2] > s[e][0] - s[e][1] for s in classes)
        hist.append((one, both))
        complements.append(inc)
    assert hist[0][0] == {0: 224, 1: 94, 2: 56, 3: 12, 4: 4}
    assert hist[1][0] == {0: 300, 1: 72, 2: 12, 3: 5, 4: 1}
    assert hist[2][0] == {0: 325, 1: 47, 2: 12, 3: 5, 4: 1}
    assert hist[0][1] == {0: 122, 1: 105, 2: 126, 3: 30, 4: 7}
    assert hist[1][1] == {0: 151, 1: 127, 2: 78, 3: 29, 4: 5}
    assert hist[2][1] == {0: 168, 1: 136, 2: 58, 3: 24, 4: 4}
    assert complements == [107, 157, 161]

    affected = sum(s[1][0] - s[1][2] < s[0][0] - s[0][2] for s in classes)
    new_complements = sum(
        s[1][1] - s[1][2] > s[1][0] - s[1][1]
        and not (s[0][1] - s[0][2] > s[0][0] - s[0][1]) for s in classes
    )
    assert (affected, new_complements) == (79, 104)
    assert [
        tuple(minimum_attacks((1, 2), ((1, 2), (3, 2), (3, 2)), g, e)
              for g in range(3)) for e in range(3)
    ] == [(8, 8, 4), (8, 8, 8), (8, 8, 8)]

    print("PASS", checks, "Boolean deadline comparisons and", len(classes)*3, "no-escape comparisons")
    for e, ((one, both), c) in enumerate(zip(hist, complements)):
        print("Escape", e, "one-gust gains", dict(sorted(one.items())),
              "two-gust gains", dict(sorted(both.items())), "complementarity", c)
    print("One-escape reduction of two-gust benefit in", affected, "classes")
    print("New second-marginal complementarity in", new_complements, "classes")


if __name__ == "__main__":
    main()
