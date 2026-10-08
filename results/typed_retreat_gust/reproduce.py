"""Independent attack-deadline and cross-kernel tests for typed defensive retreat."""
from collections import Counter
from dataclasses import replace
from functools import lru_cache
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.durable_gust_minimax import enumerate_boards
from tools.durable_gust_minimax import minimum_attacks as no_escape
from tools.defender_escape_gust import minimum_attacks as abstract_escape
from tools.typed_retreat_gust import Target, minimum_attacks, retreat_payment_remainders


@lru_cache(None)
def can_win(a, b, g, items, allowed, need, turns):
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
        if target.hits > 1:
            hurt = replace(target, hits=target.hits - 1)
            defender = [(hurt, others, items)]
            for j, p in enumerate(others):
                rest = others[:j] + others[j + 1 :]
                if not hurt.retreat_blocked:
                    for residual in retreat_payment_remainders(hurt.energy_cards, hurt.retreat_cost):
                        defender.append((
                            p, tuple(sorted((replace(hurt, energy_cards=residual),) + rest)), items
                        ))
                if items and allowed:
                    defender.append((p, tuple(sorted((hurt,) + rest)), items - 1))
            if all(can_win(p, bb, tokens, left, allowed, need, turns - 1)
                   for p, bb, left in defender):
                return True
        elif target.prize >= need or not others:
            return True
        elif all(
            can_win(p, others[:j] + others[j + 1 :], tokens, items,
                    allowed, need - target.prize, turns - 1)
            for j, p in enumerate(others)
        ):
            return True
    return False


def adapted(card, case):
    prize, hits = card
    energy = (1,) if (
        case == "all"
        or case == "high" and prize == 3
        or case == "low" and prize == 1
    ) else ()
    return Target(prize, hits, 1, energy)


def main():
    assert retreat_payment_remainders((2, 1, 1), 2) == ((1, 1), (2,))
    assert retreat_payment_remainders((2, 1, 1, 1), 3) == ((1, 1), (2,))
    assert retreat_payment_remainders((1, 2), 0) == ((1, 2),)
    assert retreat_payment_remainders((1,), 2) == ()

    records = []
    checks = 0
    bridges = 0
    for active, bench, values in enumerate_boards():
        data = {}
        for case in ("none", "high", "low", "all"):
            a = adapted(active, case)
            b = tuple(sorted(adapted(c, case) for c in bench))
            scores = []
            for g in range(3):
                actual = minimum_attacks(a, b, g)
                deadline = next(
                    t for t in range(1, sum(hits for _, hits in values) + 1)
                    if can_win(a, b, g, 0, True, 6, t)
                )
                assert actual == deadline, (values, active, case, g, actual, deadline)
                scores.append(actual)
                checks += 1
            data[case] = tuple(scores)

        blocked_a = Target(active[0], active[1], 1, (), True)
        blocked_b = tuple(sorted(Target(v, h, 1, (), True) for v, h in bench))
        for g in range(3):
            assert data["none"][g] == no_escape(active, bench, g)
            assert minimum_attacks(blocked_a, blocked_b, g, 1, True) == abstract_escape(
                active, bench, g, 1
            )
            assert minimum_attacks(blocked_a, blocked_b, g, 1, False) == no_escape(
                active, bench, g
            )
            bridges += 3
        records.append(data)

    assert len(records) == 390 and checks == 4680 and bridges == 3510
    expected = {
        "none": ({0: 122, 1: 105, 2: 126, 3: 30, 4: 7}, 107),
        "high": ({0: 145, 1: 132, 2: 85, 3: 24, 4: 4}, 169),
        "low": ({0: 120, 1: 112, 2: 117, 3: 34, 4: 7}, 109),
        "all": ({0: 171, 1: 134, 2: 57, 3: 24, 4: 4}, 159),
    }
    for case, (hist, complement) in expected.items():
        actual_hist = Counter(r[case][0] - r[case][2] for r in records)
        actual_complement = sum(
            r[case][1] - r[case][2] > r[case][0] - r[case][1]
            for r in records
        )
        assert actual_hist == hist and actual_complement == complement
        print(case, "two-gust benefit", dict(sorted(actual_hist.items())),
              "increasing second marginal", actual_complement)

    high_affected = sum(
        r["high"][0] - r["high"][2] < r["none"][0] - r["none"][2]
        for r in records
    )
    low_affected = sum(
        r["low"][0] - r["low"][2] < r["none"][0] - r["none"][2]
        for r in records
    )
    assert (high_affected, low_affected) == (70, 6)

    a = Target(1, 2, 1)
    base = (Target(1, 2, 1), Target(3, 2, 1), Target(3, 2, 1))
    high = (Target(1, 2, 1), Target(3, 2, 1, (1,)), Target(3, 2, 1, (1,)))
    blocked = tuple(replace(t, retreat_blocked=True) for t in base)
    assert [tuple(minimum_attacks(a, b, g) for g in range(3)) for b in (base, high)] == [
        (8, 8, 4), (8, 8, 8)
    ]
    assert tuple(minimum_attacks(replace(a, retreat_blocked=True), blocked, g, 1, False)
                 for g in range(3)) == (8, 8, 4)

    print("PASS", checks, "Boolean horizon states;", bridges, "cross-kernel identities")
    print("Two-gust value reduced in", high_affected, "three-Prize-Energy states versus",
          low_affected, "one-Prize-Energy states")


if __name__ == "__main__":
    main()
