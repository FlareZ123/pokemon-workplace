"""Exact Raichu/Gladion access under physically reserved Ball payment policies.

Harto Miki 2024 Aichi deck counts. No clairvoyant knowledge of initial Prizes:
Computer Search can inspect the deck and take the target if unprized,
or pivot to an available Gladion when the target is Prized.
"""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations, product
from math import comb

CATEGORIES = ("T", "G", "U", "C", "R", "B", "F", "P")
POLICIES = ("strict", "spare_ultra", "computer_can_use_ultra", "any_source")
EVENTS = (
    "target_held", "ultra_paid", "computer_paid",
    "ultra_gladion", "static", "adaptive"
)


def all_prized(unseen: int, copies: int, prizes: int) -> Fraction:
    """Probability that all unseen copies occupy uniformly random Prizes."""
    if copies > prizes or copies > unseen:
        return Fraction()
    return Fraction(comb(unseen - copies, prizes - copies),
                    comb(unseen, prizes))


def source_state(
    hand: tuple[int, ...], unseen: tuple[int, ...],
    prizes: int, policy: str,
) -> dict[str, Fraction]:
    t, g, u, c, r, b, f, _ = hand
    safe = r + f
    ultra_paid = (
        u >= 1 and safe + (u - 1 if policy != "strict" else 0)
        + (c if policy == "any_source" else 0) >= 2
    )
    computer_paid = (
        c >= 1 and safe + (u if policy in (
            "computer_can_use_ultra", "any_source"
        ) else 0) >= 2
    )
    if policy not in POLICIES:
        raise ValueError("unknown source payment policy")
    if policy == "strict":
        ultra_paid = u >= 1 and safe >= 2
    hidden = sum(unseen)
    target_prized = (Fraction() if t > 0 else
                     all_prized(hidden, unseen[0], prizes))
    target_in_deck = Fraction() if t > 0 else 1 - target_prized
    prize_and_gladion_in_deck = Fraction()
    if t == 0:
        prize_and_gladion_in_deck = target_prized * (
            1 - all_prized(hidden - 1, unseen[1], prizes - 1)
        )
    if g >= 1:
        gladion_prize_access = target_prized
        computer_prize_access = Fraction()
    else:
        gladion_prize_access = Fraction()
        computer_prize_access = (
            prize_and_gladion_in_deck if computer_paid else Fraction()
        )
    already_held = Fraction(int(t > 0))
    ultra_endpoint = (already_held + (1 - already_held) * (
        gladion_prize_access + target_in_deck * int(ultra_paid)
    ))
    static = (already_held + (1 - already_held) * (
        gladion_prize_access
        + target_in_deck * int(ultra_paid or computer_paid)
    ))
    adaptive = static + (1 - already_held) * computer_prize_access
    return {
        "target_held": already_held,
        "ultra_paid": Fraction(int(ultra_paid)),
        "computer_paid": Fraction(int(computer_paid)),
        "ultra_gladion": ultra_endpoint,
        "static": static,
        "adaptive": adaptive,
    }


