"""Exact target-Supporter access in an Aichi Mega Absol Crobat-to-Lumineon swap.

The source has Tapu Lele-GX Wonder Tag already. Evaluate the marginal value
of replacing Crobat V with Lumineon V's Luminous Sign, preserving the one
Pokémon V Forest Seal Stone host in a legal full 60-card deck. First-turn
material access is conditional on a Basic-valid seven-card opener, six Prizes,
and one natural draw. A search Ability requires hand-to-Bench entry.

Only one directly held or physically payable named Item bridge is allowed;
searching an eligible body with Quick/Ultra/Communication, or recovering a
Prized body with Hisuian Heavy Ball, is permitted before its Ability.
Item chains, Star Alchemy, draw payloads, opponent locks and actual Supporter
play are deliberately excluded.
"""
from __future__ import annotations

from collections import Counter
from fractions import Fraction
from itertools import combinations
from math import comb

TARGET = "sv7-133"      # Crispin, a singleton Supporter
LELE = "sm2-60"        # Tapu Lele-GX / Wonder Tag
CROBAT = "swsh3-104"   # Dark Asset, not Supporter search
LUMINEON = "swsh9-40"  # Luminous Sign
MEGA = "me1-86"
QUICK = "swsh1-179"
ULTRA = "swsh9-150"
COMM = "sm9-152"
HEAVY = "swsh10-146"
CATEGORIES = (
    "target", "lele", "host", "mega", "other_basic", "evolution",
    "quick", "ultra", "comm", "heavy", "energy", "filler",
)
FLAGS = (
    "target_held", "direct_body", "paid_item_to_body", "heavy_to_body",
    "target_possession", "search_body_seen",
)


def category_counts(
    quantities: dict[str, int], records: dict,
) -> dict[str, int]:
    """Partition all physical cards and preserve exactly one V host."""
    assert quantities[TARGET] == quantities[LELE] == 1
    assert quantities.get(CROBAT, 0) + quantities.get(LUMINEON, 0) == 1
    named = {
        TARGET: "target", LELE: "lele", CROBAT: "host", LUMINEON: "host",
        MEGA: "mega", QUICK: "quick", ULTRA: "ultra",
        COMM: "comm", HEAVY: "heavy",
    }
    out = Counter({key: 0 for key in CATEGORIES})
    for card_id, count in quantities.items():
        record = records[card_id]
        if card_id in named:
            key = named[card_id]
        elif record.is_basic_pokemon:
            key = "other_basic"
        elif record.supertype == "Pokémon":
            key = "evolution"
        elif record.supertype == "Energy":
            key = "energy"
        else:
            key = "filler"
        out[key] += count
    assert sum(out.values()) == 60
    return {key: out[key] for key in CATEGORIES}


def _hands(capacities: dict[str, int], amount: int):
    def generate(index: int, left: int, vector: list[int], weight: int):
        if index == len(CATEGORIES):
            if left == 0:
                yield dict(zip(CATEGORIES, vector)), weight
            return
        key = CATEGORIES[index]
        for chosen in range(min(left, capacities[key]) + 1):
            vector.append(chosen)
            yield from generate(
                index + 1, left - chosen, vector,
                weight * comb(capacities[key], chosen),
            )
            vector.pop()
    yield from generate(0, amount, [], 1)


