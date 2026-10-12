"""Exact Prize-aware Guzma & Hala discard feasibility for Iron Thorns ex.

This is a named attack-resource sensitivity model, not a match simulator.
Designated safe cards are a hypothetical user-supplied discardability class.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from math import comb, prod


@dataclass(frozen=True)
class Counts:
    n: int = 60
    iron: int = 4
    tag: int = 2
    gh: int = 2
    mountain: int = 1
    dce: int = 2
    safe: int = 12
    opener: int = 7
    prizes: int = 6

    @property
    def cats(self) -> tuple[int, ...]:
        protected = self.n - sum(
            (self.iron, self.tag, self.gh, self.mountain, self.dce, self.safe)
        )
        if protected < 0:
            raise ValueError("Count exceeds deck")
        return (
            self.iron, self.tag, self.gh, self.mountain,
            self.dce, self.safe, protected,
        )


def allocations(total: int, caps: tuple[int, ...]):
    choices = [0] * len(caps)

    def walk(i: int, left: int):
        if i == len(caps) - 1:
            if 0 <= left <= caps[i]:
                choices[i] = left
                yield tuple(choices)
            return
        for k in range(min(caps[i], left) + 1):
            choices[i] = k
            yield from walk(i + 1, left - k)

    yield from walk(0, total)


def exact(counts: Counts) -> dict[str, Fraction]:
    """Exact conditional masses under ideal, strict, and spare-connector DCI.

    The first natural draw is marginally uniform among 53 post-opening cards.
    Given that card, the six Prizes are uniform among the remaining 52. This
    reorder matches the physical chronology of Prize placement then draw.
    """
    cats = counts.cats
    if counts.iron < 1 or counts.opener + counts.prizes >= counts.n:
        raise ValueError("Invalid setup configuration")
    accepted = comb(counts.n, counts.opener) - comb(
        counts.n - counts.iron, counts.opener
    )
    denominator = (
        accepted * comb(counts.n - counts.opener, counts.prizes)
        * (counts.n - counts.opener - counts.prizes)
    )
    mass = {
        key: 0 for key in (
            "direct", "no_discard", "paid_ideal", "paid_strict",
            "paid_spare", "total",
        )
    }

    for opening in allocations(counts.opener, cats):
        if not opening[0]:
            continue
        opening_weight = prod(comb(n, k) for n, k in zip(cats, opening))
        left = [n - k for n, k in zip(cats, opening)]
        for drawn, copies in enumerate(left):
            if not copies:
                continue
            hand = [h + int(drawn == i) for i, h in enumerate(opening)]
            hand[0] -= 1
            remaining = [n - int(drawn == i) for i, n in enumerate(left)]
            other_count = sum(remaining) - sum(remaining[i] for i in (2, 3, 4))
            common_weight = opening_weight * copies
            ranges = (
                range(min(counts.prizes, remaining[2]) + 1),
                range(min(counts.prizes, remaining[3]) + 1),
                range(min(counts.prizes, remaining[4]) + 1),
            )
            for prize_gh, prize_m, prize_d in product(*ranges):
                other_prizes = counts.prizes - prize_gh - prize_m - prize_d
                if not 0 <= other_prizes <= other_count:
                    continue
                weight = (
                    common_weight
                    * comb(remaining[2], prize_gh)
                    * comb(remaining[3], prize_m)
                    * comb(remaining[4], prize_d)
                    * comb(other_count, other_prizes)
                )
                mass["total"] += weight
                if hand[3] and hand[4]:
                    mass["direct"] += weight
                    continue
                mountain_exists = hand[3] or remaining[3] > prize_m
                dce_exists = hand[4] or remaining[4] > prize_d
                gh_direct = hand[2] > 0
                gh_via_tag = hand[1] > 0 and remaining[2] > prize_gh
                if not (mountain_exists and dce_exists and (gh_direct or gh_via_tag)):
                    continue
                if hand[4]:
                    mass["no_discard"] += weight
                    continue

                mass["paid_ideal"] += weight
                if hand[5] >= 2:
                    mass["paid_strict"] += weight
                spare_gh = max(0, hand[2] - int(gh_direct))
                spare_tag = hand[1] - int(not gh_direct)
                if hand[5] + spare_gh + spare_tag >= 2:
                    mass["paid_spare"] += weight

    assert mass["total"] == denominator, (mass["total"], denominator)
    return {name: Fraction(weight, denominator) for name, weight in mass.items()}


def reach(mass: dict[str, Fraction], paid_key: str) -> Fraction:
    return mass["direct"] + mass["no_discard"] + mass[paid_key]
