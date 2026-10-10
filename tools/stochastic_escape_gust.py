"""Finite-deck gust timing against adversarial, limited defender escape.

An attacker draws once before each attack. A gust drawn this turn can target
one Benched Pokemon; its use consumes one copy in hand. One attack deals one
unit of damage, and hits remaining persist through subsequent switches.
Between unsuccessful (non-KO) attacks the defender can spend one escape token
to promote any Benched Pokemon, or leave the target Active. After a KO the
defender promotes one surviving Pokemon without spending an escape token.
Other turn actions, resources, Prize draws, and attacker vulnerability omitted.
"""
from fractions import Fraction
from functools import lru_cache

Pokemon = tuple[int, int]  # (Prize reward, hits until KO)


@lru_cache(None)
def expected_attacks(
    active: Pokemon,
    bench: tuple[Pokemon, ...],
    gust_hand: int,
    gust_deck: int,
    filler_deck: int,
    escapes: int,
    prizes_needed: int = 6,
) -> Fraction:
    """Minimum expected attacks, with worst-case switching and promotion."""
    assert gust_hand >= 0 and gust_deck >= 0 and filler_deck >= 0
    assert escapes >= 0 and prizes_needed > 0
    count = gust_deck + filler_deck
    assert count >= active[1] + sum(hits for _, hits in bench), "Need one normal draw per possible attack"
    out = Fraction()
    if gust_deck:
        out += Fraction(gust_deck, count) * after_draw(
            active, bench, gust_hand + 1, gust_deck - 1, filler_deck, escapes, prizes_needed
        )
    if filler_deck:
        out += Fraction(filler_deck, count) * after_draw(
            active, bench, gust_hand, gust_deck, filler_deck - 1, escapes, prizes_needed
        )
    return out


@lru_cache(None)
def after_draw(
    active: Pokemon,
    bench: tuple[Pokemon, ...],
    gust_hand: int,
    gust_deck: int,
    filler_deck: int,
    escapes: int,
    prizes_needed: int,
) -> Fraction:
    actions = [(active, bench, gust_hand)]
    if gust_hand:
        for index, target in enumerate(bench):
            survivors = tuple(sorted((active,) + bench[:index] + bench[index + 1 :]))
            actions.append((target, survivors, gust_hand - 1))

    values = []
    for (reward, hits), survivors, hand_left in actions:
        if hits == 1:
            if reward >= prizes_needed or not survivors:
                values.append(Fraction(1))
                continue
            values.append(1 + max(
                expected_attacks(p, survivors[:i] + survivors[i + 1 :],
                                 hand_left, gust_deck, filler_deck, escapes,
                                 prizes_needed - reward)
                for i, p in enumerate(survivors)
            ))
        else:
            wounded = (reward, hits - 1)
            choices = [expected_attacks(wounded, survivors, hand_left,
                                        gust_deck, filler_deck, escapes, prizes_needed)]
            if escapes:
                for i, promoted in enumerate(survivors):
                    rest = tuple(sorted((wounded,) + survivors[:i] + survivors[i + 1 :]))
                    choices.append(expected_attacks(promoted, rest, hand_left,
                                                    gust_deck, filler_deck, escapes - 1,
                                                    prizes_needed))
            values.append(1 + max(choices))
    return min(values)
