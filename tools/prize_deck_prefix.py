"""Conserved Prize/deck belief with a variable-length ordered deck suffix prefix.

The current top is stored in PrizePoolWorld. Each PrefixWorld additionally
tracks k ordered positions immediately behind the top; those cards remain
included in the physical remainder inventory and are counted only once.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from math import isclose
from typing import Mapping

from prize_position_top_swap import CardGroup
from prize_top_draw_pool import PrizePoolBelief, PrizePoolWorld


@dataclass(frozen=True)
class PrefixWorld:
    pool: PrizePoolWorld
    suffix_prefix: tuple[CardGroup, ...]


@dataclass(frozen=True)
class PrizeDeckPrefixBelief:
    groups: tuple[str, ...]
    totals: tuple[int, ...]
    face_up: tuple[bool, ...]
    masses: tuple[tuple[PrefixWorld, float], ...]

    def __post_init__(self) -> None:
        if not self.masses or not isclose(
            sum(mass for _, mass in self.masses), 1, abs_tol=1e-10
        ):
            raise ValueError("prefix probabilities must sum to one")
        lengths = {len(world.suffix_prefix) for world, _ in self.masses}
        if len(lengths) != 1:
            raise ValueError("prefix depth must match across support")
        if len({world for world, _ in self.masses}) != len(self.masses):
            raise ValueError("duplicate prefix worlds")
        labels = (*self.groups, None)
        collapsed: dict[PrizePoolWorld, float] = defaultdict(float)
        for world, mass in self.masses:
            if not 0 < mass <= 1:
                raise ValueError("invalid world probability")
            if any(card not in labels for card in world.suffix_prefix):
                raise ValueError("unknown group in suffix prefix")
            counted = Counter(world.suffix_prefix)
            for i, label in enumerate(labels):
                if counted[label] > world.pool.remainder[i]:
                    raise ValueError("ordered prefix exceeds remaining group copies")
            collapsed[world.pool] += mass
        PrizePoolBelief(
            self.groups, self.totals, self.face_up,
            tuple(collapsed.items())
        )

    @classmethod
    def from_exchangeable_pool(
        cls,
        pool: PrizePoolBelief,
        *,
        depth: int,
    ) -> PrizeDeckPrefixBelief:
        """Materialize the next depth deck positions without replacement."""
        if depth < 0:
            raise ValueError("prefix depth must be nonnegative")
        labels: tuple[CardGroup, ...] = (*pool.groups, None)
        output: dict[PrefixWorld, float] = defaultdict(float)

        def expand(
            base: PrizePoolWorld,
            mass: float,
            prefix: tuple[CardGroup, ...],
            available: tuple[int, ...],
        ) -> None:
            if len(prefix) == depth:
                output[PrefixWorld(base, prefix)] += mass
                return
            denominator = sum(available)
            if denominator <= 0:
                raise ValueError("depth exceeds remaining deck size")
            for index, count in enumerate(available):
                if count:
                    remaining = list(available)
                    remaining[index] -= 1
                    expand(
                        base,
                        mass * count / denominator,
                        prefix + (labels[index],),
                        tuple(remaining),
                    )

        for world, mass in pool.masses:
            expand(world, mass, (), world.remainder)

        return cls(
            pool.groups, pool.totals, pool.face_up,
            tuple(sorted(output.items(), key=lambda item: repr(item[0])))
        )

    @property
    def depth(self) -> int:
        return len(self.masses[0][0].suffix_prefix)

    def to_exchangeable_pool(self) -> PrizePoolBelief:
        """Forget all ordered suffix positions, keeping conserved group counts."""
        output: dict[PrizePoolWorld, float] = defaultdict(float)
        for world, mass in self.masses:
            output[world.pool] += mass
        return PrizePoolBelief(
            self.groups, self.totals, self.face_up,
            tuple(output.items())
        )

    def _result(self, output: Mapping[PrefixWorld, float]) -> PrizeDeckPrefixBelief:
        return PrizeDeckPrefixBelief(
            self.groups, self.totals, self.face_up,
            tuple(sorted(output.items(), key=lambda item: repr(item[0])))
        )

    def probability_at_deck_position(
        self, position: int, group: CardGroup
    ) -> float:
        """Deck position 0 is current top; positions 1..depth are prefix."""
        if not 0 <= position <= self.depth:
            raise IndexError("deck position outside modeled prefix")
        if group is not None and group not in self.groups:
            raise ValueError("unknown observed group")
        return sum(
            mass for world, mass in self.masses
            if (
                world.pool.top if position == 0
                else world.suffix_prefix[position - 1]
            ) == group
        )

    def observe_deck_position(
        self, position: int, group: CardGroup
    ) -> PrizeDeckPrefixBelief:
        likelihood = self.probability_at_deck_position(position, group)
        if likelihood <= 0:
            raise ValueError("observation has zero probability")
        return self._result({
            world: mass / likelihood
            for world, mass in self.masses
            if (
                world.pool.top if position == 0
                else world.suffix_prefix[position - 1]
            ) == group
        })

    def swap_top_with_face_down(self, position: int) -> PrizeDeckPrefixBelief:
        if not 0 <= position < len(self.face_up):
            raise IndexError("Prize position out of range")
        if self.face_up[position]:
            raise ValueError("cannot swap face-up Prize")
        output: dict[PrefixWorld, float] = defaultdict(float)
        for world, mass in self.masses:
            base = world.pool
            prizes = list(base.prizes)
            outgoing = prizes[position]
            prizes[position] = base.top
            output[PrefixWorld(
                PrizePoolWorld(
                    tuple(prizes), outgoing, base.remainder, base.drawn
                ), world.suffix_prefix
            )] += mass
        return self._result(output)

    def draw_top_and_advance(self) -> PrizeDeckPrefixBelief:
        """Draw current top and expose the next, retaining up to depth suffix."""
        labels: tuple[CardGroup, ...] = (*self.groups, None)
        output: dict[PrefixWorld, float] = defaultdict(float)

        for world, mass in self.masses:
            base = world.pool
            drawn = list(base.drawn)
            drawn[labels.index(base.top)] += 1

            if world.suffix_prefix:
                next_top = world.suffix_prefix[0]
                remainder = list(base.remainder)
                remainder[labels.index(next_top)] -= 1
                carried = world.suffix_prefix[1:]
            else:
                next_top = None
                remainder = list(base.remainder)
                carried = ()

            free = list(remainder)
            for card in carried:
                free[labels.index(card)] -= 1
            if any(c < 0 for c in free):
                raise AssertionError("known-prefix card consumed twice")

            if world.suffix_prefix:
                if sum(free) > 0:
                    choices = (
                        (labels[i], count / sum(free))
                        for i, count in enumerate(free) if count
                    )
                else:
                    choices = ((None, 1.0),)  # sentinel: do not append on exhaustion
            else:
                available = sum(free)
                if available <= 0:
                    raise ValueError("no card remains to become new deck top")
                choices = (
                    (labels[i], count / available)
                    for i, count in enumerate(free) if count
                )

            for card, weight in choices:
                if not world.suffix_prefix:
                    next_index = labels.index(card)
                    next_remainder = list(remainder)
                    next_remainder[next_index] -= 1
                    next_world = PrefixWorld(
                        PrizePoolWorld(
                            base.prizes, card, tuple(next_remainder),
                            tuple(drawn)
                        ), ()
                    )
                else:
                    next_world = PrefixWorld(
                        PrizePoolWorld(
                            base.prizes, next_top, tuple(remainder),
                            tuple(drawn)
                        ),
                        carried + ((card,) if sum(free) > 0 else ()),
                    )
                output[next_world] += mass * weight

        return self._result(output)
