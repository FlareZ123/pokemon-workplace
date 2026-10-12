"""Exact first-draw Item routes for loading Dragapult ex to the discard pile.

Analyzed routes: Battle Compressor from deck; held Dragapult as Quick Ball
or Mysterious Treasure payment; Mysterious Treasure into Dragapult followed
by a second one-card discard Item. No draw engines, prior search, locks,
Supporters, or game attacks are modeled.
"""
from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from math import comb


@dataclass(frozen=True)
class Build:
    dragapult: int = 1
    compressor: int = 1
    quick_ball: int = 3
    mysterious_treasure: int = 3
    regidrago_v: int = 4
    other_basics: int = 11
    safe_filler: int = 0
    total: int = 60


def choose(n: int, k: int) -> int:
    return comb(n, k) if 0 <= k <= n else 0


def exact_access(
    build: Build, *, prize_count: int = 6, opening_size: int = 7
) -> dict[str, Fraction]:
    """Exact conditional distribution of accepted opener, Prizes and first draw.

    For Item payment/search routes, require a Regidrago V still in deck.
    The safe chain requires a designated expendable non-Basic filler card.
    The ideal chain allows any other hand card as the first Treasure payment.
    """
    protected_filler = (
        build.total - build.dragapult - build.compressor
        - build.quick_ball - build.mysterious_treasure
        - build.regidrago_v - build.other_basics - build.safe_filler
    )
    if protected_filler < 0 or min(build.__dict__.values()) < 0:
        raise ValueError("Invalid deck partition")
    group = (
        build.dragapult, build.compressor, build.quick_ball,
        build.mysterious_treasure, build.regidrago_v, build.other_basics,
        build.safe_filler, protected_filler,
    )
    n = build.total
    visible = opening_size + 1
    if prize_count < 0 or visible + prize_count > n:
        raise ValueError("Insufficient cards for setup, Prizes and next draw")
    keys = (
        "dragapult_not_all_prized",
        "loaded_direct", "loaded_ideal", "loaded_safe",
        "loaded_bc", "loaded_hand_payment",
        "loaded_chain_ideal", "loaded_chain_safe",
        "regidrago_hand",
        "joint_loaded_ideal_regidrago_hand",
        "joint_loaded_safe_regidrago_hand",
    )
    numerators = {key: 0 for key in keys}
    denominator = 0

    # An unordered 8-card visible hand encodes the 7-card opener plus one
    # natural draw. One Basic in the eight has 7 of 8 acceptable last draws;
    # two or more Basics makes every choice of the eighth card acceptable.
    for first in product(*(range(min(c, visible) + 1) for c in group[:-1])):
        final = visible - sum(first)
        if not 0 <= final <= group[-1]:
            continue
        hand = (*first, final)
        basics = hand[4] + hand[5]
        valid_last_choices = (
            visible if basics >= 2 else (visible - 1 if basics == 1 else 0)
        )
        if not valid_last_choices:
            continue
        hand_ways = valid_last_choices
        for size, count in zip(group, hand):
            hand_ways *= choose(size, count)
        if not hand_ways:
            continue

        unseen_dp = build.dragapult - hand[0]
        unseen_regidrago = build.regidrago_v - hand[4]
        other_unseen = n - visible - unseen_dp - unseen_regidrago
        for dp_prized in range(min(prize_count, unseen_dp) + 1):
            for regidrago_prized in range(
                min(prize_count - dp_prized, unseen_regidrago) + 1
            ):
                rest_prized = prize_count - dp_prized - regidrago_prized
                prize_ways = (
                    choose(unseen_dp, dp_prized)
                    * choose(unseen_regidrago, regidrago_prized)
                    * choose(other_unseen, rest_prized)
                )
                if not prize_ways:
                    continue
                weight = hand_ways * prize_ways
                denominator += weight
                deck_dp = unseen_dp - dp_prized
                deck_regidrago = unseen_regidrago - regidrago_prized
                searchable = deck_regidrago > 0

                bc = hand[1] > 0 and deck_dp > 0
                held_payment = (
                    hand[0] > 0 and hand[2] + hand[3] > 0 and searchable
                )
                chain = (
                    deck_dp > 0 and hand[3] > 0
                    and hand[2] + hand[3] >= 2 and searchable
                )
                chain_safe = chain and hand[6] > 0
                direct = bc or held_payment
                ideal = direct or chain
                safe = direct or chain_safe

                events = {
                    "dragapult_not_all_prized": hand[0] + deck_dp > 0,
                    "loaded_direct": direct,
                    "loaded_ideal": ideal,
                    "loaded_safe": safe,
                    "loaded_bc": bc,
                    "loaded_hand_payment": held_payment,
                    "loaded_chain_ideal": chain,
                    "loaded_chain_safe": chain_safe,
                    "regidrago_hand": hand[4] > 0,
                    "joint_loaded_ideal_regidrago_hand": ideal and hand[4] > 0,
                    "joint_loaded_safe_regidrago_hand": safe and hand[4] > 0,
                }
                for key, occurred in events.items():
                    if occurred:
                        numerators[key] += weight

    if not denominator:
        raise ValueError("No valid starting hands")
    return {
        key: Fraction(numerator, denominator)
        for key, numerator in numerators.items()
    }


def counterfactuals(safe_filler: int = 0) -> dict[str, Build]:
    """Five sixty-card profiles, adjusting one declared slot at a time."""
    baseline = Build(safe_filler=safe_filler)
    return {
        "published": baseline,
        "second Dragapult for unnamed filler": Build(
            dragapult=2, safe_filler=safe_filler
        ),
        "second Dragapult for one Quick Ball": Build(
            dragapult=2, quick_ball=2, safe_filler=safe_filler
        ),
        "second Dragapult for one Mysterious Treasure": Build(
            dragapult=2, mysterious_treasure=2, safe_filler=safe_filler
        ),
        "second Dragapult for Battle Compressor": Build(
            dragapult=2, compressor=0, safe_filler=safe_filler
        ),
    }
