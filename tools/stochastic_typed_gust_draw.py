"""Exact finite-deck draw timing for two heterogeneous gust cards.

A normal draw occurs before each attack. Boss and one other gust begin hidden
in the draw pile with F filler cards. The other gust is 'counter', 'serena', or
a second unrestricted 'boss'. Defender promotes before the next draw.
Card access is modeled openly to the adversarial future-policy oracle.
"""
from fractions import Fraction
from functools import lru_cache

from tools.target_restricted_gust_minimax import PRIZE_VALUE


@lru_cache(None)
def expected_attacks(
    active: str,
    bench: tuple[str, ...],
    boss_hand: int,
    other_hand: int,
    boss_deck: int,
    other_deck: int,
    filler_deck: int,
    prizes_needed: int,
    opponent_prizes: int,
    other_kind: str,
) -> Fraction:
    """Optimal expected attacks with one public draw before the attack turn."""
    if prizes_needed <= 0:
        return Fraction(0)
    if not bench:
        return Fraction(1)
    remaining = boss_deck + other_deck + filler_deck
    assert remaining >= len(bench) + 1, "require a draw every possible turn"

    value = Fraction(0)
    if boss_deck:
        value += Fraction(boss_deck, remaining) * after_draw(
            active, bench, boss_hand + 1, other_hand,
            boss_deck - 1, other_deck, filler_deck,
            prizes_needed, opponent_prizes, other_kind
        )
    if other_deck:
        value += Fraction(other_deck, remaining) * after_draw(
            active, bench, boss_hand, other_hand + 1,
            boss_deck, other_deck - 1, filler_deck,
            prizes_needed, opponent_prizes, other_kind
        )
    if filler_deck:
        value += Fraction(filler_deck, remaining) * after_draw(
            active, bench, boss_hand, other_hand,
            boss_deck, other_deck, filler_deck - 1,
            prizes_needed, opponent_prizes, other_kind
        )
    return value


@lru_cache(None)
def after_draw(
    active: str,
    bench: tuple[str, ...],
    boss_hand: int,
    other_hand: int,
    boss_deck: int,
    other_deck: int,
    filler_deck: int,
    prizes_needed: int,
    opponent_prizes: int,
    other_kind: str,
) -> Fraction:
    """Choose an attack target after observing the current drawn card."""
    moves = [(active, bench, boss_hand, other_hand)]
    for i, target in enumerate(bench):
        survivors = tuple(sorted((active,) + bench[:i] + bench[i + 1 :]))
        if boss_hand:
            moves.append((target, survivors, boss_hand - 1, other_hand))
        other_legal = (
            other_kind == "boss"
            or (other_kind == "serena" and target.startswith("V"))
            or (other_kind == "counter" and prizes_needed > opponent_prizes)
        )
        if other_hand and other_legal:
            moves.append((target, survivors, boss_hand, other_hand - 1))

    values = []
    for target, survivors, b, other in moves:
        if PRIZE_VALUE[target] >= prizes_needed or not survivors:
            values.append(Fraction(1))
        else:
            values.append(
                1 + max(
                    expected_attacks(
                        p, survivors[:i] + survivors[i + 1 :],
                        b, other, boss_deck, other_deck, filler_deck,
                        prizes_needed - PRIZE_VALUE[target],
                        opponent_prizes, other_kind
                    )
                    for i, p in enumerate(survivors)
                )
            )
    return min(values)
