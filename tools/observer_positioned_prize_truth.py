"""Synchronize physical card-instance Prize positions with observer posteriors."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping
from prize_position_top_swap import CardGroup, PrizePositionTopBelief


@dataclass(frozen=True)
class PhysicalPrizeTop:
    """Exact unique instance IDs at each Prize position and the deck top."""

    prizes: tuple[str, ...]
    deck_top: str
    face_up: tuple[bool, ...]
    groups_by_instance: tuple[tuple[str, CardGroup], ...]

    def __post_init__(self) -> None:
        if len(self.prizes) != len(self.face_up):
            raise ValueError("Prize and visibility lengths differ")
        current = (*self.prizes, self.deck_top)
        if len(current) != len(set(current)):
            raise ValueError("physical card instances must be distinct")
        labels = dict(self.groups_by_instance)
        if len(labels) != len(self.groups_by_instance) or not all(
            card in labels for card in current
        ):
            raise ValueError("physical instances require unique group mappings")

    def projected_world(self) -> tuple[tuple[CardGroup, ...], CardGroup]:
        labels = dict(self.groups_by_instance)
        return tuple(labels[c] for c in self.prizes), labels[self.deck_top]

    def swap(self, index: int) -> PhysicalPrizeTop:
        if not 0 <= index < len(self.prizes):
            raise IndexError("Prize position out of range")
        if self.face_up[index]:
            raise ValueError("cannot swap a face-up Prize")
        prizes = list(self.prizes)
        outgoing = prizes[index]
        prizes[index] = self.deck_top
        return PhysicalPrizeTop(
            tuple(prizes), outgoing, self.face_up, self.groups_by_instance
        )

    def shuffle(self, sources: tuple[int, ...]) -> PhysicalPrizeTop:
        """Use one externally sampled physical permutation of face-down Prizes."""
        positions = tuple(i for i, up in enumerate(self.face_up) if not up)
        if len(sources) != len(positions) or set(sources) != set(positions):
            raise ValueError("shuffle must permute exactly face-down positions")
        updated = list(self.prizes)
        for destination, source in zip(positions, sources):
            updated[destination] = self.prizes[source]
        return PhysicalPrizeTop(
            tuple(updated), self.deck_top, self.face_up, self.groups_by_instance
        )

    def reveal(self, index: int) -> PhysicalPrizeTop:
        if not 0 <= index < len(self.prizes):
            raise IndexError("Prize position out of range")
        if self.face_up[index]:
            raise ValueError("Prize already face up")
        flags = list(self.face_up)
        flags[index] = True
        return PhysicalPrizeTop(
            self.prizes, self.deck_top, tuple(flags), self.groups_by_instance
        )


@dataclass(frozen=True)
class ObserverPositionedPrizes:
    """One immutable physical truth plus multiple information-state beliefs."""

    truth: PhysicalPrizeTop
    observers: tuple[tuple[str, PrizePositionTopBelief], ...]

    def __post_init__(self) -> None:
        identities = [identity for identity, _ in self.observers]
        if not identities or len(set(identities)) != len(identities):
            raise ValueError("observer identities must be distinct and nonempty")
        actual = self.truth.projected_world()
        for _, belief in self.observers:
            if belief.face_up != self.truth.face_up:
                raise ValueError("observer visibility disagrees with physical truth")
            if not any(w == actual and mass > 0 for w, mass in belief.masses):
                raise ValueError("observer posterior excludes the physical truth")

    def belief_for(self, observer_id: str) -> PrizePositionTopBelief:
        for identity, belief in self.observers:
            if identity == observer_id:
                return belief
        raise KeyError(observer_id)

    def peek_top(self, observer_id: str) -> ObserverPositionedPrizes:
        if observer_id not in dict(self.observers):
            raise KeyError(observer_id)
        actual_group = self.truth.projected_world()[1]
        return ObserverPositionedPrizes(
            self.truth,
            tuple(
                (i, b.observe_top(actual_group) if i == observer_id else b)
                for i, b in self.observers
            ),
        )

    def swap(
        self,
        index: int,
        *,
        observed_choice_likelihoods: Mapping[
            str, Mapping[CardGroup, float]
        ] | None = None,
    ) -> ObserverPositionedPrizes:
        if observed_choice_likelihoods and not set(
            observed_choice_likelihoods
        ) <= dict(self.observers).keys():
            raise ValueError("unknown observer in policy likelihoods")
        next_truth = self.truth.swap(index)
        updated = []
        for identity, belief in self.observers:
            if observed_choice_likelihoods and identity in observed_choice_likelihoods:
                belief = belief.condition_on_public_swap(
                    observed_choice_likelihoods[identity]
                )
            updated.append((identity, belief.swap_face_down_with_top(index)))
        return ObserverPositionedPrizes(next_truth, tuple(updated))

    def shuffle(self, sources: tuple[int, ...]) -> ObserverPositionedPrizes:
        """The caller draws a uniform permutation, hidden from each observer."""
        return ObserverPositionedPrizes(
            self.truth.shuffle(sources),
            tuple((i, b.shuffle_face_down_positions()) for i, b in self.observers),
        )

    def reveal(self, index: int) -> ObserverPositionedPrizes:
        next_truth = self.truth.reveal(index)
        revealed_group = self.truth.projected_world()[0][index]
        return ObserverPositionedPrizes(
            next_truth,
            tuple((i, b.reveal_prize(index, revealed_group)) for i, b in self.observers),
        )
