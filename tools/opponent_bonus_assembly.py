"""Exact opponent bonus-draw assembly probabilities after a valid opening.

All tracked target groups are mutually disjoint. Each may include a specified
subset of ordinary Basic starters. Prize placement is uniform; drawn cards are exchangeable
over the non-opening portion of the deck after marginalizing hidden Prizes.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from math import comb
from collections.abc import Sequence

def _choose(n: int, k: int) -> int:
    """Combinations with zero out-of-range witnesses."""
    return comb(n, k) if 0 <= k <= n else 0


from tools.setup_count_dependent_policy import (
    CountDependentPolicy,
    optimize_count_dependent_mulligan_penalty,
)
from tools.setup_hand_value_policy import HandValue


@dataclass(frozen=True)
class OpponentBonusAssembly:
    deck_size: int
    opening_size: int
    prize_count: int
    basic_starters: int
    required_groups: tuple[int, ...]
    basic_overlap_groups: tuple[int, ...] = ()

    def __post_init__(self) -> None:
        if self.deck_size <= 0 or not 0 < self.opening_size < self.deck_size:
            raise ValueError("invalid deck/opening size")
        if not 0 <= self.prize_count <= self.deck_size - self.opening_size:
            raise ValueError("invalid Prize count")
        if self.basic_starters <= 0 or not self.required_groups:
            raise ValueError("a positive starter count and target groups are required")
        if any(group <= 0 for group in self.required_groups):
            raise ValueError("target-group sizes must be positive")
        if self.basic_overlap_groups and (
            len(self.basic_overlap_groups) != len(self.required_groups)
        ):
            raise ValueError("starter-overlap counts must match target groups")
        overlaps = self.overlaps
        if any(
            overlap < 0 or overlap > size
            for size, overlap in zip(self.required_groups, overlaps)
        ):
            raise ValueError("starter overlaps must fit within each target group")
        if sum(overlaps) > self.basic_starters:
            raise ValueError("overlapping targets exceed Basic starter count")
        if (
            self.basic_starters + sum(self.required_groups) - sum(overlaps)
            > self.deck_size
        ):
            raise ValueError("target and starter union exceeds deck size")

    @property
    def overlaps(self) -> tuple[int, ...]:
        return self.basic_overlap_groups or (0,) * len(self.required_groups)

    @property
    def maximum_bonus_draws(self) -> int:
        return self.deck_size - self.opening_size - self.prize_count

    def probability_none(
        self, missing_target_cards: int, bonus_draws: int,
        *, starter_overlap: int = 0
    ) -> Fraction:
        """P(no tracked cards in opener or bonus), conditioned on a Basic opener.

        Prize positions are marginalized. If no tracked card was in the opening
        hand, the bonus sample is exchangeable among all N-H unseen cards, even
        though six randomly chosen positions are physically put into Prizes.
        """
        if not 0 <= missing_target_cards <= sum(self.required_groups):
            raise ValueError("invalid target count")
        if not 0 <= starter_overlap <= min(
            missing_target_cards, self.basic_starters
        ):
            raise ValueError("starter overlap must be within both groups")
        if not 0 <= bonus_draws <= self.maximum_bonus_draws:
            raise ValueError("bonus draws exceed the post-Prize deck")
        n, h, b, k = (
            self.deck_size,
            self.opening_size,
            self.basic_starters,
            missing_target_cards,
        )
        accepted = comb(n, h) - comb(n - b, h)
        no_target_accepted = _choose(n - k, h) - _choose(n - b - k + starter_overlap, h)
        return (
            Fraction(no_target_accepted, accepted)
            * Fraction(_choose(n - h - k, bonus_draws), comb(n - h, bonus_draws))
        )

    def assembly_probability(self, bonus_draws: int) -> Fraction:
        """Exact P(at least one card from every required group)."""
        total = Fraction(0)
        indices = range(len(self.required_groups))
        for length in range(len(self.required_groups) + 1):
            for chosen in combinations(indices, length):
                absent_cards = sum(self.required_groups[index] for index in chosen)
                shared_basics = sum(self.overlaps[index] for index in chosen)
                total += (-1) ** length * self.probability_none(
                    absent_cards, bonus_draws, starter_overlap=shared_basics
                )
        return total

    def bonus_marginal_costs(
        self, payoff: float, *, draw_cap: int | None = None
    ) -> tuple[float, ...]:
        """Per-mulligan externality for a capped bonus-draw policy.

        payoff measures the value to the opponent of assembling all groups,
        expressed in the player's own opening-utility units. The opponent is
        assumed to choose all available bonus draws until the stated cap.
        After that cap the marginal cost is zero.
        """
        if payoff < 0:
            raise ValueError("payoff must be non-negative")
        cap = self.maximum_bonus_draws if draw_cap is None else draw_cap
        if not 0 <= cap <= self.maximum_bonus_draws:
            raise ValueError("draw_cap exceeds the post-Prize deck")
        probabilities = [self.assembly_probability(count) for count in range(cap + 1)]
        return tuple(
            float(payoff * (probabilities[count + 1] - probabilities[count]))
            for count in range(cap)
        )


def optimize_setup_against_bonus(
    opponent: OpponentBonusAssembly,
    *,
    payoff: float,
    draw_cap: int,
    own_forced_starters: int,
    own_optional_groups: Sequence[int],
    own_feature_groups: Sequence[int],
    own_terminal_value: HandValue,
    own_opening_size: int = 7,
) -> CountDependentPolicy:
    """Optimize opening quality minus *incremental* opponent assembly benefit.

    Omits the constant opponent assembly probability before any bonus draws.
    Uses the existing exact count-dependent setup solver. After draw_cap
    mulligans, the opponent's modeled bonus count remains capped.
    """
    return optimize_count_dependent_mulligan_penalty(
        opponent.deck_size,
        own_forced_starters,
        own_optional_groups,
        own_feature_groups,
        own_terminal_value,
        opening_hand_size=own_opening_size,
        prefix_marginal_penalties=opponent.bonus_marginal_costs(
            payoff, draw_cap=draw_cap
        ),
        tail_marginal_penalty=0.0,
    )
