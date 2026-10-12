"""Independent physical move-tree oracle and exact retreat-payment witnesses."""

from collections import deque
from dataclasses import replace
from itertools import combinations, product
from pathlib import Path
import json

from tools.guzma_forced_pivot import best_prizes as abstract_best
from tools.guzma_retreat_payment import Attacker, best_prizes


def oracle(attackers, opponent_prizes, supporter, switch_held=False, items_allowed=True):
    # BFS enumerates the entire finite action sequence space independently of
    # the production model's memoized depth-first search.
    queue = deque([(attackers, 0, 0, False, False, False)])
    seen = set()
    best = 0
    while queue:
        board, own, opp, retreated, supported, switched = queue.popleft()
        key = (board, own, opp, retreated, supported, switched)
        if key in seen:
            continue
        seen.add(key)
        attacker = board[own]
        if attacker.ko_mask & (1 << opp) and sum(attacker.energy_cards) >= attacker.attack_cost:
            best = max(best, opponent_prizes[opp])
        if not retreated and not attacker.retreat_blocked:
            energy = attacker.energy_cards
            for cnt in range(len(energy)+1):
                for ids in combinations(range(len(energy)), cnt):
                    paid = sum(energy[i] for i in ids)
                    if paid < attacker.retreat_cost or any(paid-energy[i]>=attacker.retreat_cost for i in ids):
                        continue
                    remaining = tuple(e for i, e in enumerate(energy) if i not in ids)
                    new_board = board[:own] + (replace(attacker, energy_cards=remaining),) + board[own+1:]
                    for next_own in range(len(board)):
                        if next_own != own:
                            queue.append((new_board, next_own, opp, True, supported, switched))
        if switch_held and items_allowed and not switched:
            for next_own in range(len(board)):
                if next_own != own:
                    queue.append((board, next_own, opp, retreated, supported, True))
        if not supported and opp == 0:
            own_options = (own,) if supporter == 'boss' else (tuple(i for i in range(len(board)) if i != own) or (own,))
            for next_own in own_options:
                queue.append((board, next_own, 1, retreated, True, switched))
    return best


def card_rule(set_code, card_id):
    repo = Path(__file__).resolve().parents[3]
    cards = json.loads((repo/'resources'/'cards'/'en'/f'{set_code}.json').read_text(encoding='utf-8'))
    return ' '.join(next(c for c in cards if c['id']==card_id)['rules'])


def main():
    assert 'Double Colorless Energy provides ColorlessColorless Energy.' in card_rule('sm1','sm1-136')
    assert 'If you do, switch your Active Pokémon' in card_rule('sm3','sm3-115')
    assert "Switch 1 of your opponent's Benched Pokémon" in card_rule('swsh2','swsh2-154')

    # A single two-unit card can pay one retreat, but is discarded whole.
    unready = Attacker(0, 1, 2, ())
    for energy, expected in (((2,), 0), ((1, 1), 3), ((1,), 0)):
        board = (Attacker(2, 1, 1, energy), unready)
        assert best_prizes(board, (1,3), 'guzma')[0] == expected
        assert best_prizes(board, (1,3), 'boss')[0] == 3
        assert oracle(board, (1,3), 'guzma') == expected
        assert best_prizes(board, (1,3), 'guzma', True, True)[0] == 3
        assert best_prizes(board, (1,3), 'guzma', True, False)[0] == expected

    free_bench = (Attacker(2, 1, 1, (2,)), Attacker(0, 1, 0, ()))
    assert best_prizes(free_bench, (1,3), 'guzma')[0] == 3
    assert best_prizes(free_bench, (1,3), 'guzma')[1][1].startswith('retreat')

    # On retreat-prohibited boards with no attack Energy requirements, reduce
    # exactly to the independently validated abstract source-comparison kernel.
    reductions = 0
    for own_size in range(1,4):
        for masks in product(range(4),repeat=own_size):
            board = tuple(Attacker(mask, 0, 1, (), True) for mask in masks)
            for prize in product((1,2,3),repeat=2):
                for supporter in ('boss','guzma'):
                    for item in (False, True):
                        for allowed in (False, True):
                            assert best_prizes(board, prize, supporter, item, allowed)[0] == abstract_best(masks, prize, supporter, item, allowed)[0]
                            reductions += 1

    # Independent BFS vs memoized DFS for 2-attacker physical configurations.
    templates = [Attacker(mask, attack_cost, retreat_cost, energy)
                 for mask in range(4)
                 for attack_cost in (0,1,2)
                 for retreat_cost in (0,1,2)
                 for energy in ((),(1,),(2,),(1,1))]
    checks = 0
    # Deterministic balanced subsample of the complete 144^2 grid.
    for i in range(0,len(templates),7):
        for j in range(0,len(templates),5):
            board = (templates[i],templates[j])
            for source in ('boss','guzma'):
                for item,allowed in ((False,True),(True,True),(True,False)):
                    got = best_prizes(board,(1,3),source,item,allowed)[0]
                    assert got == oracle(board,(1,3),source,item,allowed)
                    checks += 1
    print('Physical Boss/Guzma oracle comparisons:',checks)
    print('Reduction to simple attacker-mask frontier:',reductions)
    print('Single DCE / two Basic retreat-card conservation witnesses passed')


if __name__ == '__main__':
    main()
