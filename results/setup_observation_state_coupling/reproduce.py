"""Compose Aichi mulligan inference with Iron Thorns bonus-card state changes."""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from aichi_setup_inference import (  # noqa: E402
    ExactListCandidate,
    acceptance_probability,
    mulligan_probability,
    posterior_left_after_exact_mulligans,
)
from iron_thorns_mulligan_bonus import (  # noqa: E402
    exact_probability,
    matchup_adjusted_probability,
)


def close(actual: float, expected: float) -> None:
    if not math.isclose(actual, expected, rel_tol=1e-11, abs_tol=1e-11):
        raise AssertionError(f"{actual} != {expected}")


def main() -> None:
    iron = ExactListCandidate("Kazuma Iron Thorns", 4, 0)
    vile = ExactListCandidate("Ando Vileplume", 14, 0)

    expected_iron_posteriors = (
        0.31683463533901846,
        0.6677178962428857,
        0.8969808734091667,
        0.9741777759679516,
        0.9939196657149556,
        0.9985901134063959,
    )
    expected_line = (
        0.34008906143861073,
        0.3788457812695931,
        0.4155138839854457,
        0.4501309200874209,
        0.4827411487803291,
        0.5133947243143232,
    )

    q_iron = mulligan_probability(iron)
    q_vile = mulligan_probability(vile)
    observation_mass = 0.0

    print("setup_observation_state_coupling: all assertions passed")
    for mulligans in range(6):
        posterior_iron = posterior_left_after_exact_mulligans(
            iron,
            vile,
            mulligans,
        )
        line = exact_probability(mulligans)
        close(posterior_iron, expected_iron_posteriors[mulligans])
        close(line, expected_line[mulligans])

        iron_joint = 0.5 * q_iron**mulligans * acceptance_probability(iron)
        vile_joint = 0.5 * q_vile**mulligans * acceptance_probability(vile)
        mass = iron_joint + vile_joint
        observation_mass += mass

        print(
            mulligans,
            f"observation_mass={mass:.12%}",
            f"posterior_iron={posterior_iron:.12%}",
            f"volt_cyclone={line:.12%}",
        )

    mixture = 0.5 * (
        matchup_adjusted_probability(4)
        + matchup_adjusted_probability(14)
    )
    close(mixture, 0.3700265137315634)
    assert observation_mass < 1.0

    print(f"equal_prior_matchup_mixture={mixture:.12%}")
    print(f"mass_in_first_six_counts={observation_mass:.12%}")


if __name__ == "__main__":
    main()
