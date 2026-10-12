"""Exact cross-check of Guzma's compulsory own pivot versus Boss's Orders."""

from collections import Counter
from itertools import product
from pathlib import Path
import json

from tools.guzma_forced_pivot import best_prizes


def print_rule(set_code: str, card_id: str) -> str:
    path = Path(__file__).resolve().parents[3] / 'resources' / 'cards' / 'en' / f'{set_code}.json'
    cards = json.loads(path.read_text(encoding='utf-8'))
    card = next(c for c in cards if c['id'] == card_id)
    return ' '.join(card['rules'])


def algebra(masks, prizes, supporter, has_item):
    """Independent reachable-attacker formula; no move enumeration."""
    active = masks[0]
    active_reward = prizes[0] if active & 1 else 0
    if has_item:
        return max(prizes[target] for mask in masks for target in (0, 1)
                   if mask & (1 << target)) if any(masks) else 0
    if supporter == 'boss':
        bench_hit = bool(active & 2)
    elif supporter == 'guzma':
        bench_hit = any(mask & 2 for mask in masks[1:]) if len(masks) > 1 else bool(active & 2)
    else:
        bench_hit = False
    return max(active_reward, prizes[1] if bench_hit else 0)


def main():
    guzma = print_rule('sm3', 'sm3-115')
    boss = print_rule('swsh2', 'swsh2-154')
    switch = print_rule('sv1', 'sv1-194')
    assert "If you do, switch your Active Pokémon with 1 of your Benched Pokémon." in guzma
    assert "Switch 1 of your opponent's Benched Pokémon with their Active Pokémon." in boss
    assert "Switch your Active Pokémon with 1 of your Benched Pokémon." in switch

    counted = Counter()
    counts_by_delta = Counter()
    total = 0
    for n in range(1, 7):
        for masks in product(range(4), repeat=n):
            for prizes in product((1, 2, 3), repeat=2):
                results = {}
                for source in ('boss', 'guzma'):
                    ordinary = best_prizes(masks, prizes, source, False, True)[0]
                    item_locked = best_prizes(masks, prizes, source, True, False)[0]
                    item_active = best_prizes(masks, prizes, source, True, True)[0]
                    assert ordinary == item_locked == algebra(masks, prizes, source, False)
                    assert item_active == algebra(masks, prizes, source, True)
                    assert item_active >= ordinary
                    results[source] = ordinary, item_active
                delta = results['guzma'][0] - results['boss'][0]
                category = 'guzma' if delta > 0 else 'boss' if delta < 0 else 'equal'
                counted[(n, category)] += 1
                counts_by_delta[delta] += 1
                assert results['boss'][1] == results['guzma'][1]
                total += 1

    assert total == 49140
    assert [counted[(n, 'boss')] for n in range(1, 7)] == [0, 24, 48, 96, 192, 384]
    assert [counted[(n, 'guzma')] for n in range(1, 7)] == [0, 24, 144, 672, 2880, 11904]
    assert [counted[(n, 'equal')] for n in range(1, 7)] == [36, 96, 384, 1536, 6144, 24576]
    assert best_prizes((2, 0), (1, 3), 'boss')[0] == 3
    assert best_prizes((2, 0), (1, 3), 'guzma')[0] == 0
    assert best_prizes((0, 2), (1, 3), 'boss')[0] == 0
    assert best_prizes((0, 2), (1, 3), 'guzma')[0] == 3
    for n in range(1, 7):
        print(f'{n} own Pokemon | Boss better: {counted[(n, "boss")]:5} | '
              f'Guzma better: {counted[(n, "guzma")]:5} | '
              f'equal: {counted[(n, "equal")]:5}')
    print('Total:', total, 'one-turn board/payoff checks; Prize delta:', dict(sorted(counts_by_delta.items())))


if __name__ == '__main__':
    main()
