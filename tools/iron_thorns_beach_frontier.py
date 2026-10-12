"""Exact Iron Thorns first-turn attack versus Tropical Beach fallback frontier.

This tracks Prize-conditional opening hand and searchable deck zones, with
hypothetical discardable cards as an externally declared sensitivity class.
It is not an estimation of match win rates or future draw continuation.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from math import comb, prod

from tools.iron_thorns_gnh_discard_gate import (
    Counts, allocations, exact as attack_exact, reach,
)


@dataclass(frozen=True)
class BeachCounts:
    n: int = 60
    iron: int = 4
    tag: int = 2
    gh: int = 2
    mountain: int = 1
    dce: int = 2
    safe: int = 12
    beach: int = 1
    opener: int = 7
    prizes: int = 6

    @property
    def cats(self) -> tuple[int, ...]:
        protected = self.n - sum(
            (self.iron, self.tag, self.gh, self.mountain,
             self.dce, self.safe, self.beach)
        )
        if protected < 0:
            raise ValueError("Deck categories exceed 60")
        return (
            self.iron, self.tag, self.gh, self.mountain,
            self.dce, self.safe, self.beach, protected,
        )


def exact(counts: BeachCounts) -> dict[str, Fraction]:
    """Probabilities conditional on a starter-containing opening.

    An attack takes precedence over the fallback. When the attack is absent,
    Tropical Beach is reachable if held in hand or accessible through a
    held G&H or Tag Call searching a G&H still in the deck. The Beach action
    ends the turn, and on this initial hand context draws at least one card.

    The first draw is marginalized before Prize allocation, which is exactly
    distributionally equivalent to placing six Prizes before drawing.
    """
    cats = counts.cats
    accepted = comb(counts.n, counts.opener) - comb(
        counts.n - counts.iron, counts.opener
    )
    denominator = (
        accepted * comb(counts.n - counts.opener, counts.prizes)
        * (counts.n - counts.opener - counts.prizes)
    )
    fields = (
        "ideal_attack", "strict_attack", "spare_attack",
        "strict_failed_held_beach", "strict_failed_search_beach",
        "spare_failed_held_beach", "spare_failed_search_beach", "total",
    )
    totals = {field: 0 for field in fields}

    for opening in allocations(counts.opener, cats):
        if opening[0] == 0:
            continue
        open_weight = prod(comb(n, k) for n, k in zip(cats, opening))
        left = [n - k for n, k in zip(cats, opening)]
        for draw, copies in enumerate(left):
            if not copies:
                continue
            hand = [opening[i] + int(draw == i) for i in range(len(cats))]
            hand[0] -= 1
            remaining = [left[i] - int(draw == i) for i in range(len(cats))]
            prize_indexes = (2, 3, 4, 6)
            other_count = sum(remaining) - sum(remaining[i] for i in prize_indexes)
            ranges = (
                range(min(remaining[i], counts.prizes) + 1)
                for i in prize_indexes
            )
            for prize_counts in product(*ranges):
                other_prizes = counts.prizes - sum(prize_counts)
                if other_prizes < 0 or other_prizes > other_count:
                    continue
                weight = (
                    open_weight * copies * comb(other_count, other_prizes)
                    * prod(
                        comb(remaining[i], k)
                        for i, k in zip(prize_indexes, prize_counts)
                    )
                )
                totals["total"] += weight
                prized_gh, prized_m, prized_dce, prized_beach = prize_counts

                can_gh = hand[2] > 0 or (
                    hand[1] > 0 and remaining[2] > prized_gh
                )
                mountain_exists = hand[3] > 0 or remaining[3] > prized_m
                dce_exists = hand[4] > 0 or remaining[4] > prized_dce
                direct_or_free = (
                    (hand[3] > 0 and hand[4] > 0)
                    or (hand[4] > 0 and can_gh and mountain_exists)
                )
                paid = (
                    not hand[4] and can_gh and mountain_exists and dce_exists
                )
                spare_gh = hand[2] - int(hand[2] > 0)
                spare_tag = hand[1] - int(hand[2] == 0)
                decisions = {
                    "ideal": direct_or_free or paid,
                    "strict": direct_or_free or (paid and hand[5] >= 2),
                    "spare": direct_or_free or (
                        paid and hand[5] + spare_gh + spare_tag >= 2
                    ),
                }
                for policy, available in decisions.items():
                    if available:
                        totals[policy + "_attack"] += weight
                    elif policy in ("strict", "spare"):
                        if hand[6]:
                            totals[policy + "_failed_held_beach"] += weight
                        elif can_gh and remaining[6] > prized_beach:
                            totals[policy + "_failed_search_beach"] += weight

    assert totals["total"] == denominator
    result = {name: Fraction(value, denominator) for name, value in totals.items()}
    other = attack_exact(
        Counts(
            n=counts.n, iron=counts.iron, tag=counts.tag, gh=counts.gh,
            mountain=counts.mountain, dce=counts.dce, safe=counts.safe,
            opener=counts.opener, prizes=counts.prizes,
        )
    )
    for policy, key in (
        ("ideal", "paid_ideal"), ("strict", "paid_strict"),
        ("spare", "paid_spare"),
    ):
        assert result[policy + "_attack"] == reach(other, key)
    return result


def beach_fallback(result: dict[str, Fraction], policy: str) -> Fraction:
    return (
        result[policy + "_failed_held_beach"]
        + result[policy + "_failed_search_beach"]
    )
