"""Exact first-turn Mew/Genesect source access with paid Quick and Ultra Ball.

The explicit discard category D is a user-defined policy sensitivity, not a
claim that that many cards in the printed deck are strategically disposable.
"""

from __future__ import annotations

import json
from fractions import Fraction
from itertools import combinations
from math import comb
from pathlib import Path
from typing import Iterator

from results.mew_genesect_vip_opening.reproduce import (
    category_counts,
    exact as vip_only_exact,
)


def vectors(total: int, caps: tuple[int, ...]) -> Iterator[tuple[int, ...]]:
    if not caps:
        if total == 0:
            yield ()
        return
    for n in range(min(total, caps[0]) + 1):
        for rest in vectors(total - n, caps[1:]):
            yield (n, *rest)


def composition(vip: int, disposable: int) -> tuple[int, ...]:
    """Mew, Genesect, other Basic, VIP, Quick, Ultra, D, protected other."""
    assert vip in (3, 4) and 0 <= disposable <= 41 - vip
    return 4, 4, 3, vip, 4, 4, disposable, 41 - vip - disposable


def paid_capacity(quick: int, ultra: int, safe_discards: int) -> int:
    """Maximum Basic searches with two printed discard costs and shared D."""
    quick_uses = min(quick, safe_discards)
    ultra_uses = min(ultra, (safe_discards - quick_uses) // 2)
    return quick_uses + ultra_uses


def legal_events(
    seen: tuple[int, ...], p_mew: int, p_genesect: int,
    deck_counts: tuple[int, ...], genesect_goal: int,
) -> tuple[bool, bool, bool]:
    mew, genesect, _, vip, quick, ultra, safe_discards, _ = seen
    need_mew = max(0, 1 - mew)
    need_genesect = max(0, genesect_goal - genesect)
    need = need_mew + need_genesect
    targets_exist = (
        deck_counts[0] - mew - p_mew >= need_mew
        and deck_counts[1] - genesect - p_genesect >= need_genesect
    )
    direct = need == 0
    via_vip = targets_exist and need <= 2 * vip
    via_balls = targets_exist and need <= 2 * vip + paid_capacity(
        quick, ultra, safe_discards
    )
    return direct, via_vip, via_balls


def exact(
    vip: int, disposable: int, genesect_goal: int
) -> dict[str, Fraction]:
    """Count exact initial-seven, six-Prize and first-draw configurations."""
    cards = composition(vip, disposable)
    assert genesect_goal in (2, 3)
    totals = [0, 0, 0, 0]
    for seen in vectors(8, cards):
        visible_basics = sum(seen[:3])
        if visible_basics == 0:
            continue
        # One Basic in the eight visible cards must not be the eighth draw.
        hand_order_factor = 8 if visible_basics >= 2 else 7
        for count, used in zip(cards, seen):
            hand_order_factor *= comb(count, used)
        remaining_mew = cards[0] - seen[0]
        remaining_genesect = cards[1] - seen[1]
        remaining_other = 52 - remaining_mew - remaining_genesect
        # Prize categories other than Mew/Genesect are exchangeable for this endpoint.
        for prized_mew in range(min(6, remaining_mew) + 1):
            for prized_genesect in range(min(6 - prized_mew, remaining_genesect) + 1):
                prized_other = 6 - prized_mew - prized_genesect
                if prized_other > remaining_other:
                    continue
                weight = (
                    hand_order_factor
                    * comb(remaining_mew, prized_mew)
                    * comb(remaining_genesect, prized_genesect)
                    * comb(remaining_other, prized_other)
                )
                direct, via_vip, via_balls = legal_events(
                    seen, prized_mew, prized_genesect, cards, genesect_goal
                )
                totals[0] += weight
                totals[1] += weight * direct
                totals[2] += weight * via_vip
                totals[3] += weight * via_balls
    denominator = 8 * comb(60, 8) * comb(52, 6)
    assert Fraction(totals[0], denominator) == 1 - Fraction(
        comb(49, 7), comb(60, 7)
    )
    assert totals[1] <= totals[2] <= totals[3]
    return dict(zip(
        ("direct", "vip", "vip_plus_paid_balls"),
        (Fraction(t, totals[0]) for t in totals[1:]),
    ))


def exact_toy(
    cards: tuple[int, ...], genesect_goal: int,
    hand_size: int = 3, prizes: int = 2,
) -> tuple[Fraction, ...]:
    total_cards = sum(cards)
    exposed = hand_size + 1
    totals = [0, 0, 0, 0]
    for seen in vectors(exposed, cards):
        basic_seen = sum(seen[:3])
        if basic_seen == 0:
            continue
        factor = exposed if basic_seen >= 2 else hand_size
        for count, used in zip(cards, seen):
            factor *= comb(count, used)
        rem_m = cards[0] - seen[0]
        rem_g = cards[1] - seen[1]
        rem_other = total_cards - exposed - rem_m - rem_g
        for pm in range(min(prizes, rem_m) + 1):
            for pg in range(min(prizes - pm, rem_g) + 1):
                tail = prizes - pm - pg
                if tail > rem_other:
                    continue
                weight = factor * comb(rem_m, pm) * comb(rem_g, pg) * comb(rem_other, tail)
                events = legal_events(seen, pm, pg, cards, genesect_goal)
                totals[0] += weight
                for i, success in enumerate(events, 1):
                    totals[i] += weight * success
    return tuple(Fraction(k, totals[0]) for k in totals[1:])


def labeled_physical_oracle(
    cards: tuple[int, ...], genesect_goal: int,
    hand_size: int = 3, prizes: int = 2,
) -> tuple[tuple[Fraction, ...], int]:
    """Independently enumerate labeled zones and all possible paid Ball subsets."""
    physical = tuple(category for category, n in enumerate(cards) for _ in range(n))
    indexes = tuple(range(len(physical)))
    totals = [0, 0, 0, 0]
    for hand in combinations(indexes, hand_size):
        if not any(physical[i] < 3 for i in hand):
            continue
        remaining = tuple(i for i in indexes if i not in hand)
        for prized in combinations(remaining, prizes):
            unprized = tuple(i for i in remaining if i not in prized)
            pm = sum(physical[i] == 0 for i in prized)
            pg = sum(physical[i] == 1 for i in prized)
            for first_draw in unprized:
                seen = tuple(sum(physical[i] == category for i in (*hand, first_draw))
                             for category in range(8))
                missing_m = max(0, 1 - seen[0])
                missing_g = max(0, genesect_goal - seen[1])
                missing = missing_m + missing_g
                searchable = cards[0] - seen[0] - pm >= missing_m and (
                    cards[1] - seen[1] - pg >= missing_g
                )
                direct = missing == 0
                via_vip = searchable and missing <= 2 * seen[3]
                via_balls = any(
                    searchable and missing <= 2 * seen[3] + q + u
                    for q in range(seen[4] + 1)
                    for u in range(seen[5] + 1)
                    if q + 2 * u <= seen[6]
                )
                totals[0] += 1
                totals[1] += direct
                totals[2] += via_vip
                totals[3] += via_balls
    return tuple(Fraction(k, totals[0]) for k in totals[1:]), totals[0]


def assert_card_sources() -> None:
    root = Path(__file__).resolve().parents[2]
    for card_id, name, required_text in (
        ("swsh8-225", "Battle VIP Pass", "up to 2 Basic Pokémon"),
        ("swsh1-179", "Quick Ball", "discard another card"),
        ("swsh9-150", "Ultra Ball", "discard 2 other cards"),
    ):
        path = root / "resources" / "cards" / "en" / (card_id.rsplit("-", 1)[0] + ".json")
        record = next(c for c in json.loads(path.read_text(encoding="utf-8")) if c["id"] == card_id)
        assert record["name"] == name and "Item" in record["subtypes"]
        assert required_text in " ".join(record["rules"]), (card_id, required_text)


def self_test() -> None:
    assert_card_sources()
    for tiny in ((2, 2, 1, 2, 1, 1, 2, 1), (2, 2, 1, 1, 1, 1, 3, 1)):
        assert sum(tiny) == 12
        for target in (2, 3):
            grouped = exact_toy(tiny, target)
            labeled, legal_worlds = labeled_physical_oracle(tiny, target)
            assert grouped == labeled, (tiny, target, grouped, labeled)
            assert legal_worlds == 46620
            print(f"Physical 12-card oracle {target}-Genesect, {legal_worlds} valid deals: PASS")
    for quick in range(5):
        for ultra in range(5):
            for safe in range(10):
                brute = max(q + u for q in range(quick + 1)
                            for u in range(ultra + 1) if q + 2 * u <= safe)
                assert brute == paid_capacity(quick, ultra, safe)
    for target in (2, 3):
        for disposable in (0, 6, 12, 24):
            base = exact(3, disposable, target)
            variant = exact(4, disposable, target)
            assert base["vip"] == vip_only_exact(
                category_counts(3), target, vip_use_limit=None
            )["combined"]
            assert variant["vip"] == vip_only_exact(
                category_counts(4), target, vip_use_limit=None
            )["combined"]
            assert variant["vip_plus_paid_balls"] > base["vip_plus_paid_balls"]
            print(f"Mew+{target} Genesect D={disposable}: "
                  f"3-VIP {float(base['vip_plus_paid_balls']):.9%}, "
                  f"4-VIP {float(variant['vip_plus_paid_balls']):.9%}, "
                  f"gain {float(variant['vip_plus_paid_balls']-base['vip_plus_paid_balls'])*100:.9f} pp")


if __name__ == "__main__":
    self_test()
