"""Position-indexed Prize and deck-top information kernel for paper Expanded.

One observer's belief over named Prize positions and the single next deck
card. A known top card swapped into a face-down Prize acquires a known physical
position without becoming face up. None represents the unmodeled filler class.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from itertools import permutations
from math import factorial, isclose
from typing import Mapping

CardGroup = str | None
World = tuple[tuple[CardGroup, ...], CardGroup]


@dataclass(frozen=True)
class PrizePositionTopBelief:
    groups: tuple[str, ...]
    face_up: tuple[bool, ...]
    masses: tuple[tuple[World, float], ...]

    def __post_init__(self) -> None:
        if len(set(self.groups)) != len(self.groups) or any(not g for g in self.groups):
            raise ValueError("group names must be unique and nonempty")
        if not self.masses:
            raise ValueError("no possible worlds")
        if any(len(world[0]) != len(self.face_up) for world, _ in self.masses):
            raise ValueError("Prize position count mismatch")
        if any(not 0 < mass <= 1 for _, mass in self.masses):
            raise ValueError("invalid world probability")
        if any(g is not None and g not in self.groups
               for (prizes, top), _ in self.masses for g in (*prizes, top)):
            raise ValueError("unknown group in world")
        if len({world for world, _ in self.masses}) != len(self.masses):
            raise ValueError("duplicate world")
        if not isclose(sum(mass for _, mass in self.masses), 1, abs_tol=1e-10):
            raise ValueError("world probabilities must sum to one")
        for index, up in enumerate(self.face_up):
            if up and len({world[0][index] for world, _ in self.masses}) != 1:
                raise ValueError("public face-up Prize must have fixed identity")

    @classmethod
    def from_pool(
        cls,
        group_counts: Mapping[str, int],
        *,
        pool_size: int,
        prize_count: int,
    ) -> PrizePositionTopBelief:
        """Sample ordered Prize positions and one top card without replacement."""
        if pool_size <= 0 or not 0 <= prize_count < pool_size:
            raise ValueError("pool must contain Prizes and one top card")
        groups = tuple(group_counts)
        counts = tuple(group_counts.values())
        if any(not isinstance(c, int) or c < 0 for c in counts):
            raise ValueError("group counts must be nonnegative integers")
        filler = pool_size - sum(counts)
        if filler < 0:
            raise ValueError("group counts exceed pool size")
        labels: tuple[CardGroup, ...] = (*groups, None)
        worlds: list[tuple[World, float]] = []

        def visit(seq: tuple[CardGroup, ...], stock: tuple[int, ...], mass: float) -> None:
            if len(seq) == prize_count + 1:
                worlds.append(((seq[:-1], seq[-1]), mass))
                return
            total = pool_size - len(seq)
            for index, copies in enumerate(stock):
                if copies:
                    updated = list(stock)
                    updated[index] -= 1
                    visit(seq + (labels[index],), tuple(updated), mass * copies / total)

        visit((), (*counts, filler), 1.0)
        return cls(groups, (False,) * prize_count, tuple(worlds))

    @property
    def prize_count(self) -> int:
        return len(self.face_up)

    def probability_at(self, index: int, group: CardGroup) -> float:
        self._check_position(index)
        self._check_group(group)
        return sum(m for (prizes, _), m in self.masses if prizes[index] == group)

    def probability_top(self, group: CardGroup) -> float:
        self._check_group(group)
        return sum(m for (_, top), m in self.masses if top == group)

    def probability_group_prized(self, group: str) -> float:
        self._check_group(group)
        return sum(m for (prizes, _), m in self.masses if group in prizes)

    def probability_face_down_group(self, group: str) -> float:
        self._check_group(group)
        return sum(
            m for (prizes, _), m in self.masses
            if any(card == group and not self.face_up[i] for i, card in enumerate(prizes))
        )

    def composition_masses(self) -> tuple[tuple[tuple[int, ...], float], ...]:
        """Forget position and deck-top correlations."""
        result: dict[tuple[int, ...], float] = defaultdict(float)
        for (prizes, _), mass in self.masses:
            result[tuple(prizes.count(g) for g in self.groups)] += mass
        return tuple(sorted(result.items()))

    def collapse_to_prize_belief(self):
        """Information-losing bridge to the count-only PrizeBelief."""
        from prize_belief_kernel import PrizeBelief
        return PrizeBelief(self.groups, self.prize_count, self.composition_masses())

    def collapse_to_visibility_belief(self):
        """Information-losing bridge to the face-up/face-down partition."""
        from prize_belief_kernel import PrizeBelief
        from prize_visibility_partition import PrizeVisibilityBelief

        visible = [i for i, up in enumerate(self.face_up) if up]
        hidden = [i for i, up in enumerate(self.face_up) if not up]
        first = self.masses[0][0][0]
        visible_counts = tuple(sum(first[i] == g for i in visible) for g in self.groups)
        visible_filler = sum(first[i] is None for i in visible)
        result: dict[tuple[int, ...], float] = defaultdict(float)
        for (prizes, _), mass in self.masses:
            result[tuple(sum(prizes[i] == g for i in hidden) for g in self.groups)] += mass
        return PrizeVisibilityBelief(
            self.groups,
            visible_counts,
            visible_filler,
            PrizeBelief(self.groups, len(hidden), tuple(sorted(result.items()))),
        )

    def observe_top(self, group: CardGroup) -> PrizePositionTopBelief:
        """Private observation of the deck top, without changing its location."""
        self._check_group(group)
        return self._condition(lambda w: w[1] == group)

    def reveal_prize(self, index: int, group: CardGroup) -> PrizePositionTopBelief:
        """Condition on a public Prize reveal, marking its location as face up."""
        self._check_position(index)
        self._check_group(group)
        if self.face_up[index]:
            raise ValueError("position already face up")
        observed = self._condition(lambda w: w[0][index] == group)
        flags = list(self.face_up)
        flags[index] = True
        return PrizePositionTopBelief(self.groups, tuple(flags), observed.masses)

    def swap_face_down_with_top(self, index: int) -> PrizePositionTopBelief:
        """Exchange the top card and a face-down Prize without an outgoing peek.

        For Arc Phone, first condition the acting observer with observe_top.
        Other observers who did not see the peek apply only this permutation.
        """
        self._check_position(index)
        if self.face_up[index]:
            raise ValueError("face-up Prize is not eligible")
        result: dict[World, float] = defaultdict(float)
        for (prizes, top), mass in self.masses:
            updated = list(prizes)
            outgoing = updated[index]
            updated[index] = top
            result[(tuple(updated), outgoing)] += mass
        return PrizePositionTopBelief(self.groups, self.face_up, tuple(result.items()))

    def shuffle_face_down_positions(self) -> PrizePositionTopBelief:
        """Uniformly shuffle remaining face-down positions, leaving top unchanged."""
        indices = tuple(i for i, up in enumerate(self.face_up) if not up)
        if len(indices) < 2:
            return self
        result: dict[World, float] = defaultdict(float)
        denominator = factorial(len(indices))
        for (prizes, top), mass in self.masses:
            for permutation in permutations(indices):
                updated = list(prizes)
                for dest, source in zip(indices, permutation):
                    updated[dest] = prizes[source]
                result[(tuple(updated), top)] += mass / denominator
        return PrizePositionTopBelief(self.groups, self.face_up, tuple(result.items()))

    def _condition(self, predicate) -> PrizePositionTopBelief:
        filtered = [(w, p) for w, p in self.masses if predicate(w)]
        total = sum(p for _, p in filtered)
        if total <= 0:
            raise ValueError("observation has zero probability")
        return PrizePositionTopBelief(
            self.groups, self.face_up, tuple((w, p / total) for w, p in filtered)
        )

    def _check_position(self, index: int) -> None:
        if not 0 <= index < self.prize_count:
            raise IndexError("Prize position out of range")

    def _check_group(self, group: CardGroup) -> None:
        if group is not None and group not in self.groups:
            raise ValueError("group must be modeled or None for filler")
