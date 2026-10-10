"""Exact two-deck Bellman validations, closed-form theorem and physical oracle."""
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

BOARD = ((3, 2), ((3, 2), (3, 2)))


@lru_cache(None)
def known_attacker_turn(active, bench, boss_hand, boss_order, switch_hand, switch_order, needed):
    boss_hand += boss_order[0] == 'G'
    boss_order = boss_order[1:]
    attacks = [(active, bench, boss_hand)]
    if boss_hand:
        for i, target in enumerate(bench):
            attacks.append((target, tuple(sorted((active,) + bench[:i] + bench[i + 1:])), boss_hand - 1))
    costs = []
    for (reward, hp), rest, held in attacks:
        if hp == 1:
            if reward >= needed or not rest:
                costs.append(1)
            else:
                costs.append(1 + max(known_defender_turn(
                    p, rest[:i] + rest[i + 1:], held, boss_order, switch_hand, switch_order, needed - reward
                ) for i, p in enumerate(rest)))
        else:
            costs.append(1 + known_defender_turn(
                (reward, hp - 1), rest, held, boss_order, switch_hand, switch_order, needed
            ))
    return min(costs)


@lru_cache(None)
def known_defender_turn(active, bench, boss_hand, boss_order, switch_hand, switch_order, needed):
    switch_hand += switch_order[0] == 'S'
    switch_order = switch_order[1:]
    continuations = [known_attacker_turn(
        active, bench, boss_hand, boss_order, switch_hand, switch_order, needed
    )]
    if switch_hand:
        for i, promoted in enumerate(bench):
            other = tuple(sorted((active,) + bench[:i] + bench[i + 1:]))
            continuations.append(known_attacker_turn(
                promoted, other, boss_hand, boss_order, switch_hand - 1, switch_order, needed
            ))
    return max(continuations)


def verify_card_sources():
    for set_name, identifier, name, subtype in (
        ('swsh2', 'swsh2-154', "Boss's Orders", 'Supporter'),
        ('sv1', 'sv1-194', 'Switch', 'Item'),
    ):
        cards = json.loads((ROOT / 'resources' / 'cards' / 'en' / f'{set_name}.json').read_text(encoding='utf8'))
        card = next(card for card in cards if card['id'] == identifier)
        assert card['name'] == name and subtype in card['subtypes']
    print('Both source card categories confirmed from bundled BW-onward card data.')


def closed_form():
    active, bench = BOARD
    checked = 0
    for attacker_size in range(6, 15):
        for defender_size in range(5, 15):
            for bosses in range(5):
                exact = attacker_draw(
                    active, bench, 0, bosses, attacker_size - bosses,
                    0, 1, defender_size - 1)
                miss = Fraction(comb(attacker_size - 4, bosses) if bosses <= attacker_size - 4 else 0,
                                comb(attacker_size, bosses))
                expected = 4 + Fraction(3, defender_size) * miss
                assert exact == expected, (attacker_size, defender_size, bosses, exact, expected)
                checked += 1
    assert checked == 450
    assert attacker_draw(active, bench, 0, 0, 12, 0, 1, 11) == Fraction(17, 4)
    assert attacker_draw(active, bench, 0, 1, 11, 0, 1, 11) == Fraction(25, 6)
    assert attacker_draw(active, bench, 0, 2, 10, 0, 1, 11) == Fraction(271, 66)
    for bosses in range(3):
        for switches in range(3):
            assert attacker_draw(active, bench, 0, bosses, 12 - bosses, 0, switches, 12 - switches,
                                 6, False) == 4
    print(f'Closed form verified in {checked} size/Boss configurations; Item lock ablation passed.')


def physical_order_oracle():
    active, bench = BOARD
    outcomes = Counter()
    for boss_positions in combinations(range(12), 2):
        boss_deck = tuple('G' if i in boss_positions else 'F' for i in range(12))
        for switch_position in range(12):
            switch_deck = tuple('S' if i == switch_position else 'F' for i in range(12))
            value = known_attacker_turn(active, bench, 0, boss_deck, 0, switch_deck, 6)
            assert value == (5 if switch_position < 3 and not any(i < 4 for i in boss_positions) else 4)
            outcomes[value] += 1
    assert outcomes == {4: 708, 5: 84}
    mean = sum(Fraction(attacks * count, 792) for attacks, count in outcomes.items())
    assert mean == Fraction(271, 66)
    assert mean == attacker_draw(active, bench, 0, 2, 10, 0, 1, 11)
    print(f'Independent paired-deck order enumeration: {dict(outcomes)}, mean {mean}')


if __name__ == '__main__':
    verify_card_sources()
    closed_form()
    physical_order_oracle()
    print('All two-sided stochastic escape assertions passed.')
