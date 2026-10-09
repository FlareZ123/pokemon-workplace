"""Exact K0/K1 information value of discarding a held Tool to thin a deck.

Toy channel:
- U unseen, exchangeable cards, of which P will be Prized.
- 1 backup Tool and 1 desired Ticket/Map target among those U.
- The player also holds one Tool (a guaranteed setup resource).
- G&H can fetch the backup only by first discarding the held Tool.
- If no replacement is fetched, the intended attack setup fails.
- A later Jirachi Stellar Wish inspects s uniformly sampled deck cards.
- All other prerequisites, including the optional two-card discard, are
  assumed to be available and have no opportunity cost.

This isolates first-full-search information, not an entire Aichi turn.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations


@dataclass(frozen=True)
class Values:
    k0_keep_setup: Fraction
    k0_replace_setup: Fraction
    k0_keep_joint: Fraction
    k0_replace_joint: Fraction
    k1_oracle_setup: Fraction
    k1_oracle_joint: Fraction
    k1_information_premium: Fraction


def exact(unseen: int, prizes: int, stellar_cards: int) -> Values:
    """Return exact unconditional probabilities over Prize placements and Wish."""
    if not (unseen >= 3 and 0 <= prizes <= unseen - 2):
        raise ValueError("Require at least two physically distinct unseen resources")
    d = unseen - prizes
    if not (1 <= stellar_cards <= d - 1):
        raise ValueError("Wish sample must fit even after backup Tool search")
    keep = Fraction(stellar_cards, unseen)
    replace = Fraction(stellar_cards * d, unseen * (unseen - 1))
    extra = Fraction(stellar_cards, unseen * (unseen - 1))
    return Values(
        k0_keep_setup=Fraction(1),
        k0_replace_setup=Fraction(d, unseen),
        k0_keep_joint=keep,
        k0_replace_joint=replace,
        k1_oracle_setup=Fraction(1),
        k1_oracle_joint=keep + extra,
        k1_information_premium=extra,
    )


def brute_force(unseen: int, prizes: int, stellar_cards: int) -> Values:
    """Independent labeled-Prize enumeration, averaging conditional Wish hits.

    Physical labels: 0=backup Tool, 1=Ticket/Map target, >=2=filler.
    """
    d = unseen - prizes
    if not 1 <= stellar_cards <= d - 1:
        raise ValueError("Invalid sample")
    sums = [Fraction(0) for _ in range(6)]
    worlds = 0
    for prized in combinations(range(unseen), prizes):
        ps = set(prized)
        backup = 0 not in ps
        ticket = 1 not in ps
        keep_hit = Fraction(stellar_cards, d) if ticket else Fraction(0)
        replace_hit = (Fraction(stellar_cards, d - 1)
                       if backup and ticket else Fraction(0))
        # Informed player only replaces the held Tool when both resources
        # are known to be in the deck and doing so improves Ticket access.
        informed_hit = replace_hit if backup and ticket else keep_hit
        row = (
            Fraction(1),
            Fraction(int(backup)),
            keep_hit,
            replace_hit,
            Fraction(1),
            informed_hit,
        )
        sums = [a + b for a, b in zip(sums, row)]
        worlds += 1
    result = [value / worlds for value in sums]
    return Values(*result, result[5] - result[2])


def describe(unseen: int = 52, prizes: int = 6, stellar_cards: int = 5) -> str:
    x = exact(unseen, prizes, stellar_cards)
    pairs = (
        ("Keep held Tool: setup", x.k0_keep_setup),
        ("Replace Tool blindly: setup", x.k0_replace_setup),
        ("Keep Tool: setup AND Ticket hit", x.k0_keep_joint),
        ("Replace Tool blindly: setup AND Ticket hit", x.k0_replace_joint),
        ("K1-adaptive: setup AND Ticket hit", x.k1_oracle_joint),
        ("K1 information premium", x.k1_information_premium),
    )
    return (f"U={unseen} P={prizes} s={stellar_cards} D={unseen-prizes}\n"
            + "\n".join(f"{name}: {value} = {100*float(value):.9f}%"
                        for name, value in pairs))


if __name__ == "__main__":
    print(describe())
