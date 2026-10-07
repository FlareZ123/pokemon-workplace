from __future__ import annotations

import json
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
from tools.iron_thorns_speed_recovery_line import (
    SpeedRecoveryCounts,
    exact_speed_recovery_line,
)


def load_card(set_id: str, card_id: str) -> dict:
    cards = json.loads(
        (ROOT / "resources" / "cards" / "en" / f"{set_id}.json").read_text(
            encoding="utf-8"
        )
    )
    return next(card for card in cards if card["id"] == card_id)


def counts_from_list(nonbasic: dict[str, int]) -> SpeedRecoveryCounts:
    return SpeedRecoveryCounts(
        iron_thorns=60 - sum(nonbasic.values()),
        tag_call=nonbasic["Tag Call"],
        guzma_hala=nonbasic["Guzma & Hala"],
        thunder_mountain=nonbasic["Thunder Mountain ♢"],
        double_colorless=nonbasic["Double Colorless Energy"],
        palace_belt=nonbasic.get("Palace Belt", 0),
        players_ceremony=nonbasic.get("Player's Ceremony", 0),
        speed_lightning=nonbasic["Speed Lightning Energy"],
    )


def main() -> None:
    speed = load_card("swsh2", "swsh2-173")
    assert speed["name"] == "Speed Lightning Energy"
    assert speed["subtypes"] == ["Special"]
    assert any("draw 2 cards" in rule for rule in speed["rules"])

    iron = load_card("sv6", "sv6-77")
    assert iron["name"] == "Iron Thorns ex"
    assert iron["types"] == ["Lightning"]

    cases = {
        "Kazuma": (
            KAZUMA_IRON_NONBASIC_COUNTS,
            0.10576296529661973,
            0.09722143028912793,
            0.04732013643754275,
        ),
        "Kohei": (
            KOHEI_IRON_NONBASIC_COUNTS,
            0.119124151674923,
            0.10272280267397117,
            0.045742208742508464,
        ),
    }

    for label, (nonbasic, expected_package, expected_paid, expected_fetch_all) in cases.items():
        counts = counts_from_list(nonbasic)
        result = exact_speed_recovery_line(counts)
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
        assert result.named_success_probability == baseline.success_probability_given_accepted_opening

        conditional = result.conditional_on_named_failure
        assert math.isclose(
            float(conditional(result.package_ready_on_failure_probability)),
            expected_package,
            abs_tol=1e-15,
        )
        assert math.isclose(
            float(conditional(result.package_requiring_paid_gh_probability)),
            expected_paid,
            abs_tol=1e-15,
        )
        assert math.isclose(
            float(conditional(result.gh_fetch_all_three_probability)),
            expected_fetch_all,
            abs_tol=1e-15,
        )

        print(
            label,
            f"package={float(conditional(result.package_ready_on_failure_probability)):.9%}",
            f"paid={float(conditional(result.package_requiring_paid_gh_probability)):.9%}",
            f"fetch_all={float(conditional(result.gh_fetch_all_three_probability)):.9%}",
        )

    print("iron thorns Speed Lightning recovery line: PASS")


if __name__ == "__main__":
    main()
