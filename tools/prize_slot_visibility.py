"""Face-up visibility over the existing position-aware Prize belief kernel."""

from __future__ import annotations

from dataclasses import dataclass

from prize_position_belief import PrizeGroup, PrizePositionBelief


@dataclass(frozen=True)
class PrizeSlotVisibilityBelief:
    """Position-aware Prize belief plus deterministic public face-up status."""

    positions: PrizePositionBelief
    face_up: tuple[bool, ...]

    def __post_init__(self) -> None:
        if len(self.face_up) != self.positions.prize_count:
            raise ValueError("face_up must align with every Prize position")

        for index, is_face_up in enumerate(self.face_up):
            if not is_face_up:
                continue
            support = {
                state[index]
                for state, probability in self.positions.masses
                if probability > 0.0
            }
            if len(support) != 1:
                raise ValueError(
                    "a face-up position must have a known grouped identity"
                )

    @classmethod
    def all_face_down(
        cls,
        positions: PrizePositionBelief,
    ) -> "PrizeSlotVisibilityBelief":
        return cls(
            positions,
            tuple(False for _ in range(positions.prize_count)),
        )

    def face_down_positions(self) -> tuple[int, ...]:
        return tuple(
            index
            for index, is_face_up in enumerate(self.face_up)
            if not is_face_up
        )

    def face_up_positions(self) -> tuple[int, ...]:
        return tuple(
            index
            for index, is_face_up in enumerate(self.face_up)
            if is_face_up
        )

    def best_face_down_probability(
        self,
        group: PrizeGroup,
    ) -> float:
        """Best hit probability when only a face-down position is eligible."""

        eligible = self.face_down_positions()
        if not eligible:
            raise ValueError("no face-down Prize positions remain")
        return max(
            self.positions.group_probability_at(position, group)
            for position in eligible
        )

    def reveal_position(
        self,
        position: int,
        observed_group: PrizeGroup,
    ) -> "PrizeSlotVisibilityBelief":
        """Condition on one slot's identity and turn that position face up."""

        if not 0 <= position < self.positions.prize_count:
            raise IndexError("position out of range")
        if self.face_up[position]:
            raise ValueError("position is already face up")

        conditioned = self.positions.condition_position(
            position,
            observed_group,
        )
        visibility = list(self.face_up)
        visibility[position] = True
        return PrizeSlotVisibilityBelief(
            conditioned,
            tuple(visibility),
        )

    def turn_all_face_down_and_shuffle(
        self,
    ) -> "PrizeSlotVisibilityBelief":
        """Apply an E-35-style face-down shuffle to every Prize position."""

        shuffled = self.positions.shuffle_positions()
        return PrizeSlotVisibilityBelief.all_face_down(shuffled)


def known_group_at_face_up(
    state: PrizeSlotVisibilityBelief,
    position: int,
) -> PrizeGroup:
    if not 0 <= position < state.positions.prize_count:
        raise IndexError("position out of range")
    if not state.face_up[position]:
        raise ValueError("position is not face up")

    support = {
        row[position]
        for row, probability in state.positions.masses
        if probability > 0.0
    }
    if len(support) != 1:
        raise AssertionError("face-up position identity is not exact")
    return next(iter(support))
