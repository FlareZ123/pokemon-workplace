"""Exact first-draw Regidrago V access after legal opening, with discardable Dragapult.

The hand is eight visible cards: accepted seven-card Basic opener plus first
natural draw. Regidrago V may be held, fetched via VIP Pass, or fetched via
Quick Ball or Mysterious Treasure by discarding a held Dragon Dragapult ex or
a designated disposable non-Basic card. This is access, not full setup.
"""
from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from math import comb


@dataclass(frozen=True)
class Build:
    regidrago_v: int = 4
    other_basics: int = 11
    dragapult_ex: int = 1
    vip_pass: int = 3
    quick_ball: int = 3
    mysterious_treasure: int = 3
    safe_filler: int = 0
    deck_size: int = 60


def choose(n: int, k: int) -> int:
    return comb(n, k) if 0 <= k <= n else 0


def access(build: Build, *, prizes: int = 6, opener: int = 7) -> dict[str, Fraction]:
    """Exact conditioned probabilities for first-draw Item access routes."""
    protected = (
        build.deck_size - build.regidrago_v - build.other_basics
        - build.dragapult_ex - build.vip_pass - build.quick_ball
        - build.mysterious_treasure - build.safe_filler
    )
    if min(build.__dict__.values()) < 0 or protected < 0:
        raise ValueError('Invalid deck partition')
    groups = (
        build.regidrago_v, build.other_basics, build.dragapult_ex,
        build.vip_pass, build.quick_ball, build.mysterious_treasure,
        build.safe_filler, protected,
    )
    visible = opener + 1
    if visible + prizes > build.deck_size:
        raise ValueError('Insufficient cards for setup, prizes and draw')
    keys = (
        'regidrago_held', 'vip_held', 'vip_only_when_no_regidrago',
        'access_vip_or_held', 'access_any_ideal', 'access_any_safe',
        'access_with_payload_payment', 'vip_unique_safe',
        'vip_unique_ideal', 'searchable_regidrago',
        'no_regidrago_held', 'vip_out_accessible',
        'payload_payment_route', 'payload_payment_unique',
    )
    counts = {key: 0 for key in keys}
    mass = 0
    for first in product(*(range(min(n, visible) + 1) for n in groups[:-1])):
        remainder = visible - sum(first)
        if not 0 <= remainder <= protected:
            continue
        hand = (*first, remainder)
        basics = hand[0] + hand[1]
        allowed_last_positions = (
            visible if basics >= 2 else visible - 1 if basics == 1 else 0
        )
        if not allowed_last_positions:
            continue
        ways = allowed_last_positions
        for n, count in zip(groups, hand):
            ways *= choose(n, count)
        rv_unseen = build.regidrago_v - hand[0]
        other_unseen = build.deck_size - visible - rv_unseen
        for rv_prized in range(min(prizes, rv_unseen) + 1):
            prize_ways = (
                choose(rv_unseen, rv_prized)
                * choose(other_unseen, prizes - rv_prized)
            )
            if not prize_ways:
                continue
            weight = ways * prize_ways
            mass += weight
            can_search = rv_unseen > rv_prized
            held = hand[0] > 0
            vip = hand[3] > 0
            paid_item = hand[4] + hand[5] > 0
            paid_safe = paid_item and hand[6] > 0
            paid_payload = paid_item and hand[2] > 0
            free_route = can_search and vip
            ideal_route = can_search and paid_item
            safe_route = can_search and paid_safe
            payload_route = can_search and paid_payload
            events = {
                'regidrago_held': held,
                'vip_held': vip,
                'vip_only_when_no_regidrago': vip and not held,
                'access_vip_or_held': held or free_route,
                'access_any_ideal': held or free_route or ideal_route,
                'access_any_safe': held or free_route or safe_route,
                'access_with_payload_payment': (
                    held or free_route or safe_route or payload_route
                ),
                'vip_unique_safe': not held and free_route and not safe_route,
                'vip_unique_ideal': not held and free_route and not ideal_route,
                'searchable_regidrago': can_search,
                'no_regidrago_held': not held,
                'vip_out_accessible': not held and free_route,
                'payload_payment_route': payload_route,
                'payload_payment_unique': (
                    not held and not free_route and not safe_route
                    and payload_route
                ),
            }
            for key, occurred in events.items():
                if occurred:
                    counts[key] += weight
    if not mass:
        raise ValueError('No accepted opening hands')
    return {key: Fraction(value, mass) for key, value in counts.items()}


def profiles(safe_filler: int = 0) -> dict[str, Build]:
    return {
        'published, 3 VIP / 1 Dragapult': Build(safe_filler=safe_filler),
        '+1 Dragapult / -1 VIP': Build(
            dragapult_ex=2, vip_pass=2, safe_filler=safe_filler,
        ),
    }


if __name__ == '__main__':
    for d in (0, 10, 20, 30):
        print('safe filler', d)
        for name, build in profiles(d).items():
            p = access(build)
            print(name, {
                key: f'{100 * float(p[key]):.9f}%'
                for key in (
                    'access_vip_or_held', 'access_any_safe',
                    'access_with_payload_payment', 'access_any_ideal',
                    'payload_payment_unique',
                )
            })
