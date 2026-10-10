"""Top-two deck-order refinement of a conserved Prize/top/card-pool belief.

The first unseen deck-suffix card is represented as an explicit 'second'
position while remaining counted in the pool world's deck remainder. This
supports private knowledge of the next card without double-counting its copy.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from math import isclose
from typing import Mapping

from prize_position_top_swap import CardGroup
from prize_top_draw_pool import PrizePoolBelief, PrizePoolWorld


@dataclass(frozen=True)
class TopTwoWorld:
    pool: PrizePoolWorld
    second: CardGroup


@dataclass(frozen=True)
class PrizeTopTwoBelief:
    groups: tuple[str, ...]
    totals: tuple[int, ...]
    face_up: tuple[bool, ...]
    masses: tuple[tuple[TopTwoWorld, float], ...]

    def __post_init__(self) -> None:
        if not self.masses or not isclose(
            sum(mass for _, mass in self.masses), 1, abs_tol=1e-10
        ):
            raise ValueError("two-card belief masses must sum to one")
        labels = (*self.groups, None)
        if len({world for world, _ in self.masses}) != len(self.masses):
            raise ValueError("duplicate two-card physical worlds")
        collapsed: dict[PrizePoolWorld, float] = defaultdict(float)
        for world, mass in self.masses:
            if not 0 < mass <= 1 or world.second not in labels:
                raise ValueError("invalid second-card group or probability")
            index = labels.index(world.second)
            if world.pool.remainder[index] <= 0:
                raise ValueError("known second is absent from remaining deck")
            collapsed[world.pool] += mass
        PrizePoolBelief(
            self.groups, self.totals, self.face_up,
            tuple(collapsed.items())
        )

    @classmethod
    def from_exchangeable_pool(
        cls, pool: PrizePoolBelief
    ) -> PrizeTopTwoBelief:
        labels: tuple[CardGroup, ...] = (*pool.groups, None)
        output: dict[TopTwoWorld, float] = defaultdict(float)
        for world, mass in pool.masses:
            available = sum(world.remainder)
            if available <= 0:
                raise ValueError("deck has no second card")
            for index, count in enumerate(world.remainder):
                if count > 0:
                    output[TopTwoWorld(world, labels[index])] += (
                        mass * count / available
                    )
        return cls(
            pool.groups, pool.totals, pool.face_up,
            tuple(output.items())
        )

    def to_exchangeable_pool(self) -> PrizePoolBelief:
        """Deliberately forget the order of the second card."""
        output: dict[PrizePoolWorld, float] = defaultdict(float)
        for world, mass in self.masses:
            output[world.pool] += mass
        return PrizePoolBelief(
            self.groups, self.totals, self.face_up,
            tuple(output.items())
        )

    def _result(self, output: Mapping[TopTwoWorld, float]) -> PrizeTopTwoBelief:
        return PrizeTopTwoBelief(
            self.groups, self.totals, self.face_up,
            tuple(sorted(output.items(), key=lambda item: repr(item[0])))
        )

    def probability_second(self, group: CardGroup) -> float:
        if group is not None and group not in self.groups:
            raise ValueError("unmodeled second group")
        return sum(mass for world, mass in self.masses if world.second == group)

    def probability_top(self, group: CardGroup) -> float:
        return self.to_exchangeable_pool().probability_top(group)

    def observe_second(self, group: CardGroup) -> PrizeTopTwoBelief:
        """Condition on a source-authorized private look at the second card."""
        weight = self.probability_second(group)
        if weight <= 0:
            raise ValueError("observed second-card group has zero probability")
        return self._result({
            world: mass / weight
            for world, mass in self.masses if world.second == group
        })

    def swap_top_with_face_down(self, position: int) -> PrizeTopTwoBelief:
        if not 0 <= position < len(self.face_up):
            raise IndexError("Prize position out of range")
        if self.face_up[position]:
            raise ValueError("cannot swap a face-up Prize")
        output: dict[TopTwoWorld, float] = defaultdict(float)
        for world, mass in self.masses:
            base = world.pool
            prizes = list(base.prizes)
            outgoing = prizes[position]
            prizes[position] = base.top
            updated = PrizePoolWorld(
                tuple(prizes), outgoing, base.remainder, base.drawn
            )
            output[TopTwoWorld(updated, world.second)] += mass
        return self._result(output)

    def draw_top_and_shift_window(self) -> PrizeTopTwoBelief:
        """Draw old top, shift known second to top, expose a new second card."""
        labels: tuple[CardGroup, ...] = (*self.groups, None)
        output: dict[TopTwoWorld, float] = defaultdict(float)
        for world, mass in self.masses:
            base = world.pool
            remaining = list(base.remainder)
            remaining[labels.index(world.second)] -= 1
            stock = sum(remaining)
            if stock <= 0:
                raise ValueError("no third card remains to form a two-card window")
            drawn = list(base.drawn)
            drawn[labels.index(base.top)] += 1
            next_pool = PrizePoolWorld(
                base.prizes, world.second, tuple(remaining), tuple(drawn)
            )
            for index, count in enumerate(remaining):
                if count:
                    output[TopTwoWorld(next_pool, labels[index])] += (
                        mass * count / stock
                    )
        return self._result(output)
