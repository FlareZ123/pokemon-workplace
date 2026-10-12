"""Exact first-window deadline penalty for shared Quick Ball two-channel access."""
from __future__ import annotations

from dataclasses import dataclass
from quick_ball_pre_draw_option import after_draw_success, allocations, choose


@dataclass(frozen=True)
class DeadlineResult:
    conditioned_mass: float
    both_after_draw: float
    attacker_before_draw: float
    rescue_before_draw: float


def deadline_joint_probability(
    deck_size: int, prize_count: int, *, other_starters: int,
    attacker_starter_copies: int, critical_nonstarter: int,
    rescue_nonstarter: int, quick_ball_copies: int,
    disposable_nonstarter: int, opening_hand_size: int = 7,
) -> DeadlineResult:
    """Require either attacker or Gladion access before the natural draw."""
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
        raise ValueError("invalid deck composition")
    denominator = choose(deck_size, opening_hand_size)
    starters = 1 + attacker_starter_copies + other_starters
    accepted = 1 - choose(
        deck_size - starters, opening_hand_size
    ) / denominator
    if not accepted or not critical_nonstarter:
        raise ValueError("conditioning event empty")
    prize_denominator = choose(deck_size - opening_hand_size, prize_count)
    mass = baseline = attacker_early = rescue_early = 0.0

    for hand in allocations(opening_hand_size, sizes):
        if hand[2] + hand[3] + hand[6] == 0:
            continue
        hand_ways = 1
        for n, k in zip(sizes, hand):
            hand_ways *= choose(n, k)
        if not hand_ways:
            continue
        remaining = tuple(n - k for n, k in zip(sizes, hand))
        limits = remaining[:6] + (remaining[6] + remaining[7],)
        for prized in allocations(prize_count, limits):
            if prized[0] == 0:
                continue
            prize_ways = 1
            for n, k in zip(limits, prized):
                prize_ways *= choose(n, k)
            if not prize_ways:
                continue
            weight = hand_ways * prize_ways / (
                denominator * accepted * prize_denominator
            )
            mass += weight
            held = (
                hand[0], hand[1], hand[2], hand[3], hand[4],
                hand[5], hand[6] + hand[7],
            )
            pack = tuple(n - k for n, k in zip(limits, prized))
            preserved = hand[2] == 1 and hand[3] + hand[6] > 0
            payable = hand[4] > 0 and hand[5] > 0
            baseline += weight * after_draw_success(
                held, pack, preserved, None
            )

            if hand[3] > 0:
                a_p = after_draw_success(held, pack, preserved, None)
            elif payable and pack[3] > 0:
                a_p = after_draw_success(
                    held, pack, preserved, "attacker"
                )
            else:
                a_p = 0.0
            attacker_early += weight * a_p

            if hand[1] > 0:
                g_p = after_draw_success(held, pack, preserved, None)
            elif preserved and pack[1] > 0:
                early_hand, early_pack = list(held), list(pack)
                early_hand[1] += 1
                early_pack[1] -= 1
                g_p = after_draw_success(
                    tuple(early_hand), tuple(early_pack), False, None
                )
            elif payable and pack[2] > 0 and pack[1] > 0:
                g_p = after_draw_success(
                    held, pack, preserved, "rescue"
                )
            else:
                g_p = 0.0
            rescue_early += weight * g_p

    if not mass:
        raise ValueError("empty conditioning event")
    return DeadlineResult(*(
        value / mass for value in
        (mass, baseline, attacker_early, rescue_early)
    ))
