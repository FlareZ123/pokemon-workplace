"""Exact one-draw value of preserving a shared Quick Ball connector.

Compare waiting until a natural draw with eager allocation of one payable
Quick Ball (attacker-first or rescue-first). Priority is predetermined,
not selected using unseen Prize contents. Valid-start/critical-Prized condition.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import comb


def choose(n: int, k: int) -> int:
    return comb(n, k) if 0 <= k <= n else 0


def allocations(total: int, limits: tuple[int, ...]):
    if len(limits) == 1:
        if 0 <= total <= limits[0]:
            yield (total,)
        return
    for count in range(min(total, limits[0]) + 1):
        for rest in allocations(total - count, limits[1:]):
            yield (count,) + rest


@dataclass(frozen=True)
class Result:
    conditioned_mass: float
    wait_joint: float
    eager_attacker_joint: float
    eager_rescue_joint: float
    eager_possible: float


def after_draw_success(
    hand: tuple[int, ...],
    deck: tuple[int, ...],
    preserved_support: bool,
    pre_choice: str | None,
    allow_search_fallback: bool = False,
) -> float:
    """Probability both targets can be completed after one random draw.

    Categories: critical, Gladion, Tapu Lele, attacker, Quick Ball,
    disposable, other.
    """
    h = list(hand)
    d = list(deck)
    attacker_established = h[3] > 0
    rescue_held = h[1] > 0
    if pre_choice is not None:
        assert h[4] > 0 and h[5] > 0
        h[4] -= 1
        h[5] -= 1
        if pre_choice == "attacker":
            if d[3] > 0:
                d[3] -= 1
                attacker_established = True
            elif allow_search_fallback and d[2] > 0 and d[1] > 0:
                # Searching reveals deck contents; choose another live Basic
                # when the original attacker target was Prized.
                d[2] -= 1
                d[1] -= 1
                rescue_held = True
        elif pre_choice == "rescue":
            if d[2] > 0:
                d[2] -= 1
                if d[1] > 0:
                    d[1] -= 1
                    rescue_held = True
            elif allow_search_fallback and not attacker_established and d[3] > 0:
                # K1 fallback after seeing that Tapu Lele-GX is Prized.
                d[3] -= 1
                attacker_established = True

    total = sum(d)
    if not total:
        return float(attacker_established and rescue_held)
    result = 0.0
    for drawn, size in enumerate(d):
        if not size:
            continue
        drawn_deck = d.copy()
        drawn_deck[drawn] -= 1
        balls = h[4] + int(drawn == 4)
        payments = h[5] + int(drawn == 5)
        budget = min(balls, payments)
        a = attacker_established or drawn == 3
        g = rescue_held or drawn == 1 or (
            (preserved_support or drawn == 2) and drawn_deck[1] > 0
        )
        miss_a = not a
        miss_g = not g
        possible = (not miss_a or drawn_deck[3] > 0) and (
            not miss_g or (drawn_deck[2] > 0 and drawn_deck[1] > 0)
        )
        if possible and budget >= int(miss_a) + int(miss_g):
            result += size / total
    return result


def opening_option_probability(
    deck_size: int,
    prize_count: int,
    *,
    other_starters: int,
    attacker_starter_copies: int,
    critical_nonstarter: int,
    rescue_nonstarter: int,
    quick_ball_copies: int,
    disposable_nonstarter: int,
    opening_hand_size: int = 7,
    allow_search_fallback: bool = False,
) -> Result:
    """Exactly enumerate valid opening, six Prizes, and one later draw.

    The eager policies use only observable opening-hand criteria when choosing
    which target to search. The latent Prize draw is integrated analytically.
    """
    filler = (
        deck_size - 1 - other_starters - attacker_starter_copies
        - critical_nonstarter - rescue_nonstarter - quick_ball_copies
        - disposable_nonstarter
    )
    sizes = (
        critical_nonstarter, rescue_nonstarter, 1, attacker_starter_copies,
        quick_ball_copies, disposable_nonstarter, other_starters, filler,
    )
    if (
        deck_size <= 0 or min(sizes) < 0
        or not 0 <= prize_count < deck_size
        or not 0 <= opening_hand_size <= deck_size - prize_count
    ):
        raise ValueError("invalid deck size/counts")
    denominator = choose(deck_size, opening_hand_size)
    starters = 1 + attacker_starter_copies + other_starters
    accepted = 1 - choose(deck_size - starters, opening_hand_size) / denominator
    if accepted <= 0 or critical_nonstarter <= 0:
        raise ValueError("invalid conditioning event")
    prize_denominator = choose(deck_size - opening_hand_size, prize_count)
    mass = wait = eager_a = eager_g = eager_possible = 0.0

    for hand in allocations(opening_hand_size, sizes):
        if hand[2] + hand[3] + hand[6] == 0:
            continue
        ways = 1
        for size, count in zip(sizes, hand):
            ways *= choose(size, count)
        if not ways:
            continue
        remain = tuple(n - k for n, k in zip(sizes, hand))
        # Remaining other starters and filler are strategically identical.
        prize_limits = remain[:6] + (remain[6] + remain[7],)
        for prizes in allocations(prize_count, prize_limits):
            if prizes[0] == 0:
                continue
            prizeways = 1
            for n, k in zip(prize_limits, prizes):
                prizeways *= choose(n, k)
            if not prizeways:
                continue
            weight = ways * prizeways / (
                denominator * accepted * prize_denominator
            )
            mass += weight
            remaining_deck = tuple(
                n - k for n, k in zip(prize_limits, prizes)
            )
            held = (
                hand[0], hand[1], hand[2], hand[3], hand[4],
                hand[5], hand[6] + hand[7],
            )
            preserved = hand[2] == 1 and hand[3] + hand[6] > 0
            wait += weight * after_draw_success(
                held, remaining_deck, preserved, None
            )

            payable = hand[4] > 0 and hand[5] > 0
            need_attacker = hand[3] == 0
            # A singleton Lele already in play cannot be re-searched.
            need_rescue = (
                hand[1] == 0 and not preserved and hand[2] == 0
            )
            first_a = (
                "attacker" if need_attacker else
                "rescue" if need_rescue else None
            )
            first_g = (
                "rescue" if need_rescue else
                "attacker" if need_attacker else None
            )
            if payable and (need_attacker or need_rescue):
                eager_possible += weight
            eager_a += weight * after_draw_success(
                held, remaining_deck, preserved,
                first_a if payable else None, allow_search_fallback,
            )
            eager_g += weight * after_draw_success(
                held, remaining_deck, preserved,
                first_g if payable else None, allow_search_fallback,
            )

    if not mass:
        raise ValueError("conditioning event empty")
    return Result(*(
        value / mass for value in
        (mass, wait, eager_a, eager_g, eager_possible)
    ))
