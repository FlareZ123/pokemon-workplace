"""Joint Prize-card supply for a Grand Tree Gothitelle bootstrap.

A simplified prior knows certain board and hand cards to be outside Prizes.
All other physical cards are exchangeable as the six Prize cards are sampled.
Remaining Gothorita and Gothitelle form disjoint named card categories.
Every completed new Gothitelle needs one of each searched from the deck.

This is a conditional hidden-zone supply calculation, not an opening-hand
or search-policy simulator.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import comb


@dataclass(frozen=True)
class EvolutionSupply:
    unseen: int
    prizes: int
    stage1: int
    stage2: int
    action_cap: int

    def __post_init__(self) -> None:
        if min(self.unseen, self.prizes, self.stage1, self.stage2, self.action_cap) < 0:
            raise ValueError("Negative model parameter")
        if self.prizes > self.unseen:
            raise ValueError("Prize sample exceeds unseen pool")
        if self.stage1 + self.stage2 > self.unseen:
            raise ValueError("Critical disjoint card groups exceed unseen pool")

    def outcome_distribution(self) -> dict[int, Fraction]:
        """Exactly distribute completed evolution chains under direct supply."""
        denominator = comb(self.unseen, self.prizes)
        other = self.unseen - self.stage1 - self.stage2
        outcomes: dict[int, Fraction] = {}
        for p1 in range(self.stage1 + 1):
            for p2 in range(self.stage2 + 1):
                ordinary = self.prizes - p1 - p2
                if not 0 <= ordinary <= other:
                    continue
                ways = (
                    comb(self.stage1, p1)
                    * comb(self.stage2, p2)
                    * comb(other, ordinary)
                )
                completed = min(
                    self.action_cap,
                    self.stage1 - p1,
                    self.stage2 - p2,
                )
                outcomes[completed] = (
                    outcomes.get(completed, Fraction())
                    + Fraction(ways, denominator)
                )
        assert sum(outcomes.values(), Fraction()) == 1
        return dict(sorted(outcomes.items()))

    def expected_completed(self) -> Fraction:
        return sum(
            (k * weight for k, weight in self.outcome_distribution().items()),
            Fraction(),
        )

    def probability_full_supply(self) -> Fraction:
        """Probability neither remaining evolution group contributes a Prize."""
        return Fraction(
            comb(self.unseen - self.stage1 - self.stage2, self.prizes),
            comb(self.unseen, self.prizes),
        ) if self.prizes <= self.unseen - self.stage1 - self.stage2 else Fraction()

    def incorrect_independence_product(self) -> Fraction:
        """Diagnostic: product of two correct but dependent zero-Prize marginals."""
        denom = comb(self.unseen, self.prizes)
        a = (
            Fraction(comb(self.unseen - self.stage1, self.prizes), denom)
            if self.prizes <= self.unseen - self.stage1 else Fraction()
        )
        b = (
            Fraction(comb(self.unseen - self.stage2, self.prizes), denom)
            if self.prizes <= self.unseen - self.stage2 else Fraction()
        )
        return a * b
