"""Exact first-turn Supporter-tutor frontier for Aichi Mega Absol / Garbodor.

Compares original single Wonder Tag tutor (Tapu Lele-GX) with a second
Luminous Sign tutor (Lumineon V instead of Crobat V). Enumerates Basic-valid
seven-card opening hands, a single natural draw, six random Prizes, and one
independently payable basic-search Item. A search effect must bring the Basic
tutor into HAND before hand-to-Bench Ability activation.

This is a restricted material-access endpoint, NOT a match-winning estimate.
"""
from __future__ import annotations

from collections import Counter
from fractions import Fraction
from itertools import combinations
from math import comb

from tools.mega_absol_named_item_access import _hands

CATEGORIES = (
    "mega", "other_basic", "tutor", "evolution", "quick_ball",
    "ultra_ball", "communication", "heavy_ball", "energy",
    "supporter", "filler",
)
OUTCOMES = (
    "direct", "quick", "ultra", "communication", "heavy",
    "ability_entry", "supporter_search", "supporter_held",
    "new_supporter_when_none_held", "held_or_search_supporter",
)
MEGA = "me1-86"
TAPU_LELE = "sm2-60"
CROBAT = "swsh3-104"
LUMINEON = "swsh9-40"
ITEMS = {
    "swsh1-179": "quick_ball",
    "swsh9-150": "ultra_ball",
    "sm9-152": "communication",
    "swsh10-146": "heavy_ball",
}
SUPPORTERS = frozenset({
    "me1-119", "sv6-145", "sv2-185", "swsh10-150",
    "sm3-115", "sv7-133", "xy6-94", "xyp-XY177",
})


def category_counts(quantities: dict[str, int], records: dict) -> dict[str, int]:
    """Partition each source-verified physical copy into exclusive types."""
    counter = Counter({name: 0 for name in CATEGORIES})
    for card_id, qty in quantities.items():
        card = records[card_id]
        if card_id == MEGA:
            role = "mega"
        elif card_id in (TAPU_LELE, LUMINEON):
            role = "tutor"
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
        counter[role] += qty
    result = {name: counter[name] for name in CATEGORIES}
    assert sum(result.values()) == 60
    assert result["mega"] == 2 and result["supporter"] == 8
    return result


def route_flags(
    start: dict[str, int],
    held: dict[str, int],
    drawn: str,
    prized_tutors: int,
    prized_supporters: int,
    capacities: dict[str, int],
) -> dict[str, bool]:
    """Restricted physically payable and correctly triggered tutor paths."""
    opening_basics = start["mega"] + start["other_basic"] + start["tutor"]
    assert opening_basics > 0
    # If one Tutor is the only initial Basic, it must start Active.
    # Drawing a second Tutor or initially holding two Basics fixes this.
    direct = held["tutor"] > 0 and (opening_basics >= 2 or drawn == "tutor")
    tutor_in_deck = capacities["tutor"] > held["tutor"] + prized_tutors
    quick = (
        tutor_in_deck and held["quick_ball"] > 0 and held["energy"] >= 1
    )
    ultra = (
        tutor_in_deck and held["ultra_ball"] > 0 and held["energy"] >= 2
    )
    spare_pokemon = (
        held["mega"] + held["other_basic"] + held["tutor"]
        + held["evolution"] - 1
    )
    communication = (
        tutor_in_deck and held["communication"] > 0 and spare_pokemon >= 1
    )
    heavy = prized_tutors > 0 and held["heavy_ball"] > 0
    entry = bool(direct or quick or ultra or communication or heavy)
    supporter_in_deck = (
        capacities["supporter"] > held["supporter"] + prized_supporters
    )
    supporter_search = bool(entry and supporter_in_deck)
    supporter_held = held["supporter"] > 0
    return {
        "direct": bool(direct),
        "quick": bool(quick),
        "ultra": bool(ultra),
        "communication": bool(communication),
        "heavy": bool(heavy),
        "ability_entry": entry,
        "supporter_search": supporter_search,
        "supporter_held": supporter_held,
        "new_supporter_when_none_held": bool(
            supporter_search and not supporter_held
        ),
        "held_or_search_supporter": bool(
            supporter_held or supporter_search
        ),
    }


def exact_access(
    capacities: dict[str, int], opening: int = 7, prizes: int = 6,
) -> dict[str, Fraction]:
    assert tuple(capacities) == CATEGORIES
    n = sum(capacities.values())
    assert 0 < opening < n - prizes
    accepted = 0
    scores = Counter()
    prize_denominator = comb(n - opening - 1, prizes)
    remaining_count = n - opening - 1

    for start, ways in _hands(capacities, opening):
        if start["mega"] + start["other_basic"] + start["tutor"] == 0:
            continue
        for drawn in CATEGORIES:
            count = capacities[drawn] - start[drawn]
            if count <= 0:
                continue
            held = start.copy()
            held[drawn] += 1
            accepted += ways * count
            remaining_tutors = capacities["tutor"] - held["tutor"]
            remaining_supporters = capacities["supporter"] - held["supporter"]
            remaining_other = (
                remaining_count - remaining_tutors - remaining_supporters
            )
            for pt in range(min(prizes, remaining_tutors) + 1):
                for ps in range(min(prizes - pt, remaining_supporters) + 1):
                    rest = prizes - pt - ps
                    if rest > remaining_other:
                        continue
                    weight = (
                        ways * count * comb(remaining_tutors, pt)
                        * comb(remaining_supporters, ps)
                        * comb(remaining_other, rest)
                    )
                    flags = route_flags(
                        start, held, drawn, pt, ps, capacities,
                    )
                    for key in OUTCOMES:
                        scores[key] += weight * flags[key]
    denominator = accepted * prize_denominator
    assert denominator > 0
    return {
        key: Fraction(scores[key], denominator)
        for key in OUTCOMES
    }


def physical_oracle(
    capacities: dict[str, int], opening: int, prizes: int,
) -> dict[str, Fraction]:
    """Independent labeled real-deal enumeration: hand, Prize, first draw."""
    assert tuple(capacities) == CATEGORIES
    cards = [name for name in CATEGORIES for _ in range(capacities[name])]
    counts = Counter()
    worlds = 0
    for hand_ids in combinations(range(len(cards)), opening):
        initial = Counter(cards[i] for i in hand_ids)
        if initial["mega"] + initial["other_basic"] + initial["tutor"] == 0:
            continue
        starting = {name: initial[name] for name in CATEGORIES}
        hand_set = set(hand_ids)
        remaining = [i for i in range(len(cards)) if i not in hand_set]
        for prize_ids in combinations(remaining, prizes):
            prize_set = set(prize_ids)
            pt = sum(cards[i] == "tutor" for i in prize_ids)
            ps = sum(cards[i] == "supporter" for i in prize_ids)
            for draw_id in remaining:
                if draw_id in prize_set:
                    continue
                held = starting.copy()
                held[cards[draw_id]] += 1
                flags = route_flags(
                    starting, held, cards[draw_id], pt, ps, capacities,
                )
                counts.update(key for key in OUTCOMES if flags[key])
                worlds += 1
    assert worlds > 0
    return {
        key: Fraction(counts[key], worlds)
        for key in OUTCOMES
    }
