"""Reproduce region-only continuation inside Iron Thorns named-line failures."""

from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.aichi_setup_inference import (
    KAZUMA_IRON_NONBASIC_COUNTS,
    KOHEI_IRON_NONBASIC_COUNTS,
    RYOYA_IRON_NONBASIC_COUNTS,
)
from tools.iron_thorns_named_line_probability import (
    NamedLineCounts,
    exact_named_line_probability,
)
from tools.iron_thorns_regional_failure_continuation import (
    RegionalContinuationCounts,
    exact_regional_failure_continuation,
)


def regional_counts(nonbasic: dict[str, int]) -> RegionalContinuationCounts:
    return RegionalContinuationCounts(
        iron_thorns=60 - sum(nonbasic.values()),
        tag_call=nonbasic["Tag Call"],
        guzma_hala=nonbasic["Guzma & Hala"],
        thunder_mountain=nonbasic["Thunder Mountain ♢"],
        double_colorless=nonbasic["Double Colorless Energy"],
        palace_book=nonbasic.get("Palace Book", 0),
        players_ceremony=nonbasic.get("Player's Ceremony", 0),
    )


def main() -> None:
    cases = {
        "Kazuma": (
            KAZUMA_IRON_NONBASIC_COUNTS,
            0.32848860519072587,
            0.05751596817074185,
        ),
        "Ryoya": (
            RYOYA_IRON_NONBASIC_COUNTS,
            0.4792753335782402,
            0.026049835385765382,
        ),
        "Kohei": (
            KOHEI_IRON_NONBASIC_COUNTS,
            0.22579832373984263,
            0.0647820589930367,
        ),
    }

    for label, (nonbasic, expected_failure_fallback, expected_search_pivot) in cases.items():
        counts = regional_counts(nonbasic)
        result = exact_regional_failure_continuation(counts)

        baseline = exact_named_line_probability(
            NamedLineCounts(
                iron_thorns=counts.iron_thorns,
                tag_call=counts.tag_call,
                guzma_hala=counts.guzma_hala,
                thunder_mountain=counts.thunder_mountain,
                double_colorless=counts.double_colorless,
            )
        )

        # Adding regional-card categories must refine the same physical state
        # space without changing the original narrow attack-line probability.
        assert result.accepted_opening_probability == baseline.accepted_opening_probability
        assert (
            result.named_success_probability
            == baseline.success_probability_given_accepted_opening
        )
        assert (
            result.resource_unavailable_failure_probability
            == baseline.unavailable_resource_probability
        )
        assert (
            result.connector_failure_probability
            == baseline.connector_access_failure_probability
        )

        assert math.isclose(
            float(result.regional_draw_given_named_failure),
            expected_failure_fallback,
            abs_tol=1e-15,
        )
        assert math.isclose(
            float(result.failure_ceremony_search_witness_probability),
            expected_search_pivot,
            abs_tol=1e-15,
        )

        print(
            label,
            "named success",
            f"{float(result.named_success_probability):.9%}",
            "regional draw among failures",
            f"{float(result.regional_draw_given_named_failure):.9%}",
            "G&H -> Ceremony failure pivot",
            f"{float(result.failure_ceremony_search_witness_probability):.9%}",
        )

    print("iron thorns regional failure continuation: PASS")


if __name__ == "__main__":
    main()
