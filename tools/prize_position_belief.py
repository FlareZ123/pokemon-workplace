"""Position-aware beliefs for face-down Prize cards.

PrizeBelief tracks grouped composition. This module preserves the additional
identity-to-position uncertainty required by actions that choose a physical
Prize position, such as Arc Phone or ordinary Prize taking.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from math import isclose, log2
from typing import Iterable, Mapping

PrizeGroup = str | None


def _group_sort_key(value: PrizeGroup) -> tuple[int, str]:
    return (1, "") if value is None else (0, value)


def _unique_multiset_permutations(
    values: tuple[PrizeGroup, ...],
) -> tuple[tuple[PrizeGroup, ...], ...]:
    counts = Counter(values)
    keys = tuple(sorted(counts, key=_group_sort_key))
    prefix: list[PrizeGroup] = []
    output: list[tuple[PrizeGroup, ...]] = []

    def visit() -> None:
        if len(prefix) == len(values):
            output.append(tuple(prefix))
            return

        for key in keys:
            if counts[key] == 0:
                continue
            counts[key] -= 1
            prefix.append(key)
            visit()
            prefix.pop()
            counts[key] += 1

    visit()
    return tuple(output)


@dataclass(frozen=True)
class PrizePositionBelief:
    """Probability distribution over grouped identities at physical Prize slots.

    None is the implicit filler group. Positions are observer-relative physical
    slots: a shuffle randomizes their mapping, while an unshuffled known
    placement can preserve it.
    """

    groups: tuple[str, ...]
    prize_count: int
    masses: tuple[tuple[tuple[PrizeGroup, ...], float], ...]

    def __post_init__(self) -> None:
        if self.prize_count < 0:
            raise ValueError("prize_count must be non-negative")
        if len(self.groups) != len(set(self.groups)):
            raise ValueError("groups must be unique")
        if not self.masses:
            raise ValueError("belief must have at least one support state")

        modeled = set(self.groups)
        for state, probability in self.masses:
            if len(state) != self.prize_count:
                raise ValueError("state length must match prize_count")
            if probability < 0.0:
                raise ValueError("probabilities must be non-negative")
            if any(
                value is not None and value not in modeled
                for value in state
            ):
                raise ValueError("state contains an unmodeled group")

        if not isclose(
            self.probability_mass(),
            1.0,
            rel_tol=0.0,
            abs_tol=1e-12,
        ):
            raise ValueError("belief probability mass must equal one")

    @classmethod
    def from_exact_composition(
        cls,
        group_counts: Mapping[str, int],
        prize_count: int,
    ) -> "PrizePositionBelief":
        """Exact composition with completely unknown position mapping."""

        if prize_count < 0:
            raise ValueError("prize_count must be non-negative")
        if any(count < 0 for count in group_counts.values()):
            raise ValueError("group counts must be non-negative")

        modeled_total = sum(group_counts.values())
        if modeled_total > prize_count:
            raise ValueError("group counts cannot exceed prize_count")

        values: list[PrizeGroup] = []
        for group, count in group_counts.items():
            values.extend([group] * count)
        values.extend([None] * (prize_count - modeled_total))

        permutations = _unique_multiset_permutations(tuple(values))
        probability = 1.0 / len(permutations)
        return cls(
            tuple(group_counts),
            prize_count,
            tuple((state, probability) for state in permutations),
        )

    @classmethod
    def from_known_positions(
        cls,
        positions: Iterable[PrizeGroup],
        *,
        groups: Iterable[str] | None = None,
    ) -> "PrizePositionBelief":
        """Point-mass belief for a fully known physical position mapping."""

        state = tuple(positions)
        resolved_groups = (
            tuple(dict.fromkeys(
                value for value in state if value is not None
            ))
            if groups is None
            else tuple(groups)
        )
        return cls(resolved_groups, len(state), ((state, 1.0),))

    def probability_mass(self) -> float:
        return sum(probability for _, probability in self.masses)

    def composition_distribution(self) -> dict[tuple[int, ...], float]:
        """Project the positional belief onto grouped Prize composition."""

        output: dict[tuple[int, ...], float] = defaultdict(float)
        for state, probability in self.masses:
            counts = tuple(
                sum(value == group for value in state)
                for group in self.groups
            )
            output[counts] += probability
        return dict(output)

    def composition_entropy_bits(self) -> float:
        return -sum(
            probability * log2(probability)
            for probability in self.composition_distribution().values()
            if probability > 0.0
        )

    def group_probability_at(
        self,
        position: int,
        group: PrizeGroup,
    ) -> float:
        if not 0 <= position < self.prize_count:
            raise IndexError("position out of range")
        if group is not None and group not in self.groups:
            raise ValueError("group must be modeled or None")

        return sum(
            probability
            for state, probability in self.masses
            if state[position] == group
        )

    def best_position_probability(self, group: PrizeGroup) -> float:
        """Best success probability when one physical Prize slot may be chosen."""

        if self.prize_count == 0:
            raise ValueError("no Prize positions remain")
        return max(
            self.group_probability_at(position, group)
            for position in range(self.prize_count)
        )

    def single_group_position_entropy_bits(self, group: str) -> float:
        """Entropy of one singleton group's physical Prize position."""

        if group not in self.groups:
            raise ValueError("group must be modeled")

        location_mass: dict[int, float] = defaultdict(float)
        for state, probability in self.masses:
            positions = [
                index
                for index, value in enumerate(state)
                if value == group
            ]
            if len(positions) != 1:
                raise ValueError(
                    "group must appear exactly once in every support state"
                )
            location_mass[positions[0]] += probability

        return -sum(
            probability * log2(probability)
            for probability in location_mass.values()
            if probability > 0.0
        )

    def condition_position(
        self,
        position: int,
        observed_group: PrizeGroup,
    ) -> "PrizePositionBelief":
        """Condition on learning the grouped identity at one physical slot."""

        likelihood = self.group_probability_at(position, observed_group)
        if likelihood == 0.0:
            raise ValueError("observation has zero probability under this belief")

        return PrizePositionBelief(
            self.groups,
            self.prize_count,
            tuple(
                (state, probability / likelihood)
                for state, probability in self.masses
                if state[position] == observed_group
            ),
        )

    def shuffle_positions(self) -> "PrizePositionBelief":
        """Randomize physical position mapping while preserving composition."""

        output: dict[tuple[PrizeGroup, ...], float] = defaultdict(float)
        for state, probability in self.masses:
            permutations = _unique_multiset_permutations(state)
            share = probability / len(permutations)
            for permutation in permutations:
                output[permutation] += share

        return PrizePositionBelief(
            self.groups,
            self.prize_count,
            tuple(sorted(output.items(), key=lambda row: repr(row[0]))),
        )
