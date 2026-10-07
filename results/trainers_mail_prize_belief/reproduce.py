from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from trainers_mail_prize_belief import (
    first_gladion_preferred_miss,
    posterior_after_misses,
)


def main() -> None:
    expected = (
        Fraction(3, 26),
        Fraction(1, 8),
        Fraction(23, 170),
        Fraction(529, 3616),
        Fraction(12167, 76994),
    )

    for misses, prize_probability in enumerate(expected):
        belief = posterior_after_misses(misses)
        assert belief.prize_probability == prize_probability
        assert belief.prize_probability + belief.deck_probability == 1
        assert belief.exact_information_value == min(
            belief.prize_probability,
            belief.deck_probability,
        )

    assert first_gladion_preferred_miss() == 23

    for misses in range(5):
        belief = posterior_after_misses(misses)
        assert belief.deck_probability > belief.prize_probability

    print("trainers_mail_prize_belief: all assertions passed")
    for misses in range(5):
        belief = posterior_after_misses(misses)
        print(
            misses,
            f"prized={float(belief.prize_probability):.12%}",
            f"exact-info-value={float(belief.exact_information_value):.12%}",
        )
    print("first Gladion-preferred miss count:", first_gladion_preferred_miss())


if __name__ == "__main__":
    main()
