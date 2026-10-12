"""Exact joint Ultra Ball/Computer Search first-turn payment in Harto Raichu.

Source-group sizes follow Harto Miki's Aichi 2024 Raichu/Electrode list.
Giratina is simultaneously a starting Basic and a discard-favorable card.
No searched target or later search output is modeled by this gate.
"""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations, product
from math import comb

EVENTS = (
    "ultra_held", "computer_held", "either_held", "discard_two_held",
    "ultra_strict", "computer_strict", "either_strict", "both_strict",
    "ultra_spares", "computer_spares", "either_spares", "both_spares",
    "ultra_all_sources", "computer_all_sources", "either_all_sources",
    "both_all_sources", "either_extra_basics", "both_extra_basics",
)


def event_flags(hand: tuple[int, ...]) -> dict[str, bool]:
    g, b, f, u, c, _ = hand
    safe = g + f
    has_both = u >= 1 and c >= 1
    has_u = u >= 1
    has_c = c >= 1
    values = (
        has_u, has_c, has_u or has_c, safe >= 2,
        has_u and safe >= 2,
        has_c and safe >= 2,
        (has_u or has_c) and safe >= 2,
        has_both and safe >= 4,
        has_u and safe + (u - 1) >= 2,
        has_c and safe >= 2,
        (has_u and safe + u - 1 >= 2) or (has_c and safe >= 2),
        has_both and safe + u - 1 >= 4,
        has_u and safe + u - 1 + c >= 2,
        has_c and safe + u >= 2,
        (has_u and safe + u - 1 + c >= 2) or (has_c and safe + u >= 2),
        has_both and safe + u - 1 >= 4,
        (has_u and safe + u - 1 + c + b >= 2)
        or (has_c and safe + u + b >= 2),
        has_both and safe + u - 1 + b >= 4,
    )
    return dict(zip(EVENTS, values))


def raichu_multi_search_gate(
    *, deck_size: int = 60, giratina: int = 1, other_basics: int = 15,
    energy: int = 11, ultra: int = 3, computer: int = 1,
    opening: int = 7, prizes: int = 6,
    active_policy: str = "preserve_giratina",
) -> dict[str, Fraction]:
    """Basic-valid initial seven, one Active, six Prizes and one draw.

    preserve_giratina promotes a different Basic if one is available.
    lead_giratina instead promotes Giratina whenever it appeared initially.
    """
    counts = (giratina, other_basics, energy, ultra, computer,
              deck_size - giratina - other_basics - energy - ultra - computer)
    if any(type(n) is not int for n in (*counts, deck_size, opening, prizes)):
        raise TypeError("integer parameters required")
    if (min(counts) < 0 or giratina != 1 or other_basics < 1 or ultra < 1
            or computer != 1 or opening < 1 or prizes < 0
            or opening + prizes >= deck_size):
        raise ValueError("invalid deck or setup configuration")
    if active_policy not in ("preserve_giratina", "lead_giratina"):
        raise ValueError("unknown Active selection policy")
    accepted = (comb(deck_size, opening)
                - comb(deck_size - giratina - other_basics, opening))
    tally = {name: Fraction() for name in EVENTS}
    total = Fraction()
    for opener in product(*(range(min(n, opening) + 1) for n in counts)):
        if opener[0] + opener[1] == 0 or sum(opener) != opening:
            continue
        lead_g = (opener[0] > 0 and (
            active_policy == "lead_giratina" or opener[1] == 0
        ))
        active_category = 0 if lead_g else 1
        ways = 1
        for n, held in zip(counts, opener):
            ways *= comb(n, held)
        opener_weight = Fraction(ways, accepted)
        for drawn, n in enumerate(counts):
            available = n - opener[drawn]
            if available == 0:
                continue
            hand = list(opener)
            hand[active_category] -= 1
            hand[drawn] += 1
            weight = opener_weight * Fraction(available, deck_size - opening)
            total += weight
            for name, yes in event_flags(tuple(hand)).items():
                if yes:
                    tally[name] += weight
    assert total == 1
    return tally


def brute_raichu_gate(
    *, deck_size: int, giratina: int, other_basics: int,
    energy: int, ultra: int, computer: int, opening: int, prizes: int,
    active_policy: str,
) -> dict[str, Fraction]:
    """Independent physical opener/Prize/draw/Active choice enumerator."""
    labels = (["G"] * giratina + ["B"] * other_basics
              + ["F"] * energy + ["U"] * ultra + ["C"] * computer)
    labels += ["P"] * (deck_size - len(labels))
    ids = tuple(range(deck_size))
    tally = {name: 0 for name in EVENTS}
    worlds = 0
    for dealt in combinations(ids, opening):
        if not any(labels[i] in ("G", "B") for i in dealt):
            continue
        g = next((i for i in dealt if labels[i] == "G"), None)
        b = next((i for i in dealt if labels[i] == "B"), None)
        active = (g if active_policy == "lead_giratina" and g is not None
                  else b if b is not None else g)
        hand = set(dealt)
        hand.remove(active)
        unseen = tuple(i for i in ids if i not in dealt)
        for prize in combinations(unseen, prizes):
            prize_set = set(prize)
            for drawn in unseen:
                if drawn in prize_set:
                    continue
                final = hand | {drawn}
                histogram = tuple(
                    sum(labels[i] == k for i in final)
                    for k in ("G", "B", "F", "U", "C", "P")
                )
                worlds += 1
                for name, yes in event_flags(histogram).items():
                    tally[name] += yes
    return {name: Fraction(count, worlds) for name, count in tally.items()}
