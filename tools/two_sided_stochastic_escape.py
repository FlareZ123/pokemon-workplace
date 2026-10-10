"""Two-player finite-deck attack and Switch response model.

Attacker draws before each attack and may play one Boss gust from hand. The
opponent has a separate random draw on each intervening turn, then can play
one held Switch Item to abandon the Active. Post-KO promotion is selected
before the opponent's draw. There is no normal retreat, damage from the
opponent, or alternative draw/search action.
"""
from fractions import Fraction
from functools import lru_cache

Pokemon = tuple[int, int]


@lru_cache(None)
def attacker_draw(
    active: Pokemon, bench: tuple[Pokemon, ...],
    boss_hand: int, boss_deck: int, attacker_filler: int,
    switch_hand: int, switch_deck: int, defender_filler: int,
    needed: int = 6, item_legal: bool = True,
) -> Fraction:
    attacker_size = boss_deck + attacker_filler
    assert attacker_size >= active[1] + sum(x[1] for x in bench)
    assert switch_deck + defender_filler >= active[1] + sum(x[1] for x in bench) - 1
    val = Fraction()
    if boss_deck:
        val += Fraction(boss_deck, attacker_size) * attacker_act(
            active, bench, boss_hand + 1, boss_deck - 1, attacker_filler,
            switch_hand, switch_deck, defender_filler, needed, item_legal)
    if attacker_filler:
        val += Fraction(attacker_filler, attacker_size) * attacker_act(
            active, bench, boss_hand, boss_deck, attacker_filler - 1,
            switch_hand, switch_deck, defender_filler, needed, item_legal)
    return val


@lru_cache(None)
def attacker_act(
    active, bench, boss_hand, boss_deck, attacker_filler,
    switch_hand, switch_deck, defender_filler, needed, item_legal,
):
    moves = [(active, bench, boss_hand)]
    if boss_hand:
        for j, target in enumerate(bench):
            moves.append((target, tuple(sorted((active,)+bench[:j]+bench[j+1:])), boss_hand-1))
    outcomes = []
    for (prizes, hp), rest, hand in moves:
        if hp == 1:
            if prizes >= needed or not rest:
                outcomes.append(Fraction(1))
            else:
                # KO promotion occurs immediately, prior to defender's next draw.
                value = max(defender_draw(
                    p, rest[:i]+rest[i+1:], hand, boss_deck,
                    attacker_filler, switch_hand, switch_deck, defender_filler,
                    needed-prizes, item_legal
                ) for i, p in enumerate(rest))
                outcomes.append(1+value)
        else:
            wounded = (prizes, hp-1)
            outcomes.append(1 + defender_draw(
                wounded, rest, hand, boss_deck, attacker_filler,
                switch_hand, switch_deck, defender_filler, needed, item_legal
            ))
    return min(outcomes)


@lru_cache(None)
def defender_draw(
    active, bench, boss_hand, boss_deck, attacker_filler,
    switch_hand, switch_deck, defender_filler, needed, item_legal,
):
    total = switch_deck + defender_filler
    assert total > 0
    out = Fraction()
    if switch_deck:
        out += Fraction(switch_deck,total) * defender_act(
            active,bench,boss_hand,boss_deck,attacker_filler,
            switch_hand+1,switch_deck-1,defender_filler,needed,item_legal)
    if defender_filler:
        out += Fraction(defender_filler,total) * defender_act(
            active,bench,boss_hand,boss_deck,attacker_filler,
            switch_hand,switch_deck,defender_filler-1,needed,item_legal)
    return out


@lru_cache(None)
def defender_act(
    active, bench, boss_hand, boss_deck, attacker_filler,
    switch_hand, switch_deck, defender_filler, needed, item_legal,
):
    vals=[attacker_draw(
        active,bench,boss_hand,boss_deck,attacker_filler,
        switch_hand,switch_deck,defender_filler,needed,item_legal)]
    if item_legal and switch_hand:
        for j, p in enumerate(bench):
            rest=tuple(sorted((active,)+bench[:j]+bench[j+1:]))
            vals.append(attacker_draw(
                p,rest,boss_hand,boss_deck,attacker_filler,
                switch_hand-1,switch_deck,defender_filler,needed,item_legal))
    return max(vals)
