"""Reproduce visible connector sequencing in Harto's Raichu branch."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from raichu_visible_connector_sequencing import (
    visible_connector_sequencing_snapshot,
)


def main() -> None:
    result = visible_connector_sequencing_snapshot()

    assert abs(result.observable_branch_mass - 0.03616755972964512) < 1e-9
    assert result.observation_count == 1331
    assert result.direct_observation_count == 847
    assert result.combined_observation_count == 957

    assert abs(result.direct_visible_fraction - 0.32562616136112005) < 1e-9
    assert abs(
        result.direct_visible_baseline_success
        - 0.5241349208739882
    ) < 1e-9

    assert abs(result.ultra_visible_fraction - 0.2532066840600113) < 1e-9
    assert abs(
        result.ultra_visible_baseline_success
        - 0.5132146342830301
    ) < 1e-9
    assert abs(
        result.computer_visible_fraction
        - 0.09070343609788564
    ) < 1e-9
    assert abs(
        result.computer_visible_baseline_success
        - 0.5434888956697607
    ) < 1e-9
    assert abs(
        result.direct_overlap_fraction
        - 0.01828395879677687
    ) < 1e-9

    assert abs(
        result.forest_visible_fraction
        - 0.018228341144079625
    ) < 1e-9
    assert abs(
        result.direct_forest_overlap_fraction
        - 0.004235153265076752
    ) < 1e-9
    assert abs(
        result.combined_visible_fraction
        - 0.33961934924012477
    ) < 1e-9
    assert abs(
        result.combined_visible_baseline_success
        - 0.5376556085196795
    ) < 1e-9

    assert abs(
        result.baseline_optimal_success
        - 0.32988188974988253
    ) < 1e-9
    assert abs(
        result.quick_ball_oracle_success
        - 0.36909665108233747
    ) < 1e-9
    assert abs(
        result.direct_policy_success
        - 0.4848360087914914
    ) < 1e-9
    assert abs(
        result.combined_policy_success
        - 0.48690299110925045
    ) < 1e-9
    assert abs(result.direct_gain - 0.15495411904160889) < 1e-9
    assert abs(result.combined_gain - 0.15702110135936792) < 1e-9
    assert abs(
        result.direct_over_quick_ball_oracle
        - 0.11573935770915393
    ) < 1e-9
    assert abs(
        result.combined_over_quick_ball_oracle
        - 0.11780634002691298
    ) < 1e-9

    print(
        "visible Ultra Ball / Computer Search observations: "
        f"{result.direct_observation_count}/{result.observation_count}"
    )
    print(
        "direct connector visible branch fraction: "
        f"{result.direct_visible_fraction:.9%}"
    )
    print(
        "baseline success in direct-visible subbranch: "
        f"{result.direct_visible_baseline_success:.9%}"
    )
    print(
        "overall baseline K0 success: "
        f"{result.baseline_optimal_success:.9%}"
    )
    print(
        "visible direct-connector-first policy: "
        f"{result.direct_policy_success:.9%}"
    )
    print(
        "combined direct/Forest policy: "
        f"{result.combined_policy_success:.9%}"
    )
    print(
        "Quick-Ball-first hidden-state oracle: "
        f"{result.quick_ball_oracle_success:.9%}"
    )
    print(
        "direct-first gain: "
        f"{result.direct_gain * 100:.9f} percentage points"
    )
    print(
        "combined gain: "
        f"{result.combined_gain * 100:.9f} percentage points"
    )


if __name__ == "__main__":
    main()
