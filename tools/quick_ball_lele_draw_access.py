"""Exact post-setup Gladion access through Quick Ball and Tapu Lele-GX.

This extends the opening-only Quick Ball/Tapu Lele model across later random
exposure. It preserves the real sequence opening -> setup role -> Prizes ->
random draws, so a Tapu Lele-GX consumed as the mandatory starting Active does
not regain its hand-to-Bench Wonder Tag trigger.

The card classes are deliberately narrow. Quick Ball's payment uses a binary
DCI-style pool of cards that are acceptable to discard in the modeled state.
The model can optionally allow spare Quick Ball copies to be used as payment.
"""

from __future__ import annotations

from functools import lru_cache
from math import comb
from typing import Literal


AccessMode = Literal["strict", "no_discard", "clean_qb", "ignore_setup"]


def _choose(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    return comb(n, k)


def _allocations(total: int, limits: tuple[int, ...]):
    current = [0] * len(limits)

    def rec(index: int, left: int):
        if index == len(limits) - 1:
            if left <= limits[index]:
                current[index] = left
                yield tuple(current)
            return
        for value in range(min(limits[index], left) + 1):
            current[index] = value
            yield from rec(index + 1, left - value)

    if total < 0:
        return
    yield from rec(0, total)


def draw_window_gladion_access_probability(
    deck_size: int,
    prize_count: int,
    *,
    other_starters: int,
    critical_nonstarter: int,
    rescue_nonstarter: int,
    quick_ball_copies: int,
    disposable_nonstarter: int,
    later_random_draws: int,
    opening_hand_size: int = 7,
    allow_spare_quick_ball_discard: bool = False,
    mode: AccessMode = "strict",
    items_allowed: bool = True,
    abilities_allowed: bool = True,
    bench_available: bool = True,
) -> float:
    """Return P(current-window Gladion access | valid start, critical Prized).

    Exactly one Tapu Lele-GX-like support Basic is modeled. It is setup
    eligible. The relevant access modes are nested counterfactuals:

    strict:
        Quick Ball needs a disposable card, Tapu Lele-GX in deck, and an
        unprized Gladion in deck.
    no_discard:
        Same chain, but Quick Ball's discard payment is ignored.
    clean_qb:
        Each accessible Quick Ball is treated as a direct Gladion out. This
        keeps Item permission but removes the intermediate Tapu Lele-GX,
        Ability, Bench, and discard requirements from the Quick Ball route.
    ignore_setup:
        Same as strict, but a Tapu Lele-GX used as the only setup starter is
        incorrectly treated as though it remained in hand. This isolates
        setup-trigger loss.
    """
    if mode not in {"strict", "no_discard", "clean_qb", "ignore_setup"}:
        raise ValueError(f"unsupported mode: {mode}")

    support_basic = 1
    filler_nonstarter = (
        deck_size
        - support_basic
        - other_starters
        - critical_nonstarter
        - rescue_nonstarter
        - quick_ball_copies
        - disposable_nonstarter
    )
    if min(
        other_starters,
        critical_nonstarter,
        rescue_nonstarter,
        quick_ball_copies,
        disposable_nonstarter,
        filler_nonstarter,
    ) < 0:
        raise ValueError("modeled card counts must be non-negative and fit in deck")
    if not 0 <= prize_count <= deck_size:
        raise ValueError("prize_count must fit in deck")
    if not 0 <= opening_hand_size <= deck_size - prize_count:
        raise ValueError("opening hand must fit before Prize cards")
    post_prize_deck = deck_size - opening_hand_size - prize_count
    if not 0 <= later_random_draws <= post_prize_deck:
        raise ValueError("later_random_draws must fit in the post-Prize deck")

    # critical, rescue, Tapu Lele-GX, Quick Ball, disposable,
    # other setup starter, filler.
    sizes = (
        critical_nonstarter,
        rescue_nonstarter,
        support_basic,
        quick_ball_copies,
        disposable_nonstarter,
        other_starters,
        filler_nonstarter,
    )
    total_starters = support_basic + other_starters
    opening_denominator = _choose(deck_size, opening_hand_size)
    accepted_openings = (
        opening_denominator
        - _choose(deck_size - total_starters, opening_hand_size)
    )
    if accepted_openings == 0:
        raise ValueError("valid opening has zero probability")
    opening_acceptance = accepted_openings / opening_denominator
    prize_denominator = _choose(deck_size - opening_hand_size, prize_count)
    draw_denominator = _choose(post_prize_deck, later_random_draws)

    @lru_cache(maxsize=None)
    def draw_success_probability(
        rescue_remaining: int,
        support_remaining: int,
        quick_ball_remaining: int,
        disposable_remaining: int,
        other_remaining: int,
        rescue_in_hand: int,
        support_preserved: int,
        quick_ball_in_hand: int,
        disposable_in_hand: int,
    ) -> float:
        success_ways = 0
        limits = (
            rescue_remaining,
            support_remaining,
            quick_ball_remaining,
            disposable_remaining,
            other_remaining,
        )
        for drawn in _allocations(later_random_draws, limits):
            (
                rescue_drawn,
                support_drawn,
                quick_ball_drawn,
                disposable_drawn,
                other_drawn,
            ) = drawn
            ways = (
                _choose(rescue_remaining, rescue_drawn)
                * _choose(support_remaining, support_drawn)
                * _choose(quick_ball_remaining, quick_ball_drawn)
                * _choose(disposable_remaining, disposable_drawn)
                * _choose(other_remaining, other_drawn)
            )
            if ways == 0:
                continue

            rescue_hand = rescue_in_hand + rescue_drawn
            rescue_deck = rescue_remaining - rescue_drawn
            support_hand = support_preserved + support_drawn
            support_deck = support_remaining - support_drawn
            quick_ball_hand = quick_ball_in_hand + quick_ball_drawn
            disposable_hand = disposable_in_hand + disposable_drawn
            if allow_spare_quick_ball_discard:
                disposable_hand += max(0, quick_ball_hand - 1)

            direct_rescue = rescue_hand >= 1
            support_line = (
                support_hand >= 1
                and rescue_deck >= 1
                and abilities_allowed
                and bench_available
            )

            if mode == "clean_qb":
                quick_ball_line = (
                    quick_ball_hand >= 1
                    and rescue_deck >= 1
                    and items_allowed
                )
            else:
                quick_ball_line = (
                    quick_ball_hand >= 1
                    and support_deck >= 1
                    and rescue_deck >= 1
                    and items_allowed
                    and abilities_allowed
                    and bench_available
                )
                if mode in {"strict", "ignore_setup"}:
                    quick_ball_line = quick_ball_line and disposable_hand >= 1

            if direct_rescue or support_line or quick_ball_line:
                success_ways += ways

        return success_ways / draw_denominator

    critical_prize_mass = 0.0
    access_mass = 0.0

    for opening in _allocations(opening_hand_size, sizes):
        (
            critical_opening,
            rescue_opening,
            support_opening,
            quick_ball_opening,
            disposable_opening,
            other_starter_opening,
            filler_opening,
        ) = opening
        if support_opening + other_starter_opening == 0:
            continue

        opening_ways = (
            _choose(critical_nonstarter, critical_opening)
            * _choose(rescue_nonstarter, rescue_opening)
            * _choose(support_basic, support_opening)
            * _choose(quick_ball_copies, quick_ball_opening)
            * _choose(disposable_nonstarter, disposable_opening)
            * _choose(other_starters, other_starter_opening)
            * _choose(filler_nonstarter, filler_opening)
        )
        if opening_ways == 0:
            continue
        opening_mass = opening_ways / opening_denominator / opening_acceptance
        remaining = tuple(size - count for size, count in zip(sizes, opening))

        if mode == "ignore_setup":
            support_preserved = int(support_opening == 1)
        else:
            support_preserved = int(
                support_opening == 1 and other_starter_opening >= 1
            )

        # After setup, ordinary starters and filler are strategically identical
        # for this access question, so merge them for Prize and draw sampling.
        prize_limits = (
            remaining[0],
            remaining[1],
            remaining[2],
            remaining[3],
            remaining[4],
            remaining[5] + remaining[6],
        )
        for prizes in _allocations(prize_count, prize_limits):
            (
                critical_prized,
                rescue_prized,
                support_prized,
                quick_ball_prized,
                disposable_prized,
                other_prized,
            ) = prizes
            if critical_prized == 0:
                continue

            prize_ways = (
                _choose(remaining[0], critical_prized)
                * _choose(remaining[1], rescue_prized)
                * _choose(remaining[2], support_prized)
                * _choose(remaining[3], quick_ball_prized)
                * _choose(remaining[4], disposable_prized)
                * _choose(remaining[5] + remaining[6], other_prized)
            )
            if prize_ways == 0:
                continue

            state_mass = opening_mass * prize_ways / prize_denominator
            critical_prize_mass += state_mass

            rescue_remaining = remaining[1] - rescue_prized
            support_remaining = remaining[2] - support_prized
            quick_ball_remaining = remaining[3] - quick_ball_prized
            disposable_remaining = remaining[4] - disposable_prized
            other_remaining = post_prize_deck - (
                rescue_remaining
                + support_remaining
                + quick_ball_remaining
                + disposable_remaining
            )

            access_mass += state_mass * draw_success_probability(
                rescue_remaining,
                support_remaining,
                quick_ball_remaining,
                disposable_remaining,
                other_remaining,
                rescue_opening,
                support_preserved,
                quick_ball_opening,
                disposable_opening,
            )

    if critical_prize_mass == 0.0:
        return 0.0
    return access_mass / critical_prize_mass
