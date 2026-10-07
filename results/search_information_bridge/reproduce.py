from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.prize_belief_kernel import PrizeBelief
from tools.prize_information_value import Line
from tools.search_action_legality import (
    SearchState,
    constrained_search_to_bench,
    constrained_search_to_hand,
)
from tools.search_information_bridge import (
    precommitment_information_value_if_observed,
    project_search_information,
)


def main() -> None:
    prior = PrizeBelief.from_hypergeometric(
        {"A": 1, "B": 1},
        pool_size=53,
        prize_count=6,
    )
    assert not prior.is_exact()
    assert prior.entropy_bits() > 0.0

    targetless = constrained_search_to_hand(
        SearchState(deck_cards=40, eligible_targets=0),
        action_class="item",
    )
    projected = project_search_information(
        targetless,
        prior,
        {"A": 0, "B": 1},
        material_action_available=False,
    )
    assert projected.observation_applied
    assert not projected.material_action_available
    assert projected.posterior_belief.is_exact()
    assert projected.posterior_belief.entropy_bits() == 0.0

    blocked = constrained_search_to_bench(
        SearchState(deck_cards=40, eligible_targets=1, bench_slots=0),
        action_class="item",
    )
    blocked_projection = project_search_information(
        blocked,
        prior,
        {"A": 0, "B": 1},
        material_action_available=False,
    )
    assert not blocked_projection.observation_applied
    assert blocked_projection.posterior_belief == prior

    material_search = constrained_search_to_hand(
        SearchState(deck_cards=40, eligible_targets=1),
        action_class="item",
    )
    material_projection = project_search_information(
        material_search,
        prior,
        {"A": 0, "B": 1},
        material_action_available=True,
    )
    assert material_projection.observation_applied
    assert material_projection.material_action_available

    lines = (
        Line("A-line", (("A", 1),)),
        Line("B-line", (("B", 1),)),
    )
    targetless_vpi = precommitment_information_value_if_observed(
        targetless,
        {"A": 1, "B": 1},
        lines,
    )
    blocked_vpi = precommitment_information_value_if_observed(
        blocked,
        {"A": 1, "B": 1},
        lines,
    )
    assert math.isclose(targetless_vpi, 0.10232220609579101, rel_tol=0.0, abs_tol=1e-12)
    assert blocked_vpi == 0.0

    print(json.dumps({
        "targetless_search": {
            "material_action_available": projected.material_action_available,
            "observation_applied": projected.observation_applied,
            "prior_entropy_bits": prior.entropy_bits(),
            "posterior_entropy_bits": projected.posterior_belief.entropy_bits(),
            "precommitment_information_value": targetless_vpi,
        },
        "blocked_search": {
            "observation_applied": blocked_projection.observation_applied,
            "precommitment_information_value": blocked_vpi,
        },
        "material_search": {
            "material_action_available": material_projection.material_action_available,
            "observation_applied": material_projection.observation_applied,
        },
    }, indent=2))


if __name__ == "__main__":
    main()
