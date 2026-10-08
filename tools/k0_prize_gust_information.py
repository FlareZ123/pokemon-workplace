"""Exact unseen-zone K0 belief policy for a gust-fueled six-Prize endgame.

Before the first deck search, a player knows Boss cards in hand but does not
know how many remain face down as Prize cards. For a uniformly shuffled
remaining deck+Prizes, the sufficient statistic is the total number of
unseen Boss cards, together with the sizes of both zones.

Each turn draws from the deck; a KO takes random Prizes into hand. The player
observes each new hand card before their next strategic decision, whereas the
defender promotes with only the *distribution* of hidden Prize identities.

This is a companion to prize_refill_gust.py, which conditions each decision
on K1 exact Prize composition inferred from deck inspection.
"""
from fractions import Fraction
from functools import lru_cache
from math import comb


@lru_cache(None)
def minimum_expected_attacks(
    active: int,
    bench: tuple[int, ...],
    hand_boss: int,
    unseen_boss: int,
    deck_size: int,
    prize_size: int,
    recover_prize_cards: bool = True,
) -> Fraction:
    """Value before the current turn's mandatory natural card draw."""
    total_unknown = deck_size + prize_size
    if deck_size <= 0:
        raise ValueError("Insufficient deck to perform the next natural draw")

    result = Fraction()
    if unseen_boss:
        result += Fraction(unseen_boss, total_unknown) * minimum_after_draw(
            active, bench, hand_boss + 1, unseen_boss - 1,
            deck_size - 1, prize_size, recover_prize_cards
        )
    if total_unknown > unseen_boss:
        result += Fraction(total_unknown - unseen_boss, total_unknown) * minimum_after_draw(
            active, bench, hand_boss, unseen_boss,
            deck_size - 1, prize_size, recover_prize_cards
        )
    return result


@lru_cache(None)
def minimum_after_draw(
    active: int,
    bench: tuple[int, ...],
    hand_boss: int,
    unseen_boss: int,
    deck_size: int,
    prize_size: int,
    recover_prize_cards: bool = True,
) -> Fraction:
    """Player acts after observing this turn's draw, before attacking."""
    return min(
        value for _label, value in first_action_values(
            active, bench, hand_boss, unseen_boss,
            deck_size, prize_size, recover_prize_cards
        )
    )


def first_action_values(
    active: int,
    bench: tuple[int, ...],
    hand_boss: int,
    unseen_boss: int,
    deck_size: int,
    prize_size: int,
    recover_prize_cards: bool = True,
) -> tuple[tuple[str, Fraction], ...]:
    """Action-conditioned exact values, retaining the target choice."""
    actions = [("attack_active", active, bench, hand_boss)]
    if hand_boss:
        for i, reward in enumerate(bench):
            survivors = tuple(sorted((active,) + bench[:i] + bench[i + 1 :]))
            actions.append((f"gust_{reward}", reward, survivors, hand_boss - 1))

    values: list[tuple[str, Fraction]] = []
    for label, reward, survivors, remaining_hand in actions:
        if reward >= prize_size or not survivors:
            values.append((label, Fraction(1)))
            continue

        total_unknown = deck_size + prize_size
        outcomes: list[tuple[Fraction, tuple[Fraction, ...]]] = []
        for found in range(
            max(0, reward - (total_unknown - unseen_boss)),
            min(unseen_boss, reward) + 1,
        ):
            probability = Fraction(
                comb(unseen_boss, found)
                * comb(total_unknown - unseen_boss, reward - found),
                comb(total_unknown, reward),
            )
            next_hand = remaining_hand + (found if recover_prize_cards else 0)
            promotions = tuple(
                minimum_expected_attacks(
                    promoted, survivors[:j] + survivors[j + 1 :],
                    next_hand, unseen_boss - found,
                    deck_size, prize_size - reward, recover_prize_cards
                )
                for j, promoted in enumerate(survivors)
            )
            outcomes.append((probability, promotions))

        # Opponent sees the board and public Prize count, but not new
        # privately observed Prize identities. Its promotion decision
        # cannot be made contingent on the hidden 'found' value.
        future = max(
            sum((chance * choices[j] for chance, choices in outcomes), Fraction())
            for j in range(len(survivors))
        )
        values.append((label, Fraction(1) + future))
    return tuple(values)


def expected_opening_deal_attacks(
    boss_copies: int,
    active: int,
    bench: tuple[int, ...],
    recover_prize_cards: bool = True,
) -> Fraction:
    """Average over initial seven-card hand, with all other identities unseen."""
    if boss_copies < 0 or boss_copies > 4:
        raise ValueError("This exact study supports 0..4 Boss copies")
    result = Fraction()
    for held in range(boss_copies + 1):
        likelihood = Fraction(
            comb(boss_copies, held) * comb(60 - boss_copies, 7 - held),
            comb(60, 7)
        )
        result += likelihood * minimum_expected_attacks(
            active, bench, held, boss_copies - held,
            47, 6, recover_prize_cards
        )
    return result
