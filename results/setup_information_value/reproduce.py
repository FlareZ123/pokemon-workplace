from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from setup_information_value import (  # noqa: E402
    Candidate,
    bayes_decision_value,
    build_examples,
    count_bin_observation,
    diagnostic_exposure_observation,
    identity_utilities,
    observation_table,
)


def assert_close(actual: float, expected: float, tol: float = 1e-12) -> None:
    if not math.isclose(actual, expected, rel_tol=tol, abs_tol=tol):
        raise AssertionError(f"{actual} != {expected}")


def main() -> None:
    low_basic = Candidate("4-Basic candidate", 4, 4)
    high_basic = Candidate("12-Basic candidate", 12, 4)
    density_candidates = (low_basic, high_basic)
    density_observations = observation_table(
        density_candidates,
        {
            candidate.name: count_bin_observation(candidate)
            for candidate in density_candidates
        },
    )
    density = bayes_decision_value(
        density_candidates,
        {candidate.name: 0.5 for candidate in density_candidates},
        identity_utilities(density_candidates),
        density_observations,
    )
    assert_close(density["baseline_value"], 0.5)
    assert_close(density["informed_value"], 0.704926840772299)
    assert_close(density["value_of_information"], 0.204926840772299)
    assert (
        density["observations"]["0 mulligans"]["best_action"]
        == "choose 12-Basic candidate"
    )
    assert (
        density["observations"]["1 mulligan"]["best_action"]
        == "choose 4-Basic candidate"
    )
    assert (
        density["observations"]["2+ mulligans"]["best_action"]
        == "choose 4-Basic candidate"
    )

    four_copy = Candidate("4-copy diagnostic", 4, 4)
    two_copy = Candidate("2-copy diagnostic", 4, 2)
    copy_candidates = (four_copy, two_copy)
    exposure_observations = observation_table(
        copy_candidates,
        {
            candidate.name: diagnostic_exposure_observation(candidate)
            for candidate in copy_candidates
        },
    )
    exposure = bayes_decision_value(
        copy_candidates,
        {candidate.name: 0.5 for candidate in copy_candidates},
        identity_utilities(copy_candidates),
        exposure_observations,
    )
    assert_close(exposure["baseline_value"], 0.5)
    assert_close(exposure["informed_value"], 0.5633081630701052)
    assert_close(exposure["value_of_information"], 0.0633081630701052)

    stable = bayes_decision_value(
        copy_candidates,
        {candidate.name: 0.5 for candidate in copy_candidates},
        {
            "preserve matchup tech": {
                "4-copy diagnostic": 1.0,
                "2-copy diagnostic": 0.72,
            },
            "spend matchup tech": {
                "4-copy diagnostic": 0.35,
                "2-copy diagnostic": 1.0,
            },
        },
        exposure_observations,
    )
    assert stable["baseline_action"] == "preserve matchup tech"
    assert all(
        row["best_action"] == "preserve matchup tech"
        for row in stable["observations"].values()
    )
    assert_close(stable["value_of_information"], 0.0)

    switching = bayes_decision_value(
        copy_candidates,
        {candidate.name: 0.5 for candidate in copy_candidates},
        {
            "preserve matchup tech": {
                "4-copy diagnostic": 1.0,
                "2-copy diagnostic": 0.3,
            },
            "spend matchup tech": {
                "4-copy diagnostic": 0.2,
                "2-copy diagnostic": 1.0,
            },
        },
        exposure_observations,
    )
    assert switching["baseline_action"] == "preserve matchup tech"
    assert (
        switching["observations"]["diagnostic exposed"]["best_action"]
        == "preserve matchup tech"
    )
    assert (
        switching["observations"]["diagnostic not exposed"]["best_action"]
        == "spend matchup tech"
    )
    assert_close(switching["value_of_information"], 0.01375393665836322)

    payload = build_examples()
    assert payload["basic_density_identification_from_count_bins"]
    print("All setup information value checks passed.")
    print("Basic-density decision accuracy:", f"{density['informed_value']:.12%}")
    print("Copy-count decision accuracy:", f"{exposure['informed_value']:.12%}")
    print(
        "Boundary-crossing tactical VOI:",
        f"{switching['value_of_information']:.12%}",
    )


if __name__ == "__main__":
    main()
