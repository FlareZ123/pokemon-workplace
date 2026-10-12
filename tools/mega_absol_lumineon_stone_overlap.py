"""Joint Forest Seal Stone / Luminous Sign / Wonder Tag first-turn access.

This extends the paper Aichi Mega Absol Lumineon-versus-Crobat Supporter
counterfactual with a shared one-Pokemon-V universal Star Alchemy source.
One individually paid search Item may retrieve a body before it is played or
equipped with an already held Stone. Adventure Bag can obtain Stone only when
it is the sole Item in that Stone route. Prizes are sampled jointly.
"""
from __future__ import annotations

from collections import Counter
from fractions import Fraction
from itertools import combinations
from math import comb

from tools.mega_absol_lumineon_supporter import (
    CATEGORIES as BASE_CATEGORIES,
    CROBAT, LUMINEON,
    category_counts as base_counts,
    route_flags as supporter_flags,
)

STONE = "swsh12-156"
BAG = "sm8-167"
CATEGORIES = (
    "target", "lele", "host", "mega", "other_basic", "evolution",
    "quick", "ultra", "comm", "heavy", "energy", "stone", "bag", "filler",
)
FLAGS = (
    "named_body", "stone_direct", "stone_prize_paid",
    "stone_deck_paid", "stone_any", "union_stone",
)


def category_counts(
    quantities: dict[str, int], records: dict,
) -> dict[str, int]:
    """Lift the fully verified source deck's 12-category Supporter counts."""
    assert quantities[STONE] == quantities[BAG] == 1
    old = base_counts(quantities, records)
    old["filler"] -= quantities[STONE] + quantities[BAG]
    assert old["filler"] >= 0
    return {
        key: quantities[STONE] if key == "stone" else
        quantities[BAG] if key == "bag" else old[key]
        for key in CATEGORIES
    }


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
    starting: dict[str, int],
    held: dict[str, int],
    prizes: dict[str, int],
    capacities: dict[str, int],
    luminous_sign: bool,
) -> dict[str, bool]:
    """Union independent legal plans, without double-spending any one Item."""
    supporter = supporter_flags(
        starting, held, prizes, capacities, luminous_sign,
    )["target_possession"]
    target_live = (
        held["target"] + prizes["target"] < capacities["target"]
    )
    host_held = held["host"] > 0
    host_prized = prizes["host"] > 0
    host_deck = (
        capacities["host"] - held["host"] - prizes["host"] > 0
    )
    stone_available = held["stone"] > 0 or (
        held["bag"] > 0 and
        capacities["stone"] - held["stone"] - prizes["stone"] > 0
    )
    # One allowed QB, Ultra or Communication can fetch the V host to hand
    # when Forest Seal Stone is ALREADY held. Bag into Stone plus a
    # different search Item would be a two-Item chain and is excluded.
    spare_pokemon = (
        held["mega"] + held["other_basic"] + held["host"] +
        held["lele"] + held["evolution"] - 1
    )
    paid_source = (
        held["quick"] > 0 and held["energy"] >= 1 or
        held["ultra"] > 0 and held["energy"] >= 2 or
        held["comm"] > 0 and spare_pokemon >= 1
    )
    direct = target_live and host_held and stone_available
    prize_paid = (
        target_live and host_prized and held["stone"] > 0
        and held["heavy"] > 0
    )
    deck_paid = (
        target_live and host_deck and held["stone"] > 0
        and paid_source
    )
    stone = bool(direct or prize_paid or deck_paid)
    return {
        "named_body": bool(supporter),
        "stone_direct": bool(direct),
        "stone_prize_paid": bool(prize_paid),
        "stone_deck_paid": bool(deck_paid),
        "stone_any": stone,
        "union_stone": bool(supporter or stone),
    }


def exact_access(
    capacities: dict[str, int], luminous_sign: bool,
    opening: int = 7, prizes: int = 6,
) -> dict[str, Fraction]:
    assert tuple(capacities) == CATEGORIES
    n = sum(capacities.values())
    assert 0 < opening < n - prizes
    score = Counter()
    accepted = 0
    prize_denom = comb(n - opening - 1, prizes)
    for start, weight in _hands(capacities, opening):
        if not start["mega"] + start["other_basic"] + start["lele"] + start["host"]:
            continue
        for drawn in CATEGORIES:
            count = capacities[drawn] - start[drawn]
            if not count:
                continue
            held = start.copy()
            held[drawn] += 1
            w = weight * count
            accepted += w
            rem = {
                key: capacities[key] - held[key]
                for key in CATEGORIES
            }
            other = (
                n - opening - 1 - rem["target"] -
                rem["lele"] - rem["host"] - rem["stone"]
            )
            for pt in range(min(prizes, rem["target"]) + 1):
                for pl in range(min(prizes - pt, rem["lele"]) + 1):
                    for ph in range(min(prizes - pt - pl, rem["host"]) + 1):
                        for ps in range(min(prizes - pt - pl - ph, rem["stone"]) + 1):
                            rest = prizes - pt - pl - ph - ps
                            if rest > other:
                                continue
                            prize_weight = (
                                comb(rem["target"], pt) *
                                comb(rem["lele"], pl) *
                                comb(rem["host"], ph) *
                                comb(rem["stone"], ps) *
                                comb(other, rest)
                            )
                            flags = route_flags(
                                start, held,
                                {"target": pt, "lele": pl,
                                 "host": ph, "stone": ps},
                                capacities, luminous_sign,
                            )
                            for key in FLAGS:
                                score[key] += w * prize_weight * int(flags[key])
    denom = accepted * prize_denom
    assert denom > 0
    return {
        key: Fraction(score[key], denom)
        for key in FLAGS
    }


def physical_oracle(
    capacities: dict[str, int], luminous_sign: bool,
    opening: int, prizes: int,
) -> dict[str, Fraction]:
    """Exhaustive physical-card oracle, hand/Prize/draw in actual order."""
    assert tuple(capacities) == CATEGORIES
    cards = [
        key for key in CATEGORIES
        for _ in range(capacities[key])
    ]
    n = len(cards)
    scores = Counter()
    worlds = 0
    for starter_ids in combinations(range(n), opening):
        start = Counter(cards[i] for i in starter_ids)
        if not (
            start["mega"] + start["other_basic"] +
            start["lele"] + start["host"]
        ):
            continue
        start_set = set(starter_ids)
        remaining = [i for i in range(n) if i not in start_set]
        for prize_ids in combinations(remaining, prizes):
            prized_set = set(prize_ids)
            packet = Counter(cards[i] for i in prize_ids)
            for draw_id in remaining:
                if draw_id in prized_set:
                    continue
                held = Counter(start)
                held[cards[draw_id]] += 1
                flags = route_flags(
                    start, held, packet, capacities, luminous_sign,
                )
                scores.update({
                    key: int(flags[key]) for key in FLAGS
                })
                worlds += 1
    return {
        key: Fraction(scores[key], worlds)
        for key in FLAGS
    }
