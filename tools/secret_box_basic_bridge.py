"""Exact first-draw Basic-search access through typed Ball and Secret Box paths.

Direct: held Quick Ball + 1 safe discard or held Ultra Ball + 2.
Indirect: held Secret Box + 4 safe discard cards, Quick Ball available
in the unprized deck, and a Basic Pokemon available in that deck.
This excludes Item lock, search-output reuse beyond the fetched Quick Ball,
and all optional Bench setup.
"""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations, product
from math import comb

EVENTS = ("direct_basic", "secret_bridge_basic", "incremental_bridge",
          "combined_basic", "bridge_pre_prize")


def all_prized(*, unseen: int, copies: int, prizes: int) -> Fraction:
    """Chance all copies among unseen cards are in random Prizes."""
    if copies > prizes or copies > unseen:
        return Fraction()
    return Fraction(comb(unseen - copies, prizes - copies),
                    comb(unseen, prizes))


def exact_basic_bridge(
    *, deck_size: int = 60, basics: int = 12, quick: int = 4,
    ultra: int = 4, secret: int = 1, filler: int = 8,
    opening: int = 7, prizes: int = 6,
) -> dict[str, Fraction]:
    """Return exact joint basic-search endpoints after Basic-valid setup."""
    counts = (basics, quick, ultra, secret, filler,
              deck_size - basics - quick - ultra - secret - filler)
    if any(type(n) is not int for n in (*counts, deck_size, opening, prizes)):
        raise TypeError("integer parameters required")
    if (min(counts) < 0 or basics < 1 or quick < 1 or ultra < 1
            or secret != 1 or opening < 1 or prizes < 0
            or opening + prizes >= deck_size):
        raise ValueError("invalid card groups or setup")
    accepted = comb(deck_size, opening) - comb(deck_size - basics, opening)
    if accepted <= 0:
        raise ValueError("no valid opener")
    tally = {name: Fraction() for name in EVENTS}
    total = Fraction()
    for opener in product(*(range(min(n, opening) + 1) for n in counts)):
        if not opener[0] or sum(opener) != opening:
            continue
        ways = 1
        for n, held in zip(counts, opener):
            ways *= comb(n, held)
        initial = Fraction(ways, accepted)
        for drawn, n in enumerate(counts):
            remaining = n - opener[drawn]
            if not remaining:
                continue
            hand = list(opener)
            hand[0] -= 1  # One Basic goes Active.
            hand[drawn] += 1
            unseen = [n - held for n, held in zip(counts, opener)]
            unseen[drawn] -= 1
            _, q, u, s, f, _ = hand
            hidden = deck_size - opening - 1
            basic_available = 1 - all_prized(
                unseen=hidden, copies=unseen[0], prizes=prizes
            )
            quick_available = 1 - all_prized(
                unseen=hidden, copies=unseen[1], prizes=prizes
            )
            both_available = (
                basic_available + quick_available - 1
                + all_prized(unseen=hidden,
                             copies=unseen[0] + unseen[1], prizes=prizes)
            )
            direct = (q >= 1 and f >= 1) or (u >= 1 and f >= 2)
            bridge = s >= 1 and f >= 4
            weight = initial * Fraction(remaining, deck_size - opening)
            total += weight
            if direct:
                tally["direct_basic"] += weight * basic_available
            if bridge:
                tally["bridge_pre_prize"] += weight
                tally["secret_bridge_basic"] += weight * both_available
                if not direct:
                    tally["incremental_bridge"] += weight * both_available
            tally["combined_basic"] += weight * (
                basic_available if direct else both_available if bridge else 0
            )
    assert total == 1
    assert (tally["combined_basic"]
            == tally["direct_basic"] + tally["incremental_bridge"])
    return tally


def brute_basic_bridge(
    *, deck_size: int, basics: int, quick: int, ultra: int,
    secret: int, filler: int, opening: int, prizes: int,
) -> dict[str, Fraction]:
    """Independent enumerator of labeled openers, Prize slots and top draws."""
    labels = (["B"] * basics + ["Q"] * quick + ["U"] * ultra
              + ["S"] * secret + ["F"] * filler)
    labels += ["P"] * (deck_size - len(labels))
    indices = tuple(range(deck_size))
    tally = {event: 0 for event in EVENTS}
    worlds = 0
    for dealt in combinations(indices, opening):
        if not any(labels[i] == "B" for i in dealt):
            continue
        hand = set(dealt)
        active = next(i for i in dealt if labels[i] == "B")
        hand.remove(active)
        unseen = tuple(i for i in indices if i not in dealt)
        for prize in combinations(unseen, prizes):
            prize_set = set(prize)
            for drawn in unseen:
                if drawn in prize_set:
                    continue
                after = hand | {drawn}
                deck = tuple(i for i in unseen if i not in prize_set and i != drawn)
                target = any(labels[i] == "B" for i in deck)
                quick_in_deck = any(labels[i] == "Q" for i in deck)
                held_quick = sum(labels[i] == "Q" for i in after) > 0
                held_ultra = sum(labels[i] == "U" for i in after) > 0
                held_secret = sum(labels[i] == "S" for i in after) > 0
                safe = sum(labels[i] == "F" for i in after)
                direct = (held_quick and safe >= 1) or (
                    held_ultra and safe >= 2)
                bridge_ready = held_secret and safe >= 4
                bridge = bridge_ready and quick_in_deck and target
                outcomes = {
                    "direct_basic": direct and target,
                    "secret_bridge_basic": bridge,
                    "incremental_bridge": bridge and not direct,
                    "combined_basic": target and (direct or bridge),
                    "bridge_pre_prize": bridge_ready,
                }
                worlds += 1
                for name, yes in outcomes.items():
                    tally[name] += yes
    return {name: Fraction(value, worlds) for name, value in tally.items()}
