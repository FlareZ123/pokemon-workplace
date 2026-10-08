"""Independent state-budget oracle for orthogonal gust target and Prize gates.

Run: python -m results.gust_source_incomparability.reproduce
"""
from collections import Counter
from functools import lru_cache

from tools.gust_source_incomparability import minimum_gust_attacks
from tools.mixed_gust_prize_minimax import mixed_gust_attacks
from tools.target_restricted_gust_minimax import (
    PRIZE_VALUE, enumerate_typed_boards, minimum_typed_attacks,
)


@lru_cache(None)
def possible_by(active, bench, bosses, serenas, catchers, own, opponent, turns):
    """Existential attacker actions; universal next-Active choices at a deadline."""
    if own <= 0:
        return True
    if turns <= 0:
        return False
    if not bench:
        return True
    actions = [(active, bench, bosses, serenas, catchers)]
    for i, target in enumerate(bench):
        rest = tuple(sorted((active,) + bench[:i] + bench[i + 1 :]))
        if bosses:
            actions.append((target, rest, bosses - 1, serenas, catchers))
        if serenas and target.startswith("V"):
            actions.append((target, rest, bosses, serenas - 1, catchers))
        if catchers and own > opponent:
            actions.append((target, rest, bosses, serenas, catchers - 1))
    for target, rest, b, s, c in actions:
        if PRIZE_VALUE[target] >= own or not rest:
            return True
        if all(
            possible_by(p, rest[:i] + rest[i + 1 :], b, s, c,
                        own - PRIZE_VALUE[target], opponent, turns - 1)
            for i, p in enumerate(rest)
        ):
            return True
    return False


def run():
    boards = tuple(enumerate_typed_boards())
    assert len(boards) == 1212
    inventories = {
        "two_boss": (2, 0, 0),
        "boss_serena": (1, 1, 0),
        "boss_counter": (1, 0, 1),
    }
    expected = {
        1: {-2: 10, -1: 116, 0: 1086},
        2: {-2: 10, -1: 116, 0: 1086},
        3: {-2: 10, -1: 116, 0: 1086},
        4: {-2: 10, -1: 104, 0: 1066, 1: 32},
        5: {-2: 10, -1: 104, 0: 1066, 1: 32},
    }
    expected_sums = {
        1: (2946, 3082, 2946),
        2: (2946, 3082, 2946),
        3: (2946, 3082, 2946),
        4: (2946, 3082, 2990),
        5: (2946, 3082, 2990),
    }
    total_checked = 0
    for opponent in range(1, 6):
        distribution = Counter()
        sums = {key: 0 for key in inventories}
        for active, bench, values in boards:
            score = {}
            for name, (bosses, serenas, catchers) in inventories.items():
                attacks = minimum_gust_attacks(
                    active, bench, bosses, serenas, catchers, 6, opponent
                )
                assert possible_by(
                    active, bench, bosses, serenas, catchers, 6, opponent,
                    attacks
                )
                assert not possible_by(
                    active, bench, bosses, serenas, catchers, 6, opponent,
                    attacks - 1
                )
                score[name] = attacks
                sums[name] += attacks
                total_checked += 1

            assert score["two_boss"] <= min(score["boss_serena"], score["boss_counter"])
            assert score["boss_serena"] == minimum_typed_attacks(
                active, bench, 1, 1
            )
            if all(not v.startswith("V") for v in values):
                assert score["boss_counter"] == mixed_gust_attacks(
                    PRIZE_VALUE[active],
                    tuple(sorted(PRIZE_VALUE[x] for x in bench)),
                    1, 1, 6, opponent
                )
            distribution[score["boss_counter"] - score["boss_serena"]] += 1

        assert dict(distribution) == expected[opponent]
        assert (
            sums["two_boss"], sums["boss_serena"], sums["boss_counter"]
        ) == expected_sums[opponent]
        print(f"opponent={opponent}: diff_C_minus_S={dict(sorted(distribution.items()))} "
              f"attack_sums={sums}")

    assert total_checked == 18180
    a, b = "N1", ("N3", "N3")
    assert (
        minimum_gust_attacks(a, b, 1, 0, 1, 6, 4),
        minimum_gust_attacks(a, b, 1, 1, 0, 6, 4),
    ) == (2, 3)
    a, b = "N2", ("N1", "N2", "V2")
    assert (
        minimum_gust_attacks(a, b, 1, 0, 1, 6, 4),
        minimum_gust_attacks(a, b, 1, 1, 0, 6, 4),
    ) == (4, 3)
    print(f"PASS: {total_checked} independent typed/Prize-gated comparisons")


if __name__ == "__main__":
    run()
