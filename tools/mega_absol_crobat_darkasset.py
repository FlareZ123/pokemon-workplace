"""Exact first-turn Dark Asset activation with physical entry and payment gates.

Uses an actual Basic-valid seven-card opener, six Prizes and one natural
draw, with empty initial Bench and a fixed hand of seven after starting Active.
Only enumerated immediate routes are credited. A payable Quick Ball, Ultra
Ball or Pokémon Communication may retrieve Crobat V from the draw deck;
a held Hisuian Heavy Ball may retrieve a Prized Crobat. Battle VIP Pass puts
Crobat directly onto the Bench and does NOT trigger Dark Asset.
"""
from __future__ import annotations

from collections import Counter
from fractions import Fraction
from itertools import combinations
from math import comb

from tools.mega_absol_named_item_access import _hands
from tools.mega_absol_stone_bridge import CATEGORIES

POLICIES = (
    "crobat_seen", "forced_active", "direct_bench_entry",
    "direct_positive", "quick_positive", "ultra_positive",
    "communication_positive", "heavy_entry", "heavy_positive",
    "vip_board_only", "positive_union",
)


def route_flags(
    starting: dict[str, int],
    held: dict[str, int],
    drawn: str,
    prized_crobat: int,
    capacities: dict[str, int],
) -> dict[str, bool]:
    """Executable restricted paths, including hand count after payment."""
    other_start_basics = starting["mega"] + starting["other_basic"]
    other_held_basics = held["mega"] + held["other_basic"]
    # A held opening Crobat needs another opening Basic to avoid forced Active.
    # A naturally drawn Crobat always has a different initial Active Pokémon.
    direct = held["crobat"] > 0 and (
        other_start_basics > 0 or drawn == "crobat"
    )
    forced_active = starting["crobat"] > 0 and other_start_basics == 0
    # One manual Energy attachment or one spare Basic played onto the Bench
    # reduces initial post-Active/post-draw hand 7 -> 6. Playing Crobat
    # subsequently leaves hand 5, enabling a one-card Dark Asset draw.
    free_shrink = held["energy"] > 0 or other_held_basics > 1
    crobat_in_deck = (
        capacities["crobat"] > held["crobat"] + prized_crobat
    )
    # QB/U/Communication item use + card payment + Crobat bench entry
    # leave hand at 5/4/5 respectively, without further optional actions.
    quick = (
        crobat_in_deck and held["quick_ball"] > 0
        and held["energy"] >= 1
    )
    ultra = (
        crobat_in_deck and held["ultra_ball"] > 0
        and held["energy"] >= 2
    )
    exchangeable_pokemon = (
        other_held_basics + held["evolution"] - 1
    )
    communication = (
        crobat_in_deck and held["communication"] > 0
        and exchangeable_pokemon >= 1
    )
    heavy = prized_crobat > 0 and held["heavy_ball"] > 0
    return {
        "crobat_seen": held["crobat"] > 0,
        "forced_active": forced_active,
        "direct_bench_entry": direct,
        "direct_positive": direct and free_shrink,
        "quick_positive": quick,
        "ultra_positive": ultra,
        "communication_positive": communication,
        "heavy_entry": heavy,
        "heavy_positive": heavy and free_shrink,
        "vip_board_only": crobat_in_deck and held["vip_pass"] > 0,
        "positive_union": (
            (direct and free_shrink) or quick or ultra
            or communication or (heavy and free_shrink)
        ),
    }


def exact_access(
    capacities: dict[str, int], opening: int = 7, prizes: int = 6,
) -> dict[str, Fraction]:
    assert tuple(capacities) == CATEGORIES
    n = sum(capacities.values())
    assert 0 < opening < n - prizes
    scores = Counter()
    accepted = 0
    prize_denominator = comb(n - opening - 1, prizes)
    for start, ways in _hands(capacities, opening):
        if start["mega"] + start["other_basic"] + start["crobat"] == 0:
            continue
        for drawn in CATEGORIES:
            count = capacities[drawn] - start[drawn]
            if not count:
                continue
            held = start.copy()
            held[drawn] += 1
            weight = ways * count
            accepted += weight
            remaining_crobat = capacities["crobat"] - held["crobat"]
            for prized_crobat in range(min(prizes, remaining_crobat) + 1):
                prize_weight = (
                    comb(remaining_crobat, prized_crobat)
                    * comb(
                        n - opening - 1 - remaining_crobat,
                        prizes - prized_crobat,
                    )
                )
                flags = route_flags(
                    start, held, drawn, prized_crobat, capacities,
                )
                for key in POLICIES:
                    scores[key] += weight * prize_weight * flags[key]
    assert accepted
    return {
        key: Fraction(scores[key], accepted * prize_denominator)
        for key in POLICIES
    }


def physical_oracle(
    capacities: dict[str, int], opening: int, prizes: int,
) -> dict[str, Fraction]:
    """Independent labeled physical dealing, hand -> Prizes -> one draw."""
    assert tuple(capacities) == CATEGORIES
    cards = [name for name in CATEGORIES for _ in range(capacities[name])]
    n = len(cards)
    scores = Counter()
    worlds = 0
    for opener_ids in combinations(range(n), opening):
        starting = Counter(cards[i] for i in opener_ids)
        if not (
            starting["mega"] + starting["other_basic"] + starting["crobat"]
        ):
            continue
        hand_set = set(opener_ids)
        remaining = [i for i in range(n) if i not in hand_set]
        for prize_ids in combinations(remaining, prizes):
            prize_set = set(prize_ids)
            prized_crobat = sum(cards[i] == "crobat" for i in prize_ids)
            for draw_id in remaining:
                if draw_id in prize_set:
                    continue
                held = Counter(starting)
                held[cards[draw_id]] += 1
                flags = route_flags(
                    starting, held, cards[draw_id], prized_crobat,
                    capacities,
                )
                scores.update({key: int(flags[key]) for key in POLICIES})
                worlds += 1
    return {key: Fraction(scores[key], worlds) for key in POLICIES}
