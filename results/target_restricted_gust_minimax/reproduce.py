"""Independent attack-deadline verification of V-family-only gust targeting.

Run: python -m results.target_restricted_gust_minimax.reproduce
"""
from collections import Counter
from functools import lru_cache

from tools.gust_prize_minimax import minimum_attacks
from tools.target_restricted_gust_minimax import (
    PRIZE_VALUE, enumerate_typed_boards, minimum_typed_attacks
)


@lru_cache(None)
def can_win_by(active, bench, bosses, serenas, needed, turns):
    """Can attacker force victory by a deadline, against every promotion?"""
    if needed <= 0:
        return True
    if turns <= 0:
        return False
    if not bench:
        return True

    actions = [(active, bench, bosses, serenas)]
    for i, target in enumerate(bench):
        rest = tuple(sorted((active,) + bench[:i] + bench[i + 1 :]))
        if bosses:
            actions.append((target, rest, bosses - 1, serenas))
        if serenas and target[:1] == "V":
            actions.append((target, rest, bosses, serenas - 1))

    for target, rest, b, s in actions:
        if PRIZE_VALUE[target] >= needed or not rest:
            return True
        if all(can_win_by(p, rest[:i] + rest[i + 1 :], b, s,
                          needed - PRIZE_VALUE[target], turns - 1)
               for i, p in enumerate(rest)):
            return True
    return False


def run():
    boards = tuple(enumerate_typed_boards())
    assert len(boards) == 1212
    inventory = ((2, 0), (1, 1), (0, 2))
    mixed_penalty = Counter()
    v_count_penalty = Counter()
    checked = 0

    for active, bench, values in boards:
        results = []
        for bosses, serenas in inventory:
            m = minimum_typed_attacks(active, bench, bosses, serenas)
            assert can_win_by(active, bench, bosses, serenas, 6, m)
            assert not can_win_by(active, bench, bosses, serenas, 6, m - 1)
            checked += 1
            results.append(m)

        assert results[0] <= results[1] <= results[2]
        mixed_penalty[results[1] - results[0]] += 1
        nv = sum(value.startswith("V") for value in values)
        v_count_penalty[(nv, results[1] > results[0])] += 1

        if nv == 0:
            assert results[0] == minimum_attacks(
                PRIZE_VALUE[active],
                tuple(sorted(PRIZE_VALUE[x] for x in bench)), 2, 6
            )

    assert checked == 3636
    assert mixed_penalty == {0: 1086, 1: 116, 2: 10}
    assert dict(v_count_penalty) == {
        (0, False): 91, (0, True): 55,
        (1, False): 255, (1, True): 46,
        (2, False): 297, (2, True): 18,
        (3, False): 234, (3, True): 6,
        (4, False): 139, (4, True): 1,
        (5, False): 58, (6, False): 12,
    }
    assert tuple(
        minimum_typed_attacks("V2", ("N3", "N3"), *t)
        for t in inventory
    ) == (2, 3, 3)
    assert tuple(
        minimum_typed_attacks("N3", ("N3", "V2"), *t)
        for t in inventory
    ) == (2, 2, 3)
    assert tuple(
        minimum_typed_attacks(
            "V2", ("N3", "N3", "V2", "V2", "V2"), *t
        )
        for t in inventory
    ) == (2, 3, 3)
    print("mixed_minus_two_Boss_penalty:", dict(sorted(mixed_penalty.items())))
    print("number_of_V_by_mixed_penalty:", dict(sorted(v_count_penalty.items())))
    print(f"PASS: {checked} independently verified typed-target endgames")


if __name__ == "__main__":
    run()
