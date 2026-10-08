"""Exact value of shuffling before a full-hand reset draw."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ShuffleValue:
    deck_size: int
    draw_count: int
    target_in_draw_window_probability: float

    @property
    def shuffled_hit_probability(self) -> float:
        return self.draw_count / self.deck_size

    @property
    def unshuffled_hit_probability(self) -> float:
        return self.target_in_draw_window_probability

    @property
    def shuffle_delta(self) -> float:
        return self.shuffled_hit_probability - self.unshuffled_hit_probability


def shuffle_value(
    deck_size: int,
    draw_count: int,
    target_in_draw_window_probability: float,
) -> ShuffleValue:
    if deck_size <= 0:
        raise ValueError("deck_size must be positive")
    if not 0 <= draw_count <= deck_size:
        raise ValueError("draw_count must lie between zero and deck_size")
    if not 0.0 <= target_in_draw_window_probability <= 1.0:
        raise ValueError("probability must lie between zero and one")
    return ShuffleValue(deck_size, draw_count, target_in_draw_window_probability)


def known_top_nontarget_window_probability(
    deck_size: int,
    draw_count: int,
) -> float:
    """Target hit probability with a known non-target top and uniform remainder."""

    if deck_size <= 1:
        return 0.0
    if not 1 <= draw_count <= deck_size:
        raise ValueError("draw_count must lie between one and deck_size")
    return (draw_count - 1) / (deck_size - 1)
