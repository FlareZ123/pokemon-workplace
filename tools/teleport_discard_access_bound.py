"""Exact K0/K1 access bounds for an Ultra Ball -> Teleport Room payload line.

Conditional model: Gothitelle is already available, the Bench is full under
Collapsed Stadium, and the ordinary Stadium-play quota is exhausted.
A successful branch requires one Ultra Ball and Sky Field in the sampled
hand, one other approved discard card, and a singleton searched Basic still
in the deck. This bounds that specified branch, not whole-game success.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from math import comb


def choose(n: int, k: int) -> int:
    return comb(n, k) if 0 <= k <= n else 0


def at_least_one_of_each(
    population: int, draws: int, groups: tuple[int, ...]
) -> Fraction:
    """Exact multivariate hypergeometric inclusion-exclusion."""
    if population < 0 or not 0 <= draws <= population:
        raise ValueError("invalid sampling population")
    if any(group < 0 for group in groups) or sum(groups) > population:
        raise ValueError("invalid disjoint group sizes")
    numerator = 0
    for mask in range(1 << len(groups)):
        removed = sum(
            count for index, count in enumerate(groups)
            if mask & (1 << index)
        )
        numerator += (-1) ** mask.bit_count() * choose(
            population - removed, draws
        )
    return Fraction(numerator, comb(population, draws))


@dataclass(frozen=True)
class UnknownPool:
    total: int
    prizes: int
    seen: int
    ultra_ball: int
    sky_field: int
    approved_discard: int
    searched_singleton: int = 1

    def __post_init__(self) -> None:
        if self.total <= 0 or not 0 <= self.prizes < self.total:
            raise ValueError("invalid pool or Prize count")
        if not 0 <= self.seen <= self.total - self.prizes:
            raise ValueError("invalid hand sample size")
        if self.searched_singleton != 1:
            raise ValueError("this model conditions on one searched target")
        if min(self.ultra_ball, self.sky_field, self.approved_discard) < 0:
            raise ValueError("negative category count")
        if (
            self.ultra_ball + self.sky_field
            + self.approved_discard + self.searched_singleton
            > self.total
        ):
            raise ValueError("categories exceed unknown pool")


def k0_payload_probability(spec: UnknownPool, *, enforce_payment: bool = True) -> Fraction:
    """Marginalize six or other random Prizes and later random seen cards.

    The singleton target must remain in the undealt deck after Prizes and
    the observed hand. Conditional on that, the observed hand is uniformly
    sampled from the other N-1 identities, making inclusion-exclusion exact.
    """
    target_in_deck = Fraction(spec.total - spec.prizes - spec.seen, spec.total)
    groups = (spec.ultra_ball, spec.sky_field)
    if enforce_payment:
        groups += (spec.approved_discard,)
    return target_in_deck * at_least_one_of_each(
        spec.total - 1, spec.seen, groups
    )


def k1_payload_probability(
    unprized_total: int,
    seen: int,
    *,
    unprized_ultra_ball: int,
    unprized_sky_field: int,
    unprized_approved_discard: int,
    target_prized: bool = False,
) -> Fraction:
    """Condition on the actual prize composition, before drawing hand cards."""
    if target_prized:
        return Fraction(0)
    if unprized_total <= 0 or not 0 <= seen < unprized_total:
        raise ValueError("invalid nonprized deck/hand pool")
    groups = (
        unprized_ultra_ball,
        unprized_sky_field,
        unprized_approved_discard,
    )
    if min(groups) < 0 or sum(groups) + 1 > unprized_total:
        raise ValueError("invalid unprized group composition")
    return Fraction(unprized_total - seen, unprized_total) * at_least_one_of_each(
        unprized_total - 1, seen, groups
    )


def enumerate_small_k0(spec: UnknownPool) -> Fraction:
    """Independent labeled exhaustive witness for deliberately small pools."""
    labels = (
        ("T",) * spec.searched_singleton
        + ("U",) * spec.ultra_ball
        + ("S",) * spec.sky_field
        + ("D",) * spec.approved_discard
    )
    labels += ("F",) * (spec.total - len(labels))
    wins = 0
    total = 0
    all_positions = tuple(range(spec.total))
    for prize_positions in combinations(all_positions, spec.prizes):
        prize_set = set(prize_positions)
        available = tuple(i for i in all_positions if i not in prize_set)
        for hand_positions in combinations(available, spec.seen):
            total += 1
            hand = {labels[i] for i in hand_positions}
            target_in_deck = all(
                labels[i] != "T" for i in prize_positions + hand_positions
            )
            wins += int(target_in_deck and {"U", "S", "D"} <= hand)
    return Fraction(wins, total)


def example_results() -> dict:
    spec = UnknownPool(46, 6, 5, 4, 2, 16)
    expected = k0_payload_probability(spec)
    naive = k0_payload_probability(spec, enforce_payment=False)
    by_discard = {
        n: k0_payload_probability(
            UnknownPool(46, 6, 5, 4, 2, n)
        )
        for n in (0, 2, 4, 8, 12, 16, 20)
    }
    return {
        "unknown_pool": spec,
        "k0_payment_aware": expected,
        "k0_access_only": naive,
        "k0_payment_gap": naive - expected,
        "vary_discardable_pool": by_discard,
        "k1_all_live": k1_payload_probability(
            40, 5,
            unprized_ultra_ball=4,
            unprized_sky_field=2,
            unprized_approved_discard=16,
        ),
        "k1_one_sky_prized": k1_payload_probability(
            40, 5,
            unprized_ultra_ball=4,
            unprized_sky_field=1,
            unprized_approved_discard=16,
        ),
    }
