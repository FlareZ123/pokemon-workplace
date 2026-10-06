"""Exact first-rescue access with clean same-window search outs.

A "clean direct out" is an abstract non-starter card already assumed to be
playable before the Supporter window. If seen, it can search one Gladion-like
rescue card from the deck into the hand. The model does not assign this status
to any concrete card automatically because real connectors have costs,
conditions, locks, and opportunity costs.

The process is literal setup order:
1. accept an opening hand containing at least one setup-eligible starter;
2. set Prize cards from the remaining deck;
3. expose additional non-Prize cards up to cards_seen;
4. ask whether at least one rescue Supporter is now playable from hand.

Results can be conditioned on at least one modeled critical singleton being
Prized, which is the state where Prize rescue is relevant.
"""

from __future__ import annotations

from itertools import product
from math import comb


def _choose(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    return comb(n, k)


def first_rescue_access_probability(
    deck_size: int,
    prize_count: int,
    *,
    starter_cards: int,
    critical_nonstarter: int,
    rescue_nonstarter: int,
    direct_out_nonstarter: int,
    cards_seen: int,
    opening_hand_size: int = 7,
    condition_on_critical_prized: bool = True,
) -> float:
    """Return exact probability of at least one current-window rescue access.

    Access succeeds if:
    * at least one rescue copy has been exposed into hand, or
    * at least one clean direct out has been exposed and at least one rescue copy
      remains in the searchable deck.

    All modeled critical, rescue, and direct-out cards are non-starters.
    """
    if deck_size <= 0:
        raise ValueError("deck_size must be positive")
    if not 0 <= prize_count <= deck_size:
        raise ValueError("prize_count must fit in the deck")
    if not 0 <= opening_hand_size <= deck_size - prize_count:
        raise ValueError("opening_hand_size must fit before Prize cards")
    if not opening_hand_size <= cards_seen <= deck_size - prize_count:
        raise ValueError("cards_seen must include the opening hand and exclude Prize cards")
    if not 0 <= starter_cards <= deck_size:
        raise ValueError("starter_cards must fit in the deck")
    if min(critical_nonstarter, rescue_nonstarter, direct_out_nonstarter) < 0:
        raise ValueError("modeled card counts must be non-negative")

    filler_nonstarter = (
        deck_size
        - starter_cards
        - critical_nonstarter
        - rescue_nonstarter
        - direct_out_nonstarter
    )
    if filler_nonstarter < 0:
        raise ValueError("modeled card counts exceed deck size")
    if starter_cards == 0:
        raise ValueError("valid-start conditioning requires at least one starter")

    # Category order: critical, rescue, direct out, starter filler, non-starter filler.
    sizes = (
        critical_nonstarter,
        rescue_nonstarter,
        direct_out_nonstarter,
        starter_cards,
        filler_nonstarter,
    )

    opening_denominator = _choose(deck_size, opening_hand_size)
    opening_acceptance = 1.0 - _choose(
        deck_size - starter_cards, opening_hand_size
    ) / opening_denominator
    if opening_acceptance == 0.0:
        raise ValueError("valid opening has zero probability")

    extra_seen = cards_seen - opening_hand_size
    numerator = 0.0
    conditioning_mass = 0.0

    opening_ranges = [
        range(min(size, opening_hand_size) + 1)
        for size in sizes
    ]
    for opening_counts in product(*opening_ranges):
        if sum(opening_counts) != opening_hand_size:
            continue
        if opening_counts[3] == 0:
            continue

        opening_ways = 1
        for size, count in zip(sizes, opening_counts):
            opening_ways *= _choose(size, count)
        if opening_ways == 0:
            continue

        opening_mass = (
            opening_ways / opening_denominator / opening_acceptance
        )
        after_opening = tuple(
            size - count for size, count in zip(sizes, opening_counts)
        )

        prize_denominator = _choose(
            deck_size - opening_hand_size, prize_count
        )
        prize_ranges = [
            range(min(size, prize_count) + 1)
            for size in after_opening
        ]
        for prize_counts in product(*prize_ranges):
            if sum(prize_counts) != prize_count:
                continue
            if condition_on_critical_prized and prize_counts[0] == 0:
                continue

            prize_ways = 1
            for size, count in zip(after_opening, prize_counts):
                prize_ways *= _choose(size, count)
            if prize_ways == 0:
                continue

            state_mass = (
                opening_mass * prize_ways / prize_denominator
            )
            conditioning_mass += state_mass

            after_prizes = tuple(
                size - count
                for size, count in zip(after_opening, prize_counts)
            )

            if extra_seen == 0:
                rescue_seen = opening_counts[1]
                outs_seen = opening_counts[2]
                rescue_in_deck = after_prizes[1]
                if rescue_seen > 0 or (
                    outs_seen > 0 and rescue_in_deck > 0
                ):
                    numerator += state_mass
                continue

            draw_denominator = _choose(
                deck_size - opening_hand_size - prize_count,
                extra_seen,
            )
            draw_ranges = [
                range(min(size, extra_seen) + 1)
                for size in after_prizes
            ]
            for draw_counts in product(*draw_ranges):
                if sum(draw_counts) != extra_seen:
                    continue

                draw_ways = 1
                for size, count in zip(after_prizes, draw_counts):
                    draw_ways *= _choose(size, count)
                if draw_ways == 0:
                    continue

                rescue_seen = opening_counts[1] + draw_counts[1]
                outs_seen = opening_counts[2] + draw_counts[2]
                rescue_in_deck = after_prizes[1] - draw_counts[1]
                if rescue_seen > 0 or (
                    outs_seen > 0 and rescue_in_deck > 0
                ):
                    numerator += (
                        state_mass * draw_ways / draw_denominator
                    )

    if conditioning_mass == 0.0:
        return 0.0
    return numerator / conditioning_mass


def critical_prized_probability_given_valid_start(
    deck_size: int,
    prize_count: int,
    *,
    starter_cards: int,
    critical_nonstarter: int,
    opening_hand_size: int = 7,
) -> float:
    """Return P(any modeled non-starter critical is Prized | valid opening)."""
    return _critical_prized_probability_direct(
        deck_size,
        prize_count,
        starter_cards=starter_cards,
        critical_nonstarter=critical_nonstarter,
        opening_hand_size=opening_hand_size,
    )


def _critical_prized_probability_direct(
    deck_size: int,
    prize_count: int,
    *,
    starter_cards: int,
    critical_nonstarter: int,
    opening_hand_size: int,
) -> float:
    """Exact marginal used by the public helper."""
    filler_nonstarter = deck_size - starter_cards - critical_nonstarter
    if filler_nonstarter < 0:
        raise ValueError("modeled card counts exceed deck size")

    sizes = (critical_nonstarter, starter_cards, filler_nonstarter)
    opening_denominator = _choose(deck_size, opening_hand_size)
    opening_acceptance = 1.0 - _choose(
        deck_size - starter_cards, opening_hand_size
    ) / opening_denominator
    if opening_acceptance == 0.0:
        raise ValueError("valid opening has zero probability")

    probability = 0.0
    for opening_counts in product(*[
        range(min(size, opening_hand_size) + 1)
        for size in sizes
    ]):
        if sum(opening_counts) != opening_hand_size:
            continue
        if opening_counts[1] == 0:
            continue

        opening_ways = 1
        for size, count in zip(sizes, opening_counts):
            opening_ways *= _choose(size, count)
        opening_mass = (
            opening_ways / opening_denominator / opening_acceptance
        )

        remaining = tuple(
            size - count for size, count in zip(sizes, opening_counts)
        )
        prize_denominator = _choose(
            deck_size - opening_hand_size, prize_count
        )
        for prize_counts in product(*[
            range(min(size, prize_count) + 1)
            for size in remaining
        ]):
            if sum(prize_counts) != prize_count:
                continue
            if prize_counts[0] == 0:
                continue

            prize_ways = 1
            for size, count in zip(remaining, prize_counts):
                prize_ways *= _choose(size, count)
            probability += (
                opening_mass * prize_ways / prize_denominator
            )

    return probability
