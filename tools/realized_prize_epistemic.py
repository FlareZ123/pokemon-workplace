"""Couple a realized physical Prize/top world with observer event-trace beliefs."""

from __future__ import annotations

from dataclasses import dataclass

from observer_positioned_prize_truth import (
    ObserverPositionedPrizes,
    PhysicalPrizeTop,
)
from prize_epistemic_trace import History, PrizeEpistemicTrace
from prize_position_top_swap import PrizePositionTopBelief, World


@dataclass(frozen=True)
class RealizedPrizeEpistemic:
    truth: PhysicalPrizeTop
    trace: PrizeEpistemicTrace
    actual_histories: tuple[History, ...]

    def __post_init__(self) -> None:
        if self.truth.face_up != self.trace.face_up:
            raise ValueError("actual/public Prize visibility mismatch")
        if len(self.actual_histories) != len(self.trace.observers):
            raise ValueError("actual observer history count mismatch")
        if not any(
            row.world == self.truth.projected_world()
            and row.histories == self.actual_histories
            and row.mass > 0
            for row in self.trace.rows
        ):
            raise ValueError("actual physical world/history excluded by trace")

    @classmethod
    def from_prior(
        cls,
        truth: PhysicalPrizeTop,
        prior: PrizePositionTopBelief,
        observers: tuple[str, ...],
    ) -> RealizedPrizeEpistemic:
        trace = PrizeEpistemicTrace.from_joint_prior(prior, observers)
        return cls(truth, trace, tuple(() for _ in observers))

    def as_observer_positioned_prizes(self) -> ObserverPositionedPrizes:
        """Project each player's current history-conditioned joint posterior."""
        return ObserverPositionedPrizes(
            self.truth,
            tuple(
                (observer_id, self.posterior_for(observer_id))
                for observer_id in self.trace.observers
            ),
        )

    def posterior_for(self, observer_id: str) -> PrizePositionTopBelief:
        index = self.trace.observers.index(observer_id)
        observed = self.actual_histories[index]
        selected = [
            row for row in self.trace.rows
            if row.histories[index] == observed
        ]
        mass = sum(row.mass for row in selected)
        if mass <= 0:
            raise ValueError("actual observer history is impossible")
        output: dict[World, float] = {}
        for row in selected:
            output[row.world] = output.get(row.world, 0.0) + row.mass / mass
        return PrizePositionTopBelief(
            self.trace.groups,
            self.trace.face_up,
            tuple(output.items()),
        )

    def private_peek(
        self,
        observer_id: str,
        *,
        zone: str,
        position: int | None = None,
    ) -> RealizedPrizeEpistemic:
        next_trace = self.trace.private_peek(
            observer_id, zone=zone, position=position
        )
        return self._advance(self.truth, next_trace)

    def selected_swap(
        self,
        *,
        actor_id: str,
        selected_position: int,
        policy_by_actor_history: dict[History, dict[int, float]],
    ) -> RealizedPrizeEpistemic:
        next_truth = self.truth.swap(selected_position)
        next_trace = self.trace.select_and_swap(
            actor_id=actor_id,
            selected_position=selected_position,
            policy_by_actor_history=policy_by_actor_history,
        )
        return self._advance(next_truth, next_trace)

    def hidden_shuffle(
        self, realized_source_order: tuple[int, ...]
    ) -> RealizedPrizeEpistemic:
        next_truth = self.truth.shuffle(realized_source_order)
        next_trace = self.trace.hidden_shuffle()
        return self._advance(next_truth, next_trace)

    def public_reveal(self, position: int) -> RealizedPrizeEpistemic:
        actual_group = self.truth.projected_world()[0][position]
        return self._advance(
            self.truth.reveal(position),
            self.trace.public_reveal(position, actual_group),
        )

    def _advance(
        self,
        new_truth: PhysicalPrizeTop,
        new_trace: PrizeEpistemicTrace,
    ) -> RealizedPrizeEpistemic:
        """Determine the actual observation history from the realized world."""
        candidates = {
            row.histories for row in new_trace.rows
            if row.world == new_truth.projected_world()
            and all(
                next_history[:len(previous)] == previous
                for next_history, previous in zip(
                    row.histories, self.actual_histories
                )
            )
        }
        if len(candidates) != 1:
            raise ValueError("realized transition has ambiguous/impossible history")
        return RealizedPrizeEpistemic(
            new_truth, new_trace, next(iter(candidates))
        )
