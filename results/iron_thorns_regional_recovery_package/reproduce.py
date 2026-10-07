"""Reproduce the two-horizon Palace Belt + draw recovery package."""

from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.aichi_setup_inference import (
    KAZUMA_IRON_NONBASIC_COUNTS,
    KOHEI_IRON_NONBASIC_COUNTS,
)
from tools.iron_thorns_named_line_probability import (
    NamedLineCounts,
    exact_named_line_probability,
)
from tools.iron_thorns_regional_recovery_package import (
    RegionalRecoveryCounts,
    exact_regional_recovery_package,
)


def counts_from_list(nonbasic: dict[str, int]) -> RegionalRecoveryCounts:
    return RegionalRecoveryCounts(
        iron_thorns=60 - sum(nonbasic.values()),
        tag_call=nonbasic["Tag Call"],
        guzma_hala=nonbasic["Guzma & Hala"],
        thunder_mountain=nonbasic["Thunder Mountain ♢"],
        double_colorless=nonbasic["Double Colorless Energy"],
        palace_book=nonbasic.get("Palace Book", 0),
        palace_belt=nonbasic.get("Palace Belt", 0),
        players_ceremony=nonbasic.get("Player's Ceremony", 0),
        competing_active_tools=(
            nonbasic.get("Handheld Fan", 0)
            + nonbasic.get("Tool Jammer", 0)
        ),
    )


def main() -> None:
    cases = {
        "Kazuma": (
            KAZUMA_IRON_NONBASIC_COUNTS,
            0.22579832373984263,
            0.1272390658412493,
            0.07808612205675779,
            0.026050339113396406,
        ),
        "Kohei": (
            KOHEI_IRON_NONBASIC_COUNTS,
            0.33726034480531564,
            0.13537034018386437,
            0.0762904972758885,
            0.027816426032736957,
        ),
    }

    for label, (
        nonbasic,
        expected_belt,
        expected_dual,
        expected_fetch_both,
        expected_dual_competing,
    ) in cases.items():
        counts = counts_from_list(nonbasic)
        result = exact_regional_recovery_package(counts)

        baseline = exact_named_line_probability(
            NamedLineCounts(
                iron_thorns=counts.iron_thorns,
                tag_call=counts.tag_call,
                guzma_hala=counts.guzma_hala,
                thunder_mountain=counts.thunder_mountain,
                double_colorless=counts.double_colorless,
            )
        )
        assert result.accepted_opening_probability == baseline.accepted_opening_probability
        assert (
            result.named_success_probability
            == baseline.success_probability_given_accepted_opening
        )

        conditional = result.conditional_on_named_failure
        assert math.isclose(
            float(conditional(result.belt_ready_on_failure_probability)),
            expected_belt,
            abs_tol=1e-15,
        )
        assert math.isclose(
            float(conditional(result.dual_horizon_ready_probability)),
            expected_dual,
            abs_tol=1e-15,
        )
        assert math.isclose(
            float(conditional(result.gh_fetch_belt_and_ceremony_probability)),
            expected_fetch_both,
            abs_tol=1e-15,
        )
        assert math.isclose(
            float(
                conditional(
                    result.dual_horizon_with_competing_tool_in_hand_probability
                )
            ),
            expected_dual_competing,
            abs_tol=1e-15,
        )

        print(
            label,
            "Belt among failures",
            f"{float(conditional(result.belt_ready_on_failure_probability)):.9%}",
            "dual horizon",
            f"{float(conditional(result.dual_horizon_ready_probability)):.9%}",
            "G&H fetch both",
            f"{float(conditional(result.gh_fetch_belt_and_ceremony_probability)):.9%}",
            "dual + competing Tool in hand",
            f"{float(conditional(result.dual_horizon_with_competing_tool_in_hand_probability)):.9%}",
        )

    print("iron thorns regional recovery package: PASS")


if __name__ == "__main__":
    main()
