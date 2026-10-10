"""Correlated Prize/top draw transition with an exchangeable residual deck pool.

Each world conserves a closed finite group multiset over Prize positions,
the current deck top, remaining unseen deck suffix, and cards drawn from the
tracked pool. Card-group distributions are exact up to float arithmetic.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from math import isclose
from typing import Mapping

from prize_position_top_swap import CardGroup, PrizePositionTopBelief


@dataclass(frozen=True)
class PrizePoolWorld:
    prizes: tuple[CardGroup, ...]
    top: CardGroup
    remainder: tuple[int, ...]
    drawn: tuple[int, ...]


@dataclass(frozen=True)
class PrizePoolBelief:
    groups: tuple[str, ...]
    totals: tuple[int, ...]  # modeled groups followed by one filler group
    face_up: tuple[bool, ...]
    masses: tuple[tuple[PrizePoolWorld, float], ...]

    def __post_init__(self) -> None:
        if len(self.groups) != len(set(self.groups)):
            raise ValueError("group names must be distinct")
        if len(self.totals) != len(self.groups) + 1:
            raise ValueError("need a copy count for every group including filler")
        if any(not isinstance(c, int) or c < 0 for c in self.totals):
            raise ValueError("total copy counts must be nonnegative integers")
        if not self.masses or not isclose(
            sum(mass for _, mass in self.masses), 1, abs_tol=1e-10
        ):
            raise ValueError("belief mass must sum to one")
        if len({world for world, _ in self.masses}) != len(self.masses):
            raise ValueError("duplicate grouped pool worlds")
        for world, mass in self.masses:
            if not 0 < mass <= 1 or len(world.prizes) != len(self.face_up):
                raise ValueError("invalid Prize world or probability")
            if len(world.remainder) != len(self.totals) or len(world.drawn) != len(self.totals):
                raise ValueError("inventory vector dimension mismatch")
            if any(not isinstance(c, int) or c < 0 for c in (*world.remainder, *world.drawn)):
                raise ValueError("negative or fractional card counts")
            present = [0] * len(self.totals)
            for card in (*world.prizes, world.top):
                present[self._index(card)] += 1
            for i, initial in enumerate(self.totals):
                if present[i] + world.remainder[i] + world.drawn[i] != initial:
                    raise ValueError("physical group cards were created or lost")
        for pos, face_up in enumerate(self.face_up):
            if face_up and len({world.prizes[pos] for world, _ in self.masses}) != 1:
                raise ValueError("face-up Prize identity must be public")

    @classmethod
    def from_joint_prior(
        cls,
        prior: PrizePositionTopBelief,
        group_pool_counts: Mapping[str, int],
        *,
        pool_size: int,
    ) -> PrizePoolBelief:
        """Lift an exchangeable-suffix prior into a conserved full group pool."""
        if tuple(group_pool_counts) != prior.groups:
            raise ValueError("pool group order must match prior")
        if any(not isinstance(c, int) or c < 0 for c in group_pool_counts.values()):
            raise ValueError("invalid group copy count")
        filler = pool_size - sum(group_pool_counts.values())
        if filler < 0:
            raise ValueError("group count exceeds pool size")
        totals = (*group_pool_counts.values(), filler)
        labels: tuple[CardGroup, ...] = (*prior.groups, None)
        index = {group: i for i, group in enumerate(labels)}
        worlds = []
        for (prizes, top), mass in prior.masses:
            remainder = list(totals)
            for card in (*prizes, top):
                remainder[index[card]] -= 1
            if any(c < 0 for c in remainder):
                raise ValueError("prior includes world incompatible with pool")
            worlds.append(
                (PrizePoolWorld(
                    prizes, top, tuple(remainder), (0,) * len(totals)
                ), mass)
            )
        return cls(prior.groups, totals, prior.face_up, tuple(worlds))

    @property
    def prize_count(self) -> int:
        return len(self.face_up)

    def _index(self, group: CardGroup) -> int:
        if group is None:
            return len(self.groups)
        if group not in self.groups:
            raise ValueError("group not modeled")
        return self.groups.index(group)

    def _result(self, output: Mapping[PrizePoolWorld, float]) -> PrizePoolBelief:
        return PrizePoolBelief(
            self.groups,
            self.totals,
            self.face_up,
            tuple(sorted(output.items(), key=lambda item: repr(item[0]))),
        )

    def probability_top(self, group: CardGroup) -> float:
        self._index(group)
        return sum(mass for world, mass in self.masses if world.top == group)

    def probability_prize_at(self, pos: int, group: CardGroup) -> float:
        if not 0 <= pos < self.prize_count:
            raise IndexError("Prize position out of range")
        self._index(group)
        return sum(
            mass for world, mass in self.masses if world.prizes[pos] == group
        )

    def probability_both(
        self, *, top: CardGroup, prize_position: int, prize_group: CardGroup
    ) -> float:
        if not 0 <= prize_position < self.prize_count:
            raise IndexError("Prize position out of range")
        self._index(top)
        self._index(prize_group)
        return sum(
            mass for world, mass in self.masses
            if world.top == top and world.prizes[prize_position] == prize_group
        )

    def observe_top(self, group: CardGroup) -> PrizePoolBelief:
        """Condition on viewing the current top without taking it."""
        self._index(group)
        event_mass = self.probability_top(group)
        if event_mass <= 0:
            raise ValueError("observed top card has zero probability")
        return self._result({
            world: mass / event_mass
            for world, mass in self.masses if world.top == group
        })

    def swap_top_with_face_down(self, position: int) -> PrizePoolBelief:
        if not 0 <= position < self.prize_count:
            raise IndexError("Prize position out of range")
        if self.face_up[position]:
            raise ValueError("cannot swap face-up Prize position")
        output: dict[PrizePoolWorld, float] = defaultdict(float)
        for world, mass in self.masses:
            prizes = list(world.prizes)
            outgoing = prizes[position]
            prizes[position] = world.top
            output[PrizePoolWorld(
                tuple(prizes), outgoing, world.remainder, world.drawn
            )] += mass
        return self._result(output)

    def draw_top_and_refill(self) -> PrizePoolBelief:
        """Move top into tracked hand; sample new top from exchangeable suffix.

        Requires one card in the remaining deck to replace the drawn top.
        """
        output: dict[PrizePoolWorld, float] = defaultdict(float)
        labels: tuple[CardGroup, ...] = (*self.groups, None)
        for world, mass in self.masses:
            available = sum(world.remainder)
            if available <= 0:
                raise ValueError("no card remains for a new deck top")
            updated_drawn = list(world.drawn)
            updated_drawn[self._index(world.top)] += 1
            for i, count in enumerate(world.remainder):
                if count <= 0:
                    continue
                updated_remaining = list(world.remainder)
                updated_remaining[i] -= 1
                result = PrizePoolWorld(
                    world.prizes, labels[i],
                    tuple(updated_remaining), tuple(updated_drawn)
                )
                output[result] += mass * count / available
        return self._result(output)

    def collapse_joint_top_prizes(self) -> PrizePositionTopBelief:
        output: dict[tuple[tuple[CardGroup, ...], CardGroup], float] = defaultdict(float)
        for world, mass in self.masses:
            output[(world.prizes, world.top)] += mass
        return PrizePositionTopBelief(
            self.groups, self.face_up, tuple(output.items())
        )
