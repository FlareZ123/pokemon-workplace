"""Exact value of Prize information for discard-and-reacquire choices.

Each endpoint-critical discard candidate has some number of replacement copies in
an unknown deck-plus-Prize pool. A discarded class is recoverable when at least
one of its replacement copies remains outside the Prize cards.

A K0 policy chooses which critical classes to discard before seeing Prize
composition. A K1 policy chooses after exact Prize composition is known.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations, product
from math import comb


@dataclass(frozen=True)
class ReplacementInformationModel:
    unknown_pool: int
    prize_count: int
    replacement_copies: tuple[int, ...]
    required_discards: int

    def __post_init__(self) -> None:
        if self.unknown_pool <= 0:
            raise ValueError("unknown_pool must be positive")
        if self.prize_count < 0 or self.prize_count > self.unknown_pool:
            raise ValueError("prize_count must be within unknown_pool")
        if not self.replacement_copies:
            raise ValueError("replacement_copies cannot be empty")
        if any(copies <= 0 for copies in self.replacement_copies):
            raise ValueError("each candidate needs at least one replacement copy")
        if sum(self.replacement_copies) > self.unknown_pool:
            raise ValueError("replacement copies exceed unknown_pool")
        if (
            self.required_discards <= 0
            or self.required_discards > len(self.replacement_copies)
        ):
            raise ValueError(
                "required_discards must be between 1 and candidate count"
            )

    @property
    def denominator(self) -> int:
        return comb(self.unknown_pool, self.prize_count)

    def hidden_worlds(
        self,
    ) -> tuple[tuple[tuple[int, ...], tuple[bool, ...], int], ...]:
        """Enumerate grouped Prize allocations with labeled-combination weights."""

        filler = self.unknown_pool - sum(self.replacement_copies)
        worlds = []
        for prized in product(
            *(range(copies + 1) for copies in self.replacement_copies)
        ):
            filler_prizes = self.prize_count - sum(prized)
            if filler_prizes < 0 or filler_prizes > filler:
                continue

            weight = comb(filler, filler_prizes)
            for copies, taken in zip(self.replacement_copies, prized):
                weight *= comb(copies, taken)

            live = tuple(
                taken < copies
                for copies, taken in zip(self.replacement_copies, prized)
            )
            worlds.append((tuple(prized), live, weight))

        if sum(weight for _prized, _live, weight in worlds) != self.denominator:
            raise AssertionError("grouped Prize weights do not conserve sample space")
        return tuple(worlds)

    @property
    def informed_success(self) -> Fraction:
        """K1 success: at least d candidate classes retain a live replacement."""

        favorable = sum(
            weight
            for _prized, live, weight in self.hidden_worlds()
            if sum(live) >= self.required_discards
        )
        return Fraction(favorable, self.denominator)

    def fixed_subset_success(self, subset: tuple[int, ...]) -> Fraction:
        """K0 success for one fixed subset of critical classes."""

        if len(subset) != self.required_discards:
            raise ValueError("subset size must equal required_discards")
        if len(set(subset)) != len(subset):
            raise ValueError("subset entries must be unique")
        if any(index < 0 or index >= len(self.replacement_copies) for index in subset):
            raise ValueError("subset index out of range")

        favorable = sum(
            weight
            for _prized, live, weight in self.hidden_worlds()
            if all(live[index] for index in subset)
        )
        return Fraction(favorable, self.denominator)

    @property
    def blind_optimal(self) -> tuple[tuple[int, ...], Fraction]:
        """Best K0 fixed subset and its exact success probability."""

        best_subset: tuple[int, ...] | None = None
        best_value = Fraction(-1, 1)
        for subset in combinations(
            range(len(self.replacement_copies)),
            self.required_discards,
        ):
            value = self.fixed_subset_success(subset)
            if value > best_value:
                best_subset = subset
                best_value = value

        if best_subset is None:
            raise AssertionError("no discard subset enumerated")
        return best_subset, best_value

    @property
    def information_value(self) -> Fraction:
        return self.informed_success - self.blind_optimal[1]


def main() -> None:
    cases = (
        ((1, 1), 1),
        ((2, 2), 1),
        ((3, 3), 1),
        ((1, 1, 1), 2),
        ((2, 2, 2), 2),
        ((1, 2), 1),
        ((1, 2, 3), 2),
    )
    for replacements, required in cases:
        model = ReplacementInformationModel(
            unknown_pool=52,
            prize_count=6,
            replacement_copies=replacements,
            required_discards=required,
        )
        subset, blind = model.blind_optimal
        print(
            f"replacements={replacements} d={required} "
            f"best={subset} "
            f"K0={float(blind):.9%} "
            f"K1={float(model.informed_success):.9%} "
            f"gap_pp={float(model.information_value) * 100:.9f}"
        )


if __name__ == "__main__":
    main()
