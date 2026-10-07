"""Hand-size and draw-to-N consequences of mandatory unrestricted search filler."""

from __future__ import annotations

from dataclasses import dataclass

from unrestricted_search_selection import unrestricted_fixed_bounds


@dataclass(frozen=True)
class SearchDrawBandwidthOutcome:
    selected_units: int
    useful_units: int
    forced_filler_units: int
    physical_hand_before_draw: int
    useful_only_hand_before_draw: int
    physical_draws: int
    useful_only_draws: int

    @property
    def draw_overstatement(self) -> int:
        return self.useful_only_draws - self.physical_draws


def draw_to_n_count(hand_size: int, target_size: int) -> int:
    if hand_size < 0:
        raise ValueError("hand_size must be non-negative")
    if target_size < 0:
        raise ValueError("target_size must be non-negative")
    return max(0, target_size - hand_size)


def unrestricted_search_then_draw_to_n(
    *,
    initial_hand_size: int,
    search_card_from_hand: bool,
    discard_cost_from_hand: int,
    specified_count: int,
    deck_size_at_search: int,
    useful_units: int,
    later_hand_plays: int,
    draw_to: int,
) -> SearchDrawBandwidthOutcome:
    """Compare physical search selection with a useful-output-only abstraction."""

    if initial_hand_size < 0:
        raise ValueError("initial_hand_size must be non-negative")
    if discard_cost_from_hand < 0 or later_hand_plays < 0:
        raise ValueError("hand costs must be non-negative")

    selected = unrestricted_fixed_bounds(
        specified_count=specified_count,
        deck_size=deck_size_at_search,
    ).minimum
    if not 0 <= useful_units <= selected:
        raise ValueError("useful_units must lie between zero and selected units")

    hand_cost = int(search_card_from_hand) + discard_cost_from_hand + later_hand_plays
    base = initial_hand_size - hand_cost
    if base < 0:
        raise ValueError("represented hand costs exceed the initial hand")

    physical_hand = base + selected
    useful_only_hand = base + useful_units
    return SearchDrawBandwidthOutcome(
        selected_units=selected,
        useful_units=useful_units,
        forced_filler_units=selected - useful_units,
        physical_hand_before_draw=physical_hand,
        useful_only_hand_before_draw=useful_only_hand,
        physical_draws=draw_to_n_count(physical_hand, draw_to),
        useful_only_draws=draw_to_n_count(useful_only_hand, draw_to),
    )
