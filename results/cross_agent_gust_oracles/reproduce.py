"""Cross-agent oracle agreement for typed gust and Prize-gated gust kernels.

The two agent implementations use different target representations and were
developed independently; this audit compares their shared state space.
Run: python -m results.cross_agent_gust_oracles.reproduce
"""
from collections import Counter

from tools.gust_prize_minimax import enumerate_boards
from tools.mixed_boss_counter_minimax import (
    minimum_attacks as agent44_mixed,
    forced_first_source as agent44_first,
)
from tools.mixed_gust_prize_minimax import (
    mixed_gust_attacks as agent20_mixed,
)
from tools.target_restricted_gust_minimax import (
    PRIZE_VALUE, enumerate_typed_boards, minimum_typed_attacks
)
from tools.typed_gust_target_minimax import (
    Target, enumerate_boards as agent44_typed_boards,
    minimum_attacks as agent44_typed,
)


def class_key(target: Target) -> str:
    prefix = "V" if target.is_pokemon_v else "N"
    return prefix + str(target.prizes)


def attack_after_source(active, bench, bosses, catchers,
                        own_prizes, opponent_prizes, target_value, kind):
    """Independent same-target forced source calculation."""
    costs = []
    for i, prize in enumerate(bench):
        if prize != target_value:
            continue
        survivors = tuple(sorted((active,) + bench[:i] + bench[i + 1 :]))
        b = bosses - (kind == "boss")
        c = catchers - (kind == "counter")
        if prize >= own_prizes or not survivors:
            costs.append(1)
        else:
            costs.append(1 + max(
                agent20_mixed(p, survivors[:j] + survivors[j + 1 :],
                              b, c, own_prizes - prize, opponent_prizes)
                for j, p in enumerate(survivors)
            ))
    return min(costs)


def run():
    original_boards = tuple(agent44_typed_boards())
    assert len(original_boards) == 582
    expanded_typed = {
        (a, b) for a, b, _ in enumerate_typed_boards()
    }
    typed_checks = 0
    for active, bench in original_boards:
        key_active = class_key(active)
        key_bench = tuple(sorted(class_key(t) for t in bench))
        assert (key_active, key_bench) in expanded_typed
        for b in range(3):
            for s in range(3):
                actual = minimum_typed_attacks(key_active, key_bench, b, s)
                expected = agent44_typed(active, bench, b, s)
                assert actual == expected, (active, bench, b, s, actual, expected)
                typed_checks += 1
    assert typed_checks == 5238

    mixed_checks = 0
    source_checks = 0
    source_disagreements = Counter()
    expected_source_cost = {
        1: 0,
        2: 0,
        3: 82,
        4: 130,
        5: 162,
    }
    for opponent in range(1, 6):
        strict = 0
        for active, bench, _ in enumerate_boards():
            for b in range(3):
                for c in range(3):
                    our = agent20_mixed(active, bench, b, c, 6, opponent)
                    theirs = agent44_mixed(active, bench, b, c, 6, opponent)
                    assert our == theirs, (opponent, active, bench, b, c)
                    mixed_checks += 1

            for target in sorted(set(bench)):
                bfirst = agent44_first(
                    active, bench, opponent, "boss", target
                )
                cfirst = agent44_first(
                    active, bench, opponent, "counter", target
                )
                independent_b = attack_after_source(
                    active, bench, 1, 1, 6, opponent, target, "boss"
                )
                independent_c = attack_after_source(
                    active, bench, 1, 1, 6, opponent, target, "counter"
                )
                assert (bfirst, cfirst) == (independent_b, independent_c)
                assert cfirst <= bfirst
                strict += cfirst < bfirst
                source_checks += 1
        source_disagreements[opponent] = strict
        assert strict == expected_source_cost[opponent]

    assert mixed_checks == 6570
    assert source_checks == 1460
    print("agent44 vs agent20 typed (Boss/Serena) agreement:",typed_checks)
    print("agent44 vs agent20 mixed (Boss/Counter) agreement:",mixed_checks)
    print("same-target forced source agreement:",source_checks)
    print("Counter-first strictly better by opposing Prizes:",
          dict(source_disagreements))
    print("PASS: 13,268 cross-agent kernel and source-order agreements")


if __name__ == "__main__":
    run()