def route_flags(
    opening: dict[str, int],
    held: dict[str, int],
    prized: dict[str, int],
    quantities: dict[str, int],
    luminous_sign: bool,
) -> dict[str, bool]:
    """One legal hand-to-Bench trigger or payable one-Item bridge."""
    target_held = held["target"] > 0
    target_deck = held["target"] + prized["target"] < quantities["target"]
    # A held opening body must have a different opening Basic to start Active.
    # A body first naturally drawn is always eligible for a Bench play.
    lele_ready = held["lele"] > 0 and (
        opening["lele"] == 0 or
        opening["mega"] + opening["other_basic"] + opening["host"] > 0
    )
    host_ready = luminous_sign and held["host"] > 0 and (
        opening["host"] == 0 or
        opening["mega"] + opening["other_basic"] + opening["lele"] > 0
    )
    body_deck = (
        quantities["lele"] - held["lele"] - prized["lele"] > 0 or (
            luminous_sign and
            quantities["host"] - held["host"] - prized["host"] > 0
        )
    )
    # Starting Active is removed physically from opening hand, so it cannot
    # double as the Pokemon Communication exchange payment.
    spare_pokemon = (
        held["mega"] + held["other_basic"] + held["host"] +
        held["lele"] + held["evolution"] - 1
    )
    paid = body_deck and (
        held["quick"] > 0 and held["energy"] >= 1 or
        held["ultra"] > 0 and held["energy"] >= 2 or
        held["comm"] > 0 and spare_pokemon >= 1
    )
    heavy = held["heavy"] > 0 and (
        prized["lele"] > 0 or
        luminous_sign and prized["host"] > 0
    )
    direct = target_deck and (lele_ready or host_ready)
    paid_source = target_deck and paid
    heavy_source = target_deck and heavy
    return {
        "target_held": target_held,
        "direct_body": direct,
        "paid_item_to_body": paid_source,
        "heavy_to_body": heavy_source,
        "target_possession": (
            target_held or direct or paid_source or heavy_source
        ),
        "search_body_seen": (
            held["lele"] > 0 or luminous_sign and held["host"] > 0
        ),
    }


def exact_access(
    capacities: dict[str, int], luminous_sign: bool,
    opening: int = 7, prizes: int = 6,
) -> dict[str, Fraction]:
    assert tuple(capacities) == CATEGORIES
    n = sum(capacities.values())
    assert 0 < opening < n - prizes
    scores = Counter()
    accepted = 0
    prize_denom = comb(n - opening - 1, prizes)
    for start, weight in _hands(capacities, opening):
        if not start["mega"] + start["other_basic"] + start["lele"] + start["host"]:
            continue
        for drawn in CATEGORIES:
            available = capacities[drawn] - start[drawn]
            if available == 0:
                continue
            hand = start.copy()
            hand[drawn] += 1
            w = weight * available
            accepted += w
            rem = {key: capacities[key] - hand[key] for key in CATEGORIES}
            others = n - opening - 1 - rem["target"] - rem["lele"] - rem["host"]
            for pt in range(min(prizes, rem["target"]) + 1):
                for pl in range(min(prizes - pt, rem["lele"]) + 1):
                    for ph in range(min(prizes - pt - pl, rem["host"]) + 1):
                        nr = prizes - pt - pl - ph
                        if nr > others:
                            continue
                        pw = (
                            comb(rem["target"], pt) *
                            comb(rem["lele"], pl) *
                            comb(rem["host"], ph) *
                            comb(others, nr)
                        )
                        flags = route_flags(
                            start, hand,
                            {"target": pt, "lele": pl, "host": ph},
                            capacities, luminous_sign,
                        )
                        for key in FLAGS:
                            scores[key] += w * pw * int(flags[key])
    denom = accepted * prize_denom
    assert denom > 0
    return {key: Fraction(scores[key], denom) for key in FLAGS}


def physical_oracle(
    capacities: dict[str, int], luminous_sign: bool,
    opening: int, prizes: int,
) -> dict[str, Fraction]:
    """Independently enumerate labeled cards and chronological physical zones."""
    assert tuple(capacities) == CATEGORIES
    cards = [
        key for key in CATEGORIES for _ in range(capacities[key])
    ]
    n = len(cards)
    scores = Counter()
    worlds = 0
    for opener_ids in combinations(range(n), opening):
        starting = Counter(cards[i] for i in opener_ids)
        if not (
            starting["mega"] + starting["other_basic"] +
            starting["host"] + starting["lele"]
        ):
            continue
        opener_set = set(opener_ids)
        remaining = [i for i in range(n) if i not in opener_set]
        for prize_ids in combinations(remaining, prizes):
            prize_set = set(prize_ids)
            prize = Counter(cards[i] for i in prize_ids)
            for drawn_id in remaining:
                if drawn_id in prize_set:
                    continue
                hand = Counter(starting)
                hand[cards[drawn_id]] += 1
                flags = route_flags(
                    starting, hand, prize, capacities, luminous_sign,
                )
                scores.update({k: int(flags[k]) for k in FLAGS})
                worlds += 1
    return {key: Fraction(scores[key], worlds) for key in FLAGS}
