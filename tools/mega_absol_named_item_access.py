"""Exact one-step Mega Absol ex access from the published Aichi 2026 list.

Supports physical seven-card Basic-valid openings, six hidden Prizes,
one natural draw, individually held named Items, and explicit payments.
No actions are simulated beyond one named Item and its destination.
"""
from __future__ import annotations

from collections import Counter
from fractions import Fraction
from itertools import combinations
from math import comb

CATEGORIES = (
    "mega", "other_basic", "evolution", "quick_ball", "ultra_ball",
    "vip_pass", "communication", "heavy_ball", "energy", "filler",
)
TARGETS = {
    "mega": "me1-86",
    "quick_ball": "swsh1-179",
    "ultra_ball": "swsh9-150",
    "vip_pass": "swsh8-225",
    "communication": "sm9-152",
    "heavy_ball": "swsh10-146",
}
POLICIES = ("direct", "vip_or_heavy", "energy_paid", "unpaid_upper")


def category_counts(quantities: dict[str, int], records: dict) -> dict[str, int]:
    known = {card_id: category for category, card_id in TARGETS.items()}
    out = Counter({category: 0 for category in CATEGORIES})
    for card_id, quantity in quantities.items():
        record = records[card_id]
        if card_id in known:
            category = known[card_id]
        elif record.is_basic_pokemon:
            category = "other_basic"
        elif record.supertype == "Pokémon":
            category = "evolution"
        elif record.supertype == "Energy":
            category = "energy"
        else:
            category = "filler"
        out[category] += quantity
    assert sum(out.values()) == 60
    assert out["mega"] >= 1
    return dict(out)


def _hands(cap: dict[str, int], cards: int):
    names = tuple(cap)

    def build(i: int, remaining: int, hand: list[int], weight: int):
        if i == len(names):
            if remaining == 0:
                yield dict(zip(names, hand)), weight
            return
        for n in range(min(remaining, cap[names[i]]) + 1):
            hand.append(n)
            yield from build(
                i + 1, remaining - n, hand, weight * comb(cap[names[i]], n)
            )
            hand.pop()

    yield from build(0, cards, [], 1)


def _route_flags(full: dict[str, int], prized_target: int) -> dict[str, bool]:
    # Basic-valid setup consumes one Basic as the starting Active Pokémon.
    direct = full["mega"] > 0
    deck_target = prized_target < (0 if direct else full["_total_mega"])
    prized = prized_target > 0
    heavy = full["heavy_ball"] > 0 and prized
    vip = full["vip_pass"] > 0 and deck_target
    spare_pokemon = full["other_basic"] + full["evolution"] - 1
    communication = full["communication"] > 0 and spare_pokemon >= 1
    strict_item = (
        vip
        or deck_target and (
            full["quick_ball"] > 0 and full["energy"] >= 1
            or full["ultra_ball"] > 0 and full["energy"] >= 2
            or communication
        )
    )
    unpaid_item = deck_target and (
        full["quick_ball"] > 0 or full["ultra_ball"] > 0
        or full["vip_pass"] > 0 or full["communication"] > 0
    )
    return {
        "direct": direct,
        "vip_or_heavy": direct or vip or heavy,
        "energy_paid": direct or strict_item or heavy,
        "unpaid_upper": direct or unpaid_item or heavy,
    }


def exact_access(
    capacities: dict[str, int], opening: int = 7, prizes: int = 6
) -> dict[str, Fraction]:
    assert set(capacities) == set(CATEGORIES)
    n = sum(capacities.values())
    assert 0 < opening < n - prizes
    target_total = capacities["mega"]
    assert target_total > 0
    scores = {name: 0 for name in POLICIES}
    accepted_weight = 0
    prize_denominator = comb(n - opening - 1, prizes)
    total_weight = comb(n, opening) * (n - opening)

    for initial, ways in _hands(capacities, opening):
        if initial["mega"] + initial["other_basic"] == 0:
            continue
        for draw_category in CATEGORIES:
            if initial[draw_category] == capacities[draw_category]:
                continue
            after_draw = initial.copy()
            after_draw[draw_category] += 1
            after_draw["_total_mega"] = target_total
            label_weight = ways * (capacities[draw_category] - initial[draw_category])
            accepted_weight += label_weight
            remaining_mega = target_total - after_draw["mega"]
            for k in range(min(remaining_mega, prizes) + 1):
                prize_weight = (
                    comb(remaining_mega, k)
                    * comb(n - opening - 1 - remaining_mega, prizes - k)
                )
                flags = _route_flags(after_draw, k)
                for name in POLICIES:
                    scores[name] += label_weight * prize_weight * int(flags[name])

    accepted_denominator = accepted_weight * prize_denominator
    return {
        "valid_opening": Fraction(accepted_weight, total_weight),
        **{
            name: Fraction(value, accepted_denominator)
            for name, value in scores.items()
        },
    }


def physical_oracle(
    capacities: dict[str, int], opening: int, prizes: int
) -> dict[str, Fraction]:
    # Independent enumeration of labeled physical cards: hand first,
    # six Prizes next, first natural deck draw last.
    cards = [
        category
        for category in CATEGORIES
        for _ in range(capacities[category])
    ]
    n = len(cards)
    accepted_hands = 0
    accepted_worlds = 0
    hits = Counter({name: 0 for name in POLICIES})
    for hand in combinations(range(n), opening):
        starting = Counter(cards[j] for j in hand)
        if starting["mega"] + starting["other_basic"] == 0:
            continue
        accepted_hands += 1
        hand_ids = set(hand)
        rest = [j for j in range(n) if j not in hand_ids]
        for prize_ids in combinations(rest, prizes):
            prize_set = set(prize_ids)
            prized_mega = sum(cards[j] == "mega" for j in prize_ids)
            for draw_id in rest:
                if draw_id in prize_set:
                    continue
                after = Counter(starting)
                after[cards[draw_id]] += 1
                full = {name: after[name] for name in CATEGORIES}
                full["_total_mega"] = capacities["mega"]
                flags = _route_flags(full, prized_mega)
                accepted_worlds += 1
                hits.update(name for name in POLICIES if flags[name])

    return {
        "valid_opening": Fraction(accepted_hands, comb(n, opening)),
        **{
            name: Fraction(hits[name], accepted_worlds)
            for name in POLICIES
        },
    }
