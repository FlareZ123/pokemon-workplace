"""Reproduce the Harto Forest Seal Stone pre-search sequencing result."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from raichu_presearch_forest_seal import forest_seal_presearch_snapshot


def main() -> None:
    result = forest_seal_presearch_snapshot()

    assert abs(result.observable_branch_mass - 0.03616755972964512) < 1e-12
    assert result.observation_count == 1331
    assert result.hosted_observation_count == 244

    assert abs(result.hosted_forest_fraction - 0.018228341144079625) < 1e-12
    assert abs(
        result.hosted_forest_baseline_success
        - 0.8548794401255311
    ) < 1e-12

    assert abs(
        result.baseline_optimal_success
        - 0.32988188974988253
    ) < 1e-12
    assert abs(
        result.improved_optimal_success
        - 0.33252719682229603
    ) < 1e-12
    assert abs(
        result.hidden_state_oracle_success
        - 0.36909665108233747
    ) < 1e-12

    assert abs(result.gain - 0.0026453070724135236) < 1e-12
    assert abs(
        result.remaining_oracle_gap
        - 0.036569454260041456
    ) < 1e-12
    assert abs(
        result.recovered_oracle_gap_fraction
        - 0.0674569213870036
    ) < 1e-12

    print(
        "hosted Forest Seal observations: "
        f"{result.hosted_observation_count}/{result.observation_count}"
    )
    print(
        "hosted Forest Seal branch fraction: "
        f"{result.hosted_forest_fraction:.9%}"
    )
    print(
        "baseline success within hosted branch: "
        f"{result.hosted_forest_baseline_success:.9%}"
    )
    print(
        "overall optimal K0 success: "
        f"{result.baseline_optimal_success:.9%}"
    )
    print(
        "with legal Forest Seal pre-search: "
        f"{result.improved_optimal_success:.9%}"
    )
    print(
        "gain: "
        f"{result.gain * 100:.9f} percentage points"
    )
    print(
        "fraction of hidden-state oracle gap recovered: "
        f"{result.recovered_oracle_gap_fraction:.9%}"
    )


if __name__ == "__main__":
    main()
