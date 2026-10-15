"""Forest Seal Stone overlap with all-eight-Supporter Absol tutor access.

Joint physical opening/draw/Prize solver, separately tracks Tapu Lele-GX,
Crobat/Lumineon V as the single Stone host, Forest Seal Stone and Adventure
Bag. One named Item or a held VSTAR Tool, no multi-Item chaining.
"""
from __future__ import annotations

from collections import Counter
from fractions import Fraction
from itertools import combinations
from math import comb

from tools.absol_support_tutor_frontier import (
    CATEGORIES as BASE_CATEGORIES,
    ITEMS, SUPPORTERS, MEGA, TAPU_LELE, CROBAT, LUMINEON,
    route_flags as supporter_route_flags,
)
from tools.mega_absol_named_item_access import _hands

STONE = "swsh12-156"
BAG = "sm8-167"
CATEGORIES = (
    "mega", "other_basic", "lele", "host", "evolution", "quick_ball",
    "ultra_ball", "communication", "heavy_ball", "energy",
    "supporter", "stone", "bag", "filler",
)
OUTCOMES = (
    "held_supporter", "tutor_or_held", "stone_direct",
    "stone_prize", "stone_deck", "stone_any",
    "stone_new_when_tutor_fails", "held_tutor_or_stone",
)


def category_counts(quantities: dict[str, int], records: dict) -> dict[str, int]:
    """Every physical print maps to exactly one category."""
    assert quantities.get(STONE) == quantities.get(BAG) == 1
    assert quantities.get(TAPU_LELE) == 1
    assert quantities.get(CROBAT, 0) + quantities.get(LUMINEON, 0) == 1
    result = Counter({name: 0 for name in CATEGORIES})
    for card_id, qty in quantities.items():
        card = records[card_id]
        if card_id == MEGA:
            role = "mega"
        elif card_id == TAPU_LELE:
            role = "lele"
        elif card_id in (CROBAT, LUMINEON):
            role = "host"
        elif card_id == STONE:
            role = "stone"
        elif card_id == BAG:
            role = "bag"
        elif card_id in ITEMS:
            role = ITEMS[card_id]
        elif card_id in SUPPORTERS:
            role = "supporter"
        elif card.is_basic_pokemon:
            role = "other_basic"
        elif card.supertype == "Pokémon":
            role = "evolution"
        elif card.supertype == "Energy":
            role = "energy"
        else:
            role = "filler"
        result[role] += qty
    out = {name: result[name] for name in CATEGORIES}
    assert sum(out.values()) == 60
    assert out["mega"] == 2 and out["supporter"] == 8
    return out


def collapse_roles(state: dict[str, int], luminous_sign: bool) -> dict[str, int]:
    """Map a complete physical role partition onto the old Tutor-only solver."""
    out = {
        key: state[key]
        for key in BASE_CATEGORIES
        if key not in ("tutor", "other_basic", "filler")
    }
    out["tutor"] = state["lele"] + (state["host"] if luminous_sign else 0)
    out["other_basic"] = state["other_basic"] + (
        0 if luminous_sign else state["host"]
    )
    out["filler"] = state["filler"] + state["stone"] + state["bag"]
    return {key: out[key] for key in BASE_CATEGORIES}


def route_flags(
    starting: dict[str, int],
    held: dict[str, int],
    drawn: str,
    prized: dict[str, int],
    capacities: dict[str, int],
    luminous_sign: bool,
) -> dict[str, bool]:
    """Independent legal strategies share a one-Item cap, not cumulative cost."""
    def old_roles(d: dict[str, int]) -> dict[str, int]:
        return collapse_roles(d, luminous_sign)
    old_drawn = (
        "tutor" if drawn == "lele" or (luminous_sign and drawn == "host")
        else "other_basic" if drawn == "host" else
        "filler" if drawn in ("stone", "bag") else drawn
    )
    tutor_prized = prized["lele"] + (
        prized["host"] if luminous_sign else 0
    )
    named = supporter_route_flags(
        old_roles(starting), old_roles(held), old_drawn,
        tutor_prized, prized["supporter"], old_roles(capacities),
    )["held_or_search_supporter"]
    target_live = (
        capacities["supporter"] > held["supporter"] + prized["supporter"]
    )
    stone_available = held["stone"] > 0 or (
        held["bag"] > 0
        and capacities["stone"] > held["stone"] + prized["stone"]
    )
    host_held = held["host"] > 0
    host_prized = prized["host"] > 0
    host_deck = (
        capacities["host"] > held["host"] + prized["host"]
    )
    spare_pokemon = (
        held["mega"] + held["other_basic"] + held["lele"] +
        held["host"] + held["evolution"] - 1
    )
    paid_body = (
        held["quick_ball"] > 0 and held["energy"] >= 1
        or held["ultra_ball"] > 0 and held["energy"] >= 2
        or held["communication"] > 0 and spare_pokemon >= 1
    )
    # A held host works from Active or Bench. Adventure Bag may supply
    # Stone only when the host is already held: a second search Item to
    # fetch the host would exceed this study's one-Item route budget.
    direct = bool(target_live and host_held and stone_available)
    prize = bool(
        target_live and host_prized and held["stone"] > 0
        and held["heavy_ball"] > 0
    )
    deck = bool(
        target_live and host_deck and held["stone"] > 0 and paid_body
    )
    stone = direct or prize or deck
    return {
        "held_supporter": held["supporter"] > 0,
        "tutor_or_held": bool(named),
        "stone_direct": direct,
        "stone_prize": prize,
        "stone_deck": deck,
        "stone_any": stone,
        "stone_new_when_tutor_fails": bool(stone and not named),
        "held_tutor_or_stone": bool(named or stone),
    }


