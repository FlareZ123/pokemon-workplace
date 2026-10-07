"""Reproduce exact and residual PlayerChannels projection counts."""

from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from source_scoped_action_restrictions import (
    CardActionAttempt,
    build_source_scoped_action_restrictions,
    restriction_blocks_attempt,
)
from source_scoped_channel_projection import (
    action_allowed,
    channel_allows_hand_attempt,
    project_source_scoped_permissions,
    projection_reasons,
)


def _one(rows, card_id: str, needle: str):
    matches = [
        row
        for row in rows
        if row.card_id == card_id
        and (needle in row.source or needle in row.text)
    ]
    assert len(matches) == 1, (card_id, needle, len(matches))
    return matches[0]


def main() -> None:
    rows = build_source_scoped_action_restrictions(ROOT / "resources")
    projection = project_source_scoped_permissions(rows)

    assert len(rows) == 106
    assert len(projection.exact_restrictions) == 94
    assert len(projection.residual_restrictions) == 12

    reason_counts = Counter(
        reason
        for restriction in projection.residual_restrictions
        for reason in projection_reasons(restriction)
    )
    assert reason_counts == {
        "evolution": 6,
        "target_relation": 4,
        "ace_spec": 2,
        "ability_pokemon_play": 2,
        "energy_attach_to_target": 2,
        "card_exception": 1,
    }

    attempts = (
        CardActionAttempt("item", "hand"),
        CardActionAttempt(
            "item",
            "hand",
            card_tags=frozenset({"ace_spec"}),
        ),
        CardActionAttempt("tool", "hand", mode="attach"),
        CardActionAttempt("supporter", "hand"),
        CardActionAttempt("stadium", "hand"),
        CardActionAttempt("pokemon", "hand"),
        CardActionAttempt(
            "pokemon",
            "hand",
            card_tags=frozenset({"has_ability"}),
        ),
        CardActionAttempt("pokemon", "hand", mode="evolve"),
        CardActionAttempt("basic_energy", "hand", mode="attach"),
        CardActionAttempt("special_energy", "hand", mode="attach"),
    )

    for restriction in projection.exact_restrictions:
        one = project_source_scoped_permissions((restriction,))
        for attempt in attempts:
            exact_allowed = not restriction_blocks_attempt(
                restriction,
                attempt,
            )
            projected_allowed = channel_allows_hand_attempt(
                one.channels,
                attempt,
            )
            assert exact_allowed == projected_allowed, (
                restriction,
                attempt,
            )

    spiritomb = _one(rows, "bw11-87", "Sealing Scream")
    spiritomb_projection = project_source_scoped_permissions((spiritomb,))
    assert action_allowed(
        spiritomb_projection,
        CardActionAttempt("item", "hand"),
    )
    assert not action_allowed(
        spiritomb_projection,
        CardActionAttempt(
            "item",
            "hand",
            card_tags=frozenset({"ace_spec"}),
        ),
    )

    vileplume = _one(rows, "xy7-3", "Irritating Pollen")
    vileplume_projection = project_source_scoped_permissions((vileplume,))
    assert not action_allowed(
        vileplume_projection,
        CardActionAttempt("item", "hand"),
    )
    assert action_allowed(
        vileplume_projection,
        CardActionAttempt("item", "prize_pending"),
    )

    print(
        json.dumps(
            {
                "restrictions": len(rows),
                "exact_channel_projection": len(
                    projection.exact_restrictions
                ),
                "residual_typed_predicates": len(
                    projection.residual_restrictions
                ),
                "exact_projection_percent": (
                    100
                    * len(projection.exact_restrictions)
                    / len(rows)
                ),
                "residual_reason_counts": dict(reason_counts),
                "vileplume_prize_pending_item_allowed": True,
                "ace_spec_selector_preserved": True,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
