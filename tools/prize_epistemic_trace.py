"""Finite hidden-world event traces derive actor information from observations.

The transition kernel records private and public observations separately for
each possible world. Public position choices are generated from the actor's
recorded information history, preventing actions conditional on never-seen
physical Prize assignments. This is a bounded epistemic model, not a full game.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from itertools import permutations
from math import factorial, isclose
from typing import Callable, Mapping

from prize_position_top_swap import CardGroup, PrizePositionTopBelief, World

History = tuple[str, ...]


@dataclass(frozen=True)
class TraceRow:
    world: World
    mass: float
    histories: tuple[History, ...]


@dataclass(frozen=True)
class PrizeEpistemicTrace:
    groups: tuple[str, ...]
    face_up: tuple[bool, ...]
    observers: tuple[str, ...]
    rows: tuple[TraceRow, ...]

    def __post_init__(self) -> None:
        if not self.observers or len(set(self.observers)) != len(self.observers):
            raise ValueError("observer IDs must be unique and nonempty")
        if not self.rows or not isclose(
            sum(row.mass for row in self.rows), 1, abs_tol=1e-10
        ):
            raise ValueError("trace rows must have total probability one")
        keys = set()
        for row in self.rows:
            prizes, top = row.world
            if not 0 < row.mass <= 1 or len(prizes) != len(self.face_up):
                raise ValueError("invalid physical world or probability")
            if len(row.histories) != len(self.observers):
                raise ValueError("observer history count mismatch")
            if any(card is not None and card not in self.groups
                   for card in (*prizes, top)):
                raise ValueError("unmodeled card group")
            key = row.world, row.histories
            if key in keys:
                raise ValueError("identical world histories must be merged")
            keys.add(key)
        for pos, face_up in enumerate(self.face_up):
            if face_up and len({row.world[0][pos] for row in self.rows}) > 1:
                raise ValueError("face-up card must have public known group")

    @classmethod
    def from_joint_prior(
        cls,
        prior: PrizePositionTopBelief,
        observers: tuple[str, ...],
    ) -> PrizeEpistemicTrace:
        return cls(
            prior.groups, prior.face_up, observers,
            tuple(
                TraceRow(world, mass, tuple(() for _ in observers))
                for world, mass in prior.masses
            ),
        )

    def histories_for(self, observer_id: str) -> frozenset[History]:
        index = self.observers.index(observer_id)
        return frozenset(row.histories[index] for row in self.rows)

    def conditional_probability(
        self,
        observer_id: str,
        history: History,
        event: Callable[[World], bool],
    ) -> float:
        index = self.observers.index(observer_id)
        masses = [row for row in self.rows if row.histories[index] == history]
        total = sum(row.mass for row in masses)
        if total <= 0:
            raise ValueError("observation history has zero probability")
        return sum(row.mass for row in masses if event(row.world)) / total

    def private_peek(
        self,
        observer_id: str,
        *,
        zone: str,
        position: int | None = None,
    ) -> PrizeEpistemicTrace:
        """Record a source-authorized top/Prize inspection in private histories."""
        index = self.observers.index(observer_id)
        if zone == "prize":
            if position is None or not 0 <= position < len(self.face_up):
                raise ValueError("Prize peek needs a valid position")
            locus = f"prize:{position}"
            group_at = lambda w: w[0][position]
        elif zone == "top":
            if position is not None:
                raise ValueError("top peek has no Prize position")
            locus = "top"
            group_at = lambda w: w[1]
        else:
            raise ValueError("only one Prize position or deck top is modeled")
        updated = []
        for row in self.rows:
            histories = list(row.histories)
            for observer_index, history in enumerate(histories):
                observation = (
                    f"private:{locus}:{group_at(row.world)!r}"
                    if observer_index == index
                    else f"public:peek:{locus}"
                )
                histories[observer_index] = history + (observation,)
            updated.append(TraceRow(row.world, row.mass, tuple(histories)))
        return self._new(self.face_up, updated)

    def select_and_swap(
        self,
        *,
        actor_id: str,
        selected_position: int,
        policy_by_actor_history: Mapping[History, Mapping[int, float]],
    ) -> PrizeEpistemicTrace:
        """Condition on publicly selected Prize slot, then perform its swap."""
        actor_index = self.observers.index(actor_id)
        if not 0 <= selected_position < len(self.face_up):
            raise IndexError("selected position out of range")
        if self.face_up[selected_position]:
            raise ValueError("cannot select a face-up Prize")
        eligible = {i for i, up in enumerate(self.face_up) if not up}
        if set(policy_by_actor_history) != self.histories_for(actor_id):
            raise ValueError("policy must cover all actor information histories")
        for choice_dist in policy_by_actor_history.values():
            if set(choice_dist) != eligible:
                raise ValueError("policy must cover each eligible slot")
            if any(not 0 <= p <= 1 for p in choice_dist.values()):
                raise ValueError("invalid choice probability")
            if not isclose(sum(choice_dist.values()), 1, abs_tol=1e-12):
                raise ValueError("choice probabilities must sum to one")

        updated = []
        for row in self.rows:
            likelihood = policy_by_actor_history[
                row.histories[actor_index]
            ][selected_position]
            if likelihood <= 0:
                continue
            prizes, top = row.world
            next_prizes = list(prizes)
            outgoing = next_prizes[selected_position]
            next_prizes[selected_position] = top
            histories = tuple(
                history + (f"public:swap:{selected_position}",)
                for history in row.histories
            )
            updated.append(
                TraceRow(
                    (tuple(next_prizes), outgoing),
                    row.mass * likelihood,
                    histories,
                )
            )
        if not updated:
            raise ValueError("observed selected slot has zero probability")
        return self._new(self.face_up, updated)

    def hidden_shuffle(self) -> PrizeEpistemicTrace:
        """Marginalize a uniform shuffle of currently face-down positions."""
        eligible = tuple(i for i, up in enumerate(self.face_up) if not up)
        denominator = factorial(len(eligible))
        updated = []
        for row in self.rows:
            prizes, top = row.world
            histories = tuple(
                history + ("public:shuffle-face-down",)
                for history in row.histories
            )
            for source_order in permutations(eligible):
                next_prizes = list(prizes)
                for dest, source in zip(eligible, source_order):
                    next_prizes[dest] = prizes[source]
                updated.append(
                    TraceRow(
                        (tuple(next_prizes), top),
                        row.mass / denominator,
                        histories,
                    )
                )
        return self._new(self.face_up, updated)

    def public_reveal(
        self,
        position: int,
        observed_group: CardGroup,
    ) -> PrizeEpistemicTrace:
        if not 0 <= position < len(self.face_up):
            raise IndexError("position out of range")
        if self.face_up[position]:
            raise ValueError("position already face up")
        updated = []
        for row in self.rows:
            if row.world[0][position] == observed_group:
                histories = tuple(
                    history + (f"public:reveal:{position}:{observed_group!r}",)
                    for history in row.histories
                )
                updated.append(TraceRow(row.world, row.mass, histories))
        if not updated:
            raise ValueError("revealed group had zero prior probability")
        mask = list(self.face_up)
        mask[position] = True
        return self._new(tuple(mask), updated)

    def _new(
        self, face_up: tuple[bool, ...], rows: list[TraceRow]
    ) -> PrizeEpistemicTrace:
        grouped: dict[tuple[World, tuple[History, ...]], float] = defaultdict(float)
        for row in rows:
            grouped[(row.world, row.histories)] += row.mass
        total = sum(grouped.values())
        return PrizeEpistemicTrace(
            self.groups, face_up, self.observers,
            tuple(
                TraceRow(world, mass / total, histories)
                for (world, histories), mass in sorted(
                    grouped.items(), key=lambda item: repr(item[0])
                )
                if mass > 0
            ),
        )
