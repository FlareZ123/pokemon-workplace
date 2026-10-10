"""Exact Boss-vs-Switch finite-draw race with payable opposing normal Retreat.

The defender draws before choosing its response to an attack, then can stay,
play one held Switch Item (if allowed), or retreat normally by discarding a
minimal legal subset of its Active Pokemon's physical Energy cards. Attack
and attached Energy state persist; the attacker may draw one Boss per turn.
"""
from dataclasses import replace
from fractions import Fraction
from functools import lru_cache
from tools.typed_retreat_gust import Target, retreat_payment_remainders


@lru_cache(None)
def attacker_draw(active: Target, bench: tuple[Target, ...], boss_hand: int,
                  boss_deck: int, attacker_filler: int, switch_hand: int,
                  switch_deck: int, defender_filler: int, needed: int = 6,
                  item_allowed: bool = True) -> Fraction:
    remaining_hits = active.hits + sum(p.hits for p in bench)
    att_size = boss_deck + attacker_filler
    assert att_size >= remaining_hits
    assert switch_deck + defender_filler >= remaining_hits - 1
    total = Fraction()
    if boss_deck:
        total += Fraction(boss_deck, att_size) * attacker_action(
            active, bench, boss_hand + 1, boss_deck - 1, attacker_filler,
            switch_hand, switch_deck, defender_filler, needed, item_allowed)
    if attacker_filler:
        total += Fraction(attacker_filler, att_size) * attacker_action(
            active, bench, boss_hand, boss_deck, attacker_filler - 1,
            switch_hand, switch_deck, defender_filler, needed, item_allowed)
    return total


@lru_cache(None)
def attacker_action(active, bench, boss_hand, boss_deck, attacker_filler,
                    switch_hand, switch_deck, defender_filler, needed, item_allowed):
    moves = [(active, bench, boss_hand)]
    if boss_hand:
        for i, target in enumerate(bench):
            moves.append((target, tuple(sorted((active,)+bench[:i]+bench[i+1:])), boss_hand-1))
    costs = []
    for target, other, held in moves:
        if target.hits == 1:
            if target.prize >= needed or not other:
                costs.append(Fraction(1))
            else:
                costs.append(1 + max(
                    defender_draw(promoted, other[:i]+other[i+1:], held, boss_deck,
                                  attacker_filler, switch_hand, switch_deck,
                                  defender_filler, needed-target.prize, item_allowed)
                    for i, promoted in enumerate(other)
                ))
        else:
            wounded=replace(target, hits=target.hits-1)
            costs.append(1 + defender_draw(
                wounded, other, held, boss_deck, attacker_filler,
                switch_hand, switch_deck, defender_filler, needed, item_allowed))
    return min(costs)


@lru_cache(None)
def defender_draw(active, bench, boss_hand, boss_deck, attacker_filler,
                  switch_hand, switch_deck, defender_filler, needed, item_allowed):
    total = switch_deck + defender_filler
    assert total > 0
    cost = Fraction()
    if switch_deck:
        cost += Fraction(switch_deck, total) * defender_action(
            active, bench, boss_hand, boss_deck, attacker_filler,
            switch_hand+1, switch_deck-1, defender_filler, needed, item_allowed)
    if defender_filler:
        cost += Fraction(defender_filler, total) * defender_action(
            active, bench, boss_hand, boss_deck, attacker_filler,
            switch_hand, switch_deck, defender_filler-1, needed, item_allowed)
    return cost


@lru_cache(None)
def defender_action(active, bench, boss_hand, boss_deck, attacker_filler,
                    switch_hand, switch_deck, defender_filler, needed, item_allowed):
    options=[attacker_draw(active, bench, boss_hand, boss_deck, attacker_filler,
                           switch_hand, switch_deck, defender_filler, needed, item_allowed)]
    for i, promoted in enumerate(bench):
        rest=bench[:i]+bench[i+1:]
        if item_allowed and switch_hand:
            options.append(attacker_draw(
                promoted, tuple(sorted((active,)+rest)), boss_hand, boss_deck,
                attacker_filler, switch_hand-1, switch_deck,
                defender_filler, needed, item_allowed))
        if not active.retreat_blocked:
            for energy_left in retreat_payment_remainders(active.energy_cards, active.retreat_cost):
                departing=replace(active,energy_cards=energy_left)
                options.append(attacker_draw(
                    promoted, tuple(sorted((departing,)+rest)), boss_hand,
                    boss_deck, attacker_filler, switch_hand,
                    switch_deck, defender_filler, needed, item_allowed))
    return max(options)
