"""Hypergeometric deadline theorem for defender Switch-only, no attacker gust."""
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from itertools import combinations
from math import comb
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.two_sided_stochastic_escape import attacker_draw


def switch_window_formula(hits: int, defender_deck: int, switch_count: int) -> Fraction:
    """Expected attacks for a 3x(3-Prize,h-hits) defender board with no Boss."""
    assert hits >= 1 and defender_deck >= 3 * hits - 1
    assert 0 <= switch_count <= defender_deck
    probability_no_timely_switch = Fraction(
        comb(defender_deck - (2 * hits - 1), switch_count)
        if switch_count <= defender_deck - (2 * hits - 1) else 0,
        comb(defender_deck, switch_count),
    )
    return Fraction(2 * hits) + (hits - 1) * (1 - probability_no_timely_switch)


def verify_dp():
    count = 0
    for hits in range(1, 7):
        for defender_deck in (max(4, 3 * hits), 3 * hits + 4, 3 * hits + 12):
            for switch_count in range(0, 5):
                active = (3, hits)
                bench = (active, active)
                actual = attacker_draw(
                    active, bench, 0, 0, 3 * hits + 4,
                    0, switch_count, defender_deck - switch_count)
                predicted = switch_window_formula(hits, defender_deck, switch_count)
                assert actual == predicted, (hits, defender_deck, switch_count, actual, predicted)
                under_lock = attacker_draw(
                    active, bench, 0, 0, 3 * hits + 4,
                    0, switch_count, defender_deck - switch_count, 6, False)
                assert under_lock == 2 * hits
                count += 1
    assert count == 90
    print(f'Exact DP / closed-form matches: {count}; Item-lock ablation matches all cases')


@lru_cache(None)
def fixed_order_attacks(active: tuple[int, int], bench: tuple[tuple[int, int], ...],
                        held_switches: int, future_switches: tuple[str, ...],
                        needed: int = 6) -> int:
    """Independent full-order physical oracle; the attacker has no gust."""
    reward, hits = active
    if hits == 1:
        if reward >= needed or not bench:
            return 1
        return 1 + max(fixed_order_defense(
            next_active, bench[:i] + bench[i+1:], held_switches,
            future_switches, needed-reward
        ) for i, next_active in enumerate(bench))
    return 1 + fixed_order_defense(
        (reward, hits-1), bench, held_switches, future_switches, needed)


@lru_cache(None)
def fixed_order_defense(active, bench, held_switches, future_switches, needed):
    held_switches += future_switches[0] == 'S'
    tail = future_switches[1:]
    options = [fixed_order_attacks(active, bench, held_switches, tail, needed)]
    if held_switches:
        for i, promoted in enumerate(bench):
            remaining = tuple(sorted((active,) + bench[:i] + bench[i+1:]))
            options.append(fixed_order_attacks(
                promoted, remaining, held_switches-1, tail, needed))
    return max(options)


def physical_oracle():
    cases = 0
    for hits, deck_size in ((2, 10), (3, 11), (4, 14), (5, 17)):
        for switch_count in range(0, 4):
            histogram = Counter()
            for positions in combinations(range(deck_size), switch_count):
                ordered = tuple('S' if i in positions else 'F' for i in range(deck_size))
                attacks = fixed_order_attacks((3, hits), ((3, hits), (3, hits)), 0, ordered)
                assert attacks in (2*hits, 3*hits-1)
                assert (attacks == 3*hits-1) == any(position < 2*hits-1 for position in positions)
                histogram[attacks] += 1
            n = comb(deck_size, switch_count)
            mean = sum(Fraction(k*v,n) for k,v in histogram.items())
            assert mean == switch_window_formula(hits, deck_size, switch_count)
            cases += n
    assert cases == sum(sum(comb(d, s) for s in range(4)) for _, d in
                        ((2, 10), (3, 11), (4, 14), (5, 17))), cases
    print(f'Independent physical-order paths: {cases} across 16 scenarios, exact histogram threshold verified')


def sample_results():
    for hits in (2, 3, 4):
        values = [switch_window_formula(hits, 12 if hits < 4 else 16, s) for s in range(5)]
        print(f'hits={hits}, switch counts 0..4: {values}')
    with (ROOT/'resources'/'cards'/'en'/'sv1.json').open(encoding='utf-8') as file:
        switch = next(c for c in json.load(file) if c['id'] == 'sv1-194')
    assert switch['name'] == 'Switch' and 'Item' in switch['subtypes']
    print('Source type check: Switch sv1-194 is an Item')


if __name__ == '__main__':
    sample_results()
    verify_dp()
    physical_oracle()
    print('All Switch access-window theorem checks passed.')
