"""Exact six-Prize low-reward promotion dominance in a no-gust three-Pokemon endgame."""
from collections import Counter
from fractions import Fraction
from itertools import combinations_with_replacement, product
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.two_sided_stochastic_escape import attacker_draw


def verify_full_census():
    categories = Counter()
    rewards_hits = tuple(product((1, 2, 3), (1, 2, 3)))
    for active in rewards_hits:
        for bench in combinations_with_replacement(rewards_hits, 2):
            world = (active,) + bench
            if sum(reward for reward, _ in world) < 6:
                continue
            counts = tuple(attacker_draw(
                active, bench, 0, 0, 12, 0, switch_count,
                12 - switch_count, 6
            ) for switch_count in range(5))
            assert all(counts[i] <= counts[i + 1] for i in range(4))
            total_hits = sum(hits for _, hits in world)
            categories['boards'] += 1
            if all(reward == 3 for reward, _ in world):
                categories['all_three_prize'] += 1
                if counts[-1] > counts[0]:
                    categories['switch_valuable'] += 1
                else:
                    categories['switch_inert_all_three'] += 1
            else:
                categories['contains_low_prize'] += 1
                assert counts == (Fraction(total_hits),) * 5, (world, counts)
                categories['zero_effect_across_five_budgets'] += 1
    assert categories == {
        'boards': 252,
        'all_three_prize': 18,
        'switch_valuable': 9,
        'switch_inert_all_three': 9,
        'contains_low_prize': 234,
        'zero_effect_across_five_budgets': 234,
    }, categories
    print(f'Full 252-board exact census: {dict(categories)}')


def exhaustive_survival_argument():
    cases = 0
    for active_reward, bench1_reward, bench2_reward in product(range(1, 4), repeat=3):
        if active_reward == bench1_reward == bench2_reward == 3:
            continue
        choices = [active_reward + bench1_reward, active_reward + bench2_reward]
        assert min(choices) < 6
        cases += 1
    assert cases == 26
    print('Independent proof check: all 26 reward triples with a low-Prize member admit a <6 first-two-KO promotion')


def defender_switch_counterexample():
    active = (3, 2)
    bench = ((3, 2), (3, 2))
    no_switch = attacker_draw(active, bench, 0, 0, 12, 0, 0, 12)
    one_switch = attacker_draw(active, bench, 0, 0, 12, 0, 1, 11)
    assert (no_switch, one_switch) == (Fraction(4), Fraction(17, 4))
    bench_low = ((2, 2), (3, 2))
    for copies in range(5):
        assert attacker_draw(active, bench_low, 0, 0, 12,
                             0, copies, 12 - copies) == 6
    print('Constructive boundary: all-three-Prize board 4->17/4, lower-Bench-Prize board stays 6')


if __name__ == '__main__':
    exhaustive_survival_argument()
    verify_full_census()
    defender_switch_counterexample()
    print('All low-Prize escape dominance tests passed.')
