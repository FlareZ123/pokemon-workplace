"""Independent physical-draw validation and finite-board census for stochastic escape gust."""
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from itertools import combinations, combinations_with_replacement, product
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.stochastic_escape_gust import expected_attacks


@lru_cache(None)
def physical_order_oracle(active, bench, held_gust, draw_order, escapes, needed=6):
    """Independent min/max recursion with a fully fixed, physically labeled draw order."""
    hand = held_gust + (draw_order[0] == 'G')
    tail = draw_order[1:]
    moves = [(active, bench, hand)]
    if hand:
        for ix, p in enumerate(bench):
            moves.append((p, tuple(sorted(bench[:ix] + bench[ix + 1:] + (active,))), hand - 1))

    attack_counts = []
    for target, rest, hand_after in moves:
        value, hp = target
        if hp == 1:
            if value >= needed or len(rest) == 0:
                attack_counts.append(1)
                continue
            replies = [physical_order_oracle(
                promoted, rest[:ix] + rest[ix + 1:], hand_after,
                tail, escapes, needed - value
            ) for ix, promoted in enumerate(rest)]
        else:
            hit = (value, hp - 1)
            replies = [physical_order_oracle(hit, rest, hand_after, tail, escapes, needed)]
            if escapes:
                replies += [physical_order_oracle(
                    promoted, tuple(sorted(rest[:ix] + rest[ix + 1:] + (hit,))),
                    hand_after, tail, escapes - 1, needed
                ) for ix, promoted in enumerate(rest)]
        attack_counts.append(1 + max(replies))
    return min(attack_counts)


def print_source_checks():
    for set_name, card_id, name, wanted in (
        ('swsh2', 'swsh2-154', "Boss's Orders", "Switch 1 of your opponent's Benched Pokémon"),
        ('sv1', 'sv1-194', 'Switch', 'Switch your Active Pokémon with 1 of your Benched Pokémon'),
    ):
        cards = json.loads((ROOT / 'resources' / 'cards' / 'en' / f'{set_name}.json').read_text(encoding='utf-8'))
        card = next(card for card in cards if card['id'] == card_id)
        assert card['name'] == name and any(wanted in text for text in card['rules'])
        print(f'Bundled source check: {card_id}, {name}: passed')


def witness():
    board = (3, 2), ((3, 2), (3, 2))
    active, bench = board
    assert expected_attacks(active, bench, 0, 0, 12, 0) == 4
    assert expected_attacks(active, bench, 0, 2, 10, 0) == 4
    assert expected_attacks(active, bench, 0, 0, 12, 1) == 5
    assert expected_attacks(active, bench, 0, 1, 11, 1) == Fraction(14, 3)
    assert expected_attacks(active, bench, 0, 2, 10, 1) == Fraction(146, 33)
    assert expected_attacks(active, bench, 0, 2, 10, 2) == Fraction(54, 11)

    outcomes = Counter()
    for positions in combinations(range(12), 2):
        sequence = tuple('G' if i in positions else 'F' for i in range(12))
        answer = physical_order_oracle(active, bench, 0, sequence, 1)
        has_timely_gust = bool(set(positions) & set(range(4)))
        assert answer == (4 if has_timely_gust else 5), positions
        outcomes[(has_timely_gust, answer)] += 1
    assert outcomes == {(True, 4): 38, (False, 5): 28}, outcomes
    weighted_mean = sum(Fraction(number * value, 66) for (_, value), number in outcomes.items())
    assert weighted_mean == expected_attacks(active, bench, 0, 2, 10, 1)
    print('Witness: 0 escapes = 4, one escape + no gust = 5')
    print('Witness: 1 escape + two hidden gusts = 146/33 expected attacks')
    print('Physical-draw oracle: 38 favorable, 28 unfavorable placements among 66; exact agreement')


def census():
    pokemon = tuple(product((1, 3), (1, 2)))
    cases = 0
    changes = Counter()
    became_useful = became_useless = 0
    helpful = Counter()
    for num_pokemon in (2, 3, 4):
        for active in pokemon:
            for bench in combinations_with_replacement(pokemon, num_pokemon - 1):
                if active[0] + sum(p[0] for p in bench) < 6:
                    continue
                cases += 1
                scenarios = {
                    e: [expected_attacks(active, bench, 0, g, 12 - g, e) for g in (0, 1, 2)]
                    for e in (0, 1, 2)
                }
                for escape in (0, 1, 2):
                    values = scenarios[escape]
                    assert values[0] >= values[1] >= values[2]
                    helpful[escape] += values[0] > values[2]
                for g in (0, 1, 2):
                    assert scenarios[0][g] <= scenarios[1][g] <= scenarios[2][g]
                gain0 = scenarios[0][0] - scenarios[0][2]
                gain1 = scenarios[1][0] - scenarios[1][2]
                changes['more' if gain1 > gain0 else 'less' if gain1 < gain0 else 'equal'] += 1
                became_useful += gain0 == 0 and gain1 > 0
                became_useless += gain0 > 0 and gain1 == 0
    assert cases == 96, cases
    assert changes == {'more': 10, 'equal': 49, 'less': 37}, changes
    assert helpful == {0: 66, 1: 58, 2: 53}, helpful
    assert (became_useful, became_useless) == (4, 12)
    print(f'Census: {cases} structural states, 12-card draw pile, 2 Boss')
    print(f'One defender escape changes Boss value: {changes} (larger/equal/smaller)')
    print(f'Value appears in {became_useful} states and disappears in {became_useless} states')
    print(f'Two Boss have positive value for {dict(helpful)} boards at escape budgets 0,1,2')


if __name__ == '__main__':
    print_source_checks()
    witness()
    census()
    print('All exact Fraction regressions and independent oracle tests passed.')
