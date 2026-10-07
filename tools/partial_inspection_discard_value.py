"""Exact discard-policy value of a partial inspection of known deck cards.

The model has m singleton replacement candidates in an unknown own-card pool.
First P cards are hidden as Prize cards. Then q cards are observed from the
remaining deck without revealing the rest. The policy sees which candidate
replacements appeared in the observation and must choose d classes to discard.

This captures the information geometry of effects such as a top-card or top-five
inspection without pretending that partial inspection establishes K1.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations, product
from math import comb


@dataclass(frozen=True)
class PartialInspectionModel:
    unknown_pool: int
    prize_count: int
    candidate_classes: int
    required_discards: int
    observed_deck_cards: int

    def __post_init__(self) -> None:
        if self.unknown_pool <= 0:
            raise ValueError("unknown_pool must be positive")
        if self.prize_count < 0 or self.prize_count > self.unknown_pool:
            raise ValueError("invalid prize_count")
        if self.candidate_classes <= 0:
            raise ValueError("candidate_classes must be positive")
        if self.candidate_classes > self.unknown_pool:
            raise ValueError("candidate classes exceed unknown pool")
        if (
            self.required_discards <= 0
            or self.required_discards > self.candidate_classes
        ):
            raise ValueError("invalid required_discards")
        deck_size = self.unknown_pool - self.prize_count
        if (
            self.observed_deck_cards < 0
            or self.observed_deck_cards > deck_size
        ):
            raise ValueError("invalid observed_deck_cards")

    @property
    def denominator(self) -> int:
        return comb(self.unknown_pool, self.prize_count) * comb(
            self.unknown_pool - self.prize_count,
            self.observed_deck_cards,
        )

    @property
    def no_inspection_success(self) -> Fraction:
        """Any fixed d singleton candidates must all avoid the Prizes."""

        return Fraction(
            comb(self.unknown_pool - self.required_discards, self.prize_count),
            comb(self.unknown_pool, self.prize_count),
        )

    def _observation_groups(
        self,
    ) -> dict[
        tuple[int, ...],
        tuple[tuple[tuple[bool, ...], int], ...],
    ]:
        """Group hidden worlds by which candidate replacements were observed."""

        filler = self.unknown_pool - self.candidate_classes
        groups: dict[
            tuple[int, ...],
            list[tuple[tuple[bool, ...], int]],
        ] = defaultdict(list)
        total = 0

        # Candidate state: 0=Prize, 1=observed deck card, 2=unobserved deck card.
        for states in product(range(3), repeat=self.candidate_classes):
            candidate_prizes = states.count(0)
            candidate_observed = states.count(1)
            filler_prizes = self.prize_count - candidate_prizes
            filler_observed = self.observed_deck_cards - candidate_observed
            if filler_prizes < 0 or filler_prizes > filler:
                continue
            if (
                filler_observed < 0
                or filler_observed > filler - filler_prizes
            ):
                continue

            weight = comb(filler, filler_prizes) * comb(
                filler - filler_prizes,
                filler_observed,
            )
            if weight == 0:
                continue

            observation = tuple(
                index for index, state in enumerate(states) if state == 1
            )
            live = tuple(state != 0 for state in states)
            groups[observation].append((live, weight))
            total += weight

        if total != self.denominator:
            raise AssertionError("partial-inspection state weights do not conserve")

        return {
            observation: tuple(worlds)
            for observation, worlds in groups.items()
        }

    @property
    def partial_policy_success(self) -> Fraction:
        """Best policy that may condition only on the partial observation."""

        favorable = 0
        for _observation, worlds in self._observation_groups().items():
            best = 0
            for subset in combinations(
                range(self.candidate_classes),
                self.required_discards,
            ):
                success_weight = sum(
                    weight
                    for live, weight in worlds
                    if all(live[index] for index in subset)
                )
                best = max(best, success_weight)
            favorable += best
        return Fraction(favorable, self.denominator)

    @property
    def full_k1_success(self) -> Fraction:
        """Full-information ceiling after exact Prize composition is known."""

        favorable = 0
        for worlds in self._observation_groups().values():
            favorable += sum(
                weight
                for live, weight in worlds
                if sum(live) >= self.required_discards
            )
        return Fraction(favorable, self.denominator)

    @property
    def recovered_information_value(self) -> Fraction:
        return self.partial_policy_success - self.no_inspection_success

    @property
    def residual_information_value(self) -> Fraction:
        return self.full_k1_success - self.partial_policy_success


def main() -> None:
    for candidates, required in ((2, 1), (3, 1), (3, 2)):
        print(f"m={candidates} d={required}")
        for observed in (0, 1, 5, 10, 20, 40, 46):
            model = PartialInspectionModel(
                unknown_pool=52,
                prize_count=6,
                candidate_classes=candidates,
                required_discards=required,
                observed_deck_cards=observed,
            )
            print(
                f"  q={observed:2d} "
                f"policy={float(model.partial_policy_success):.9%} "
                f"K1={float(model.full_k1_success):.9%} "
                f"residual_pp={float(model.residual_information_value) * 100:.9f}"
            )


if __name__ == "__main__":
    main()
