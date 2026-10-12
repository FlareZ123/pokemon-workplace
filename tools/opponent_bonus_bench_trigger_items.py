"""Exact first-window access to two singleton Basic hand-to-Bench triggers.

Both target Basics must remain unplayed during setup to trigger their E-06
Abilities later. An unrelated Basic must occupy the starting Active Spot.
Missing targets may be retrieved with paid one-output search Items. Items and
payments are abstract and assumed fully usable; target Prizes are integrated.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import comb, prod

from tools.opponent_bonus_matching import allocations


def choose(n: int, k: int) -> int:
    return comb(n, k) if 0 <= k <= n else 0


@dataclass(frozen=True)
class TwoBenchTriggerItems:
    deck_size: int = 60
    opening_size: int = 7
    prizes: int = 6
    other_basics: int = 5
    item_sources: int = 3
    safe_fodder: int = 12
    payment_per_item: int = 2

    def __post_init__(self) -> None:
        if not 0 < self.opening_size < self.deck_size:
            raise ValueError("invalid deck or opening")
        if not 0 <= self.prizes <= self.deck_size - self.opening_size:
            raise ValueError("invalid Prize count")
        if min(self.other_basics, self.item_sources, self.safe_fodder,
               self.payment_per_item) < 0 or min(self.capacities) < 0:
            raise ValueError("invalid card-class counts")

    @property
    def capacities(self) -> tuple[int, ...]:
        # Both trigger targets are singleton ordinary Basics, distinct from
        # every unrelated Basic starter and each other.
        groups = (self.other_basics, 1, 1, self.item_sources, self.safe_fodder)
        return (*groups, self.deck_size - sum(groups))

    @property
    def max_bonus_draws(self) -> int:
        return self.deck_size - self.opening_size - self.prizes

    def probability(
        self, bonus_draws: int, *, require_bench_triggers: bool = True,
        ignore_payment: bool = False, ignore_prizes: bool = False,
    ) -> Fraction:
        """P(both goals accessible | an opening with any ordinary Basic).

        Without trigger requirement, seeing either target in the setup hand
        counts as enough. With it, a non-target Basic must have been in the
        initial opening, so both singleton target copies remain in hand (or
        may be searched into hand after setup).
        """
        if not 0 <= bonus_draws <= self.max_bonus_draws:
            raise ValueError("invalid bonus count")
        n, h = self.deck_size, self.opening_size
        seen, unseen = h + bonus_draws, n - h - bonus_draws
        size = self.capacities
        accepted = Fraction(
            choose(n, h) - choose(n - self.other_basics - 2, h), choose(n, h)
        )
        success = Fraction()
        for counts in allocations(size, seen):
            other, a, b, sources, fodder, _ = counts
            missing = 2 - a - b
            if sources < missing:
                continue
            if not ignore_payment and fodder < missing * self.payment_per_item:
                continue
            starter_count = other if require_bench_triggers else other + a + b
            legal_setup_fraction = Fraction(
                choose(seen, h) - choose(seen - starter_count, h),
                choose(seen, h),
            )
            if not legal_setup_fraction:
                continue
            target_survives_prizes = (
                Fraction(1) if ignore_prizes else
                Fraction(choose(unseen - missing, self.prizes),
                         choose(unseen, self.prizes))
            )
            mass = Fraction(
                prod(choose(capacity, observed)
                     for capacity, observed in zip(size, counts)),
                choose(n, seen),
            )
            success += legal_setup_fraction * target_survives_prizes * mass
        return success / accepted

    def ablation(self, bonus_draws: int) -> dict[str, Fraction]:
        return {
            "naive": self.probability(bonus_draws, require_bench_triggers=False),
            "role_only": self.probability(bonus_draws, ignore_payment=True,
                                          ignore_prizes=True),
            "role_and_payment": self.probability(bonus_draws,
                                                 ignore_prizes=True),
            "role_and_prizes": self.probability(bonus_draws,
                                                ignore_payment=True),
            "physical": self.probability(bonus_draws),
        }