def exact_access(
    capacities: dict[str, int], luminous_sign: bool,
    opening: int = 7, prizes: int = 6,
) -> dict[str, Fraction]:
    assert tuple(capacities) == CATEGORIES
    n = sum(capacities.values())
    assert 0 < opening < n - prizes
    accepted, scores = 0, Counter()
    prize_denominator = comb(n - opening - 1, prizes)
    for start, ways in _hands(capacities, opening):
        if start["mega"] + start["other_basic"] + start["lele"] + start["host"] == 0:
            continue
        for drawn in CATEGORIES:
            drawn_count = capacities[drawn] - start[drawn]
            if not drawn_count:
                continue
            held = start.copy()
            held[drawn] += 1
            hand_weight = ways * drawn_count
            accepted += hand_weight
            rem = {key: capacities[key] - held[key] for key in CATEGORIES}
            other = (
                n - opening - 1 - rem["supporter"] - rem["lele"]
                - rem["host"] - rem["stone"]
            )
            for ps in range(min(prizes, rem["supporter"]) + 1):
                for pl in range(min(prizes - ps, rem["lele"]) + 1):
                    for ph in range(min(prizes - ps - pl, rem["host"]) + 1):
                        for pt in range(min(prizes - ps - pl - ph, rem["stone"]) + 1):
                            remain = prizes - ps - pl - ph - pt
                            if remain > other:
                                continue
                            prize_weight = (
                                comb(rem["supporter"], ps) *
                                comb(rem["lele"], pl) *
                                comb(rem["host"], ph) *
                                comb(rem["stone"], pt) *
                                comb(other, remain)
                            )
                            flags = route_flags(
                                start, held, drawn,
                                {"supporter": ps, "lele": pl,
                                 "host": ph, "stone": pt},
                                capacities, luminous_sign,
                            )
                            for key in OUTCOMES:
                                scores[key] += hand_weight * prize_weight * flags[key]
    total = accepted * prize_denominator
    assert total > 0
    return {key: Fraction(scores[key], total) for key in OUTCOMES}


def physical_oracle(
    capacities: dict[str, int], luminous_sign: bool, opening: int, prizes: int,
) -> dict[str, Fraction]:
    """An independent labeled-card enumeration in true setup deal order."""
    assert tuple(capacities) == CATEGORIES
    physical = [key for key in CATEGORIES for _ in range(capacities[key])]
    worlds, scores = 0, Counter()
    for hand_ids in combinations(range(len(physical)), opening):
        initial = Counter(physical[i] for i in hand_ids)
        if not initial["mega"] + initial["other_basic"] + initial["lele"] + initial["host"]:
            continue
        start = {name: initial[name] for name in CATEGORIES}
        taken = set(hand_ids)
        rest = [i for i in range(len(physical)) if i not in taken]
        for prize_ids in combinations(rest, prizes):
            prize_set = set(prize_ids)
            prized = Counter(physical[i] for i in prize_ids)
            for draw_id in rest:
                if draw_id in prize_set:
                    continue
                held = start.copy()
                held[physical[draw_id]] += 1
                result = route_flags(
                    start, held, physical[draw_id], prized,
                    capacities, luminous_sign,
                )
                scores.update({name: int(result[name]) for name in OUTCOMES})
                worlds += 1
    assert worlds > 0
    return {name: Fraction(scores[name], worlds) for name in OUTCOMES}
