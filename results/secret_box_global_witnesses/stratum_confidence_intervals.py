"""Wilson intervals for rare-Prize conditional output-necessity incidences.

Three 100k-accepted-opening strata are PINNED to the verified sampled
counts from full Prize importance workflow 38051488314.
The six-Prize Item stratum has only 13 successes; report uncertainty.

These are approximate confidence intervals for conditional binomial
sampling error, scaled by an EXACT forced-Prize event probability.
They exclude uncertainty from the compressed game model itself.
"""

from fractions import Fraction
from math import sqrt
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))

from accepted_opening_prize_probabilities import (
    fixed_nonbasic_prized_given_valid_opener,
)


N = 100_000
Z = 1.959963984540054
EVENTS = (
    ("Tag Call ×4 / requires Supporter", 4, 6_063),
    ("Guzma & Hala ×4 / requires Tool and Stadium", 4, 1_283),
    ("Stealthy Hood ×3 + Counter Gain + Artazon ×2 / requires Item", 6, 13),
)


def wilson_interval(successes: int, trials: int, z: float = Z) -> tuple[float, float]:
    """Two-sided Wilson score confidence interval for a Bernoulli rate."""
    if trials <= 0 or not 0 <= successes <= trials:
        raise ValueError("invalid successes or trial count")
    proportion = successes / trials
    z2 = z * z
    denominator = 1 + z2 / trials
    center = (proportion + z2 / (2 * trials)) / denominator
    halfwidth = (
        z
        * sqrt(
            proportion * (1 - proportion) / trials
            + z2 / (4 * trials * trials)
        )
        / denominator
    )
    return (center - halfwidth, center + halfwidth)


def main() -> None:
    assert wilson_interval(0, 10)[0] == 0
    assert wilson_interval(10, 10)[1] == 1
    assert wilson_interval(5, 10)[0] < 0.5 < wilson_interval(5, 10)[1]

    expected = {
        "Tag Call ×4 / requires Supporter": (1.913224015, 1.867079012, 1.960434187),
        "Guzma & Hala ×4 / requires Tool and Stadium": (
            0.404860038, 0.383432275, 0.427468852
        ),
        "Stealthy Hood ×3 + Counter Gain + Artazon ×2 / requires Item": (
            0.000002697, 0.000001576, 0.000004615
        ),
    }

    for label, forced_count, successes in EVENTS:
        forced_odds = fixed_nonbasic_prized_given_valid_opener(
            cards=60, basics=14, opening=7,
            prizes=6, forced_nonbasic=forced_count,
        )
        conditional_lower, conditional_upper = wilson_interval(successes, N)
        per_million_point = float(
            forced_odds * Fraction(successes, N) * 1_000_000
        )
        per_million_lower = float(forced_odds) * conditional_lower * 1_000_000
        per_million_upper = float(forced_odds) * conditional_upper * 1_000_000
        benchmark = expected[label]
        for actual, target in zip(
            (per_million_point, per_million_lower, per_million_upper),
            benchmark,
        ):
            assert abs(actual - target) < 0.000000001, (actual, target)

        print(label)
        print("  conditional rate:", successes, "/", N)
        print("  exact forced Prize probability:", forced_odds)
        print(
            "  estimated cases per million valid starts:",
            f"{per_million_point:.12g}",
        )
        print(
            "  95% Wilson interval per million:",
            f"[{per_million_lower:.12g}, {per_million_upper:.12g}]",
        )

    print("All Wilson uncertainty regressions passed.")


if __name__ == "__main__":
    main()