def raichu_prize_source_policy(
    *, deck_size: int = 60, target: int = 1, gladion: int = 2,
    ultra: int = 3, computer: int = 1, giratina: int = 1,
    other_basics: int = 15, energy: int = 11,
    opening: int = 7, prizes: int = 6,
    active_policy: str = "preserve_giratina",
) -> dict[str, Fraction]:
    counts = (
        target, gladion, ultra, computer, giratina, other_basics, energy,
        deck_size - target - gladion - ultra - computer - giratina
        - other_basics - energy
    )
    if any(type(n) is not int for n in (*counts, deck_size, opening, prizes)):
        raise TypeError("integer parameters required")
    if (min(counts) < 0 or target != 1 or giratina != 1
            or other_basics < 1 or ultra < 1 or computer != 1
            or opening < 1 or prizes < 0 or opening + prizes >= deck_size):
        raise ValueError("invalid source/category counts or setup")
    if active_policy not in ("preserve_giratina", "lead_giratina"):
        raise ValueError("unknown Active policy")
    accepted = (comb(deck_size, opening)
                - comb(deck_size - giratina - other_basics, opening))
    sums = {f"{p}_{event}": Fraction() for p in POLICIES for event in EVENTS}
    total = Fraction()
    for opener in product(*(range(min(n, opening) + 1) for n in counts)):
        if opener[4] + opener[5] == 0 or sum(opener) != opening:
            continue
        active = 4 if opener[4] and (
            active_policy == "lead_giratina" or not opener[5]
        ) else 5
        ways = 1
        for n, held in zip(counts, opener):
            ways *= comb(n, held)
        initial = Fraction(ways, accepted)
        for draw, n in enumerate(counts):
            remaining = n - opener[draw]
            if remaining == 0:
                continue
            hand = list(opener)
            hand[active] -= 1
            hand[draw] += 1
            unseen = [n - held for n, held in zip(counts, opener)]
            unseen[draw] -= 1
            weight = initial * Fraction(remaining, deck_size - opening)
            total += weight
            for policy in POLICIES:
                values = source_state(tuple(hand), tuple(unseen), prizes, policy)
                for event, val in values.items():
                    sums[f"{policy}_{event}"] += weight * val
    assert total == 1
    return sums


def brute_raichu_prize_policy(
    *, deck_size: int, target: int, gladion: int, ultra: int,
    computer: int, giratina: int, other_basics: int, energy: int,
    opening: int, prizes: int, active_policy: str,
) -> dict[str, Fraction]:
    """Independent labeled physical setup, Prizes, natural draw and searches."""
    counts = (target, gladion, ultra, computer, giratina, other_basics, energy)
    labels: list[str] = []
    for kind, count in zip(CATEGORIES, (
        *counts, deck_size - sum(counts)
    )):
        labels += [kind] * count
    indices = tuple(range(deck_size))
    tally = {f"{p}_{e}": 0 for p in POLICIES for e in EVENTS}
    worlds = 0
    for opener in combinations(indices, opening):
        if not any(labels[i] in ("R", "B") for i in opener):
            continue
        r = next((i for i in opener if labels[i] == "R"), None)
        b = next((i for i in opener if labels[i] == "B"), None)
        active = (r if active_policy == "lead_giratina" and r is not None
                  else b if b is not None else r)
        hand = set(opener)
        hand.remove(active)
        pool = tuple(i for i in indices if i not in opener)
        for prize_cards in combinations(pool, prizes):
            prize_set = set(prize_cards)
            for drawn in pool:
                if drawn in prize_set:
                    continue
                after = hand | {drawn}
                in_deck = tuple(
                    i for i in pool if i not in prize_set and i != drawn
                )
                hist = tuple(
                    sum(labels[i] == kind for i in after)
                    for kind in CATEGORIES
                )
                t, g, u, c, r, b, f, _ = hist
                target_prized = any(labels[i] == "T" for i in prize_set)
                target_deck = any(labels[i] == "T" for i in in_deck)
                gladion_deck = any(labels[i] == "G" for i in in_deck)
                worlds += 1
                for policy in POLICIES:
                    safe = r + f
                    ultra_paid = (
                        u >= 1 and safe + (u - 1 if policy != "strict" else 0)
                        + (c if policy == "any_source" else 0) >= 2
                    )
                    computer_paid = (
                        c >= 1 and safe + (u if policy in (
                            "computer_can_use_ultra", "any_source"
                        ) else 0) >= 2
                    )
                    ul = (t > 0 or (target_prized and g > 0)
                          or (target_deck and ultra_paid))
                    st = (t > 0 or (target_prized and g > 0)
                          or (target_deck and (ultra_paid or computer_paid)))
                    ad = st or (
                        target_prized and g == 0
                        and computer_paid and gladion_deck
                    )
                    values = dict(
                        target_held=t > 0, ultra_paid=ultra_paid,
                        computer_paid=computer_paid, ultra_gladion=ul,
                        static=st, adaptive=ad
                    )
                    for event, yes in values.items():
                        tally[f"{policy}_{event}"] += yes
    return {k: Fraction(v, worlds) for k, v in tally.items()}
