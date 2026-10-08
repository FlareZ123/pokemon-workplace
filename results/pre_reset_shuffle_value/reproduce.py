"""Reproduce pre-reset shuffle-value thresholds."""

from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from pre_reset_shuffle_value import (
    known_top_nontarget_window_probability,
    shuffle_value,
)


def close(actual: float, expected: float) -> None:
    assert abs(actual - expected) < 1e-12, (actual, expected)


def main() -> None:
    deck_size = 46
    draw_count = 6
    uniform = Fraction(draw_count, deck_size)

    neutral = shuffle_value(deck_size, draw_count, float(uniform))
    close(neutral.shuffle_delta, 0.0)

    known_hit = shuffle_value(deck_size, draw_count, 1.0)
    close(known_hit.shuffled_hit_probability, float(Fraction(3, 23)))
    close(known_hit.shuffle_delta, float(Fraction(-20, 23)))

    known_miss = shuffle_value(deck_size, draw_count, 0.0)
    close(known_miss.shuffle_delta, float(Fraction(3, 23)))

    top_miss_probability = known_top_nontarget_window_probability(
        deck_size,
        draw_count,
    )
    close(top_miss_probability, float(Fraction(1, 9)))
    top_miss = shuffle_value(deck_size, draw_count, top_miss_probability)
    close(top_miss.shuffle_delta, float(Fraction(4, 207)))

    print("Pre-reset shuffle-value regression: PASS")


if __name__ == "__main__":
    main()
