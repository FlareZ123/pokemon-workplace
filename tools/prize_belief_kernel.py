"""Grouped probability kernel for Prize-composition knowledge.

The state tracks a probability distribution over counts of line-relevant card
groups in the current Prize set. Unmodeled cards share one implicit filler
group. It is intentionally a compact information model rather than a full game
state.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from math import comb, log2
from typing import Mapping


@dataclass(frozen=True)
class PrizeBelief:
    """Probability distribution over grouped Prize-card counts."""

    groups: tuple[str, ...]
    prize_count: int
    masses: tuple[tuple[tuple[int, ...], float], ...]

    @classmethod
    def from_exact(
        cls,
        group_counts: Mapping[str, int],
        prize_count: int,
    ) -> "PrizeBelief":
        """Create a point-mass belief for one exactly known Prize composition."""
        if prize_count < 0:
            raise ValueError("prize_count must be non-negative")
        groups = tuple(group_counts)
        counts = tuple(group_counts[group] for group in groups)
        if any(count < 0 for count in counts):
            raise ValueError("group counts must be non-negative")
        if sum(counts) > prize_count:
            raise ValueError("group counts cannot exceed prize_count")
        return cls(groups, prize_count, ((counts, 1.0),))

    @classmethod
    def from_hypergeometric(
        cls,
        group_pool_counts: Mapping[str, int],
        pool_size: int,
        prize_count: int,
    ) -> "PrizeBelief":
        """Create the exact grouped belief for a random Prize subset."""
        if pool_size <= 0:
            raise ValueError("pool_size must be positive")
        if not 0 <= prize_count <= pool_size:
            raise ValueError("prize_count must be between 0 and pool_size")

        groups = tuple(group_pool_counts)
        pool_counts = tuple(group_pool_counts[group] for group in groups)
        if any(count < 0 for count in pool_counts):
            raise ValueError("group pool counts must be non-negative")
        if sum(pool_counts) > pool_size:
            raise ValueError("group pool counts cannot exceed pool_size")

        filler = pool_size - sum(pool_counts)
        denominator = comb(pool_size, prize_count)
        masses: list[tuple[tuple[int, ...], float]] = []

        for state in product(*[range(count + 1) for count in pool_counts]):
            filler_prized = prize_count - sum(state)
            if not 0 <= filler_prized <= filler:
                continue

            ways = comb(filler, filler_prized)
            for pool_count, prized_count in zip(pool_counts, state):
                ways *= comb(pool_count, prized_count)

            if ways:
                masses.append((state, ways / denominator))

        return cls(groups, prize_count, tuple(masses))

    def probability_mass(self) -> float:
        return sum(probability for _, probability in self.masses)

    def is_exact(self) -> bool:
        return (
            len(self.masses) == 1
            and abs(self.masses[0][1] - 1.0) <= 1e-12
        )

    def entropy_bits(self) -> float:
        return -sum(
            probability * log2(probability)
            for _, probability in self.masses
            if probability > 0.0
        )

    def state_dicts(self) -> list[tuple[dict[str, int], float]]:
        return [
            (dict(zip(self.groups, state)), probability)
            for state, probability in self.masses
        ]

    def replace_unknown_position_with_known(
        self,
        incoming_group: str | None,
    ) -> "PrizeBelief":
        """Replace one identity-unknown Prize position with a known incoming card.

        The chosen physical Prize position is assumed not to reveal its identity.
        Conditional on a composition state, each Prize card is equally likely to
        occupy that position. incoming_group=None means the incoming card is
        outside the modeled groups and belongs to filler.
        """
        if self.prize_count <= 0:
            raise ValueError("cannot replace a Prize card when prize_count is zero")

        group_index = {group: index for index, group in enumerate(self.groups)}
        if incoming_group is not None and incoming_group not in group_index:
            raise ValueError("incoming_group must be modeled or None")
        incoming_index = (
            group_index[incoming_group]
            if incoming_group is not None
            else None
        )

        output: dict[tuple[int, ...], float] = {}

        for state, mass in self.masses:
            filler_count = self.prize_count - sum(state)
            outgoing_choices = [(None, filler_count)]
            outgoing_choices.extend(
                (index, count)
                for index, count in enumerate(state)
            )

            for outgoing_index, count in outgoing_choices:
                if count == 0:
                    continue

                next_state = list(state)
                if outgoing_index is not None:
                    next_state[outgoing_index] -= 1
                if incoming_index is not None:
                    next_state[incoming_index] += 1

                key = tuple(next_state)
                output[key] = (
                    output.get(key, 0.0)
                    + mass * count / self.prize_count
                )

        return PrizeBelief(
            self.groups,
            self.prize_count,
            tuple(sorted(output.items())),
        )

    def observe_random_position(
        self,
        observed_group: str | None,
    ) -> "PrizeBelief":
        """Condition on revealing the identity group at one random Prize position.

        observed_group=None means the revealed card belongs to filler.
        This observes the card without removing it from the Prize set.
        """
        if self.prize_count <= 0:
            raise ValueError("cannot observe a Prize card when prize_count is zero")

        group_index = {group: index for index, group in enumerate(self.groups)}
        if observed_group is not None and observed_group not in group_index:
            raise ValueError("observed_group must be modeled or None")
        observed_index = (
            group_index[observed_group]
            if observed_group is not None
            else None
        )

        weighted: list[tuple[tuple[int, ...], float]] = []
        total = 0.0

        for state, mass in self.masses:
            if observed_index is None:
                count = self.prize_count - sum(state)
            else:
                count = state[observed_index]

            weight = mass * count / self.prize_count
            if weight:
                weighted.append((state, weight))
                total += weight

        if total == 0.0:
            raise ValueError("observation has zero probability under this belief")

        return PrizeBelief(
            self.groups,
            self.prize_count,
            tuple((state, weight / total) for state, weight in weighted),
        )
