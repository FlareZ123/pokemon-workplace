"""Finite-deck draw access layered onto adversarial-promotion gust Prize racing.

A normal draw precedes each attack. Opponent promotion is chosen before the
next draw, maximizing the *expected* remaining number of attacks. The attacker
sees its own draw before deciding whether to gust; other Supporters, opponents'
turns, and Prize-card contents are deliberately omitted.
"""
from fractions import Fraction
from functools import lru_cache


@lru_cache(None)
def expected_attacks(
    active: int,
    bench: tuple[int, ...],
    gust_in_hand: int,
    gust_in_deck: int,
    filler_in_deck: int,
    prizes_needed: int = 6,
) -> Fraction:
    """Expected number of attacks to win under optimal timing and adversarial promotion."""
    remaining_draws = gust_in_deck + filler_in_deck
    assert remaining_draws >= len(bench) + 1, "Require a draw for each possible attack"
    expected = Fraction(0)
    if gust_in_deck:
        expected += Fraction(gust_in_deck, remaining_draws) * after_draw(
            active, bench, gust_in_hand + 1, gust_in_deck - 1, filler_in_deck, prizes_needed
        )
    if filler_in_deck:
        expected += Fraction(filler_in_deck, remaining_draws) * after_draw(
            active, bench, gust_in_hand, gust_in_deck, filler_in_deck - 1, prizes_needed
        )
    return expected


@lru_cache(None)
def after_draw(
    active: int,
    bench: tuple[int, ...],
    gust_in_hand: int,
    gust_in_deck: int,
    filler_in_deck: int,
    prizes_needed: int,
) -> Fraction:
    """Player chooses target after seeing draw, before a one-attack turn finishes."""
    actions = [(active, bench, gust_in_hand)]
    if gust_in_hand:
        for i, prize in enumerate(bench):
            survivors = tuple(sorted((active,) + bench[:i] + bench[i + 1 :]))
            actions.append((prize, survivors, gust_in_hand - 1))

    costs = []
    for reward, survivors, next_hand in actions:
        if reward >= prizes_needed or not survivors:
            costs.append(Fraction(1))
            continue
        defending_choice = max(
            expected_attacks(
                promoted,
                survivors[:i] + survivors[i + 1 :],
                next_hand,
                gust_in_deck,
                filler_in_deck,
                prizes_needed - reward,
            )
            for i, promoted in enumerate(survivors)
        )
        costs.append(1 + defending_choice)
    return min(costs)
