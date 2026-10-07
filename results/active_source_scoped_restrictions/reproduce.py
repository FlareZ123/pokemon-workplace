"""Reproduce aggregation of simultaneous continuous and temporal restrictions."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from active_source_scoped_restrictions import (
    ContinuousRestrictionSource,
    active_restrictions_for_player,
)
from attack_restriction_turn_windows import (
    begin_turn,
    create_attack_restriction_window,
)
from attack_source_scoped_restrictions import materialize_attack_restriction
from continuous_source_scoped_restrictions import ContinuousRestrictionContext
from source_scoped_action_restrictions import CardActionAttempt
from source_scoped_channel_projection import (
    action_allowed,
    project_source_scoped_permissions,
)
from source_scoped_restriction_activation import build_restriction_activation_profiles


def _one(profiles, card_id: str, needle: str):
    matches = [
        row
        for row in profiles
        if row.restriction.card_id == card_id
        and (
            needle in row.restriction.source
            or needle in row.restriction.text
        )
    ]
    assert len(matches) == 1, (card_id, needle, len(matches))
    return matches[0]


def main() -> None:
    profiles = build_restriction_activation_profiles(ROOT / "resources")

    vileplume = _one(profiles, "xy7-3", "Irritating Pollen")
    arbok = _one(profiles, "sv10-113", "Potent Glare")
    psyduck = _one(profiles, "sm9-26", "Headache")

    continuous = (
        ContinuousRestrictionSource(
            profile=vileplume,
            context=ContinuousRestrictionContext(
                source_in_play=True,
                ability_enabled=True,
                source_active=False,
            ),
            source_player="A",
            other_player="B",
        ),
        ContinuousRestrictionSource(
            profile=arbok,
            context=ContinuousRestrictionContext(
                source_in_play=True,
                ability_enabled=True,
                source_active=True,
            ),
            source_player="B",
            other_player="A",
        ),
    )

    psyduck_restriction = materialize_attack_restriction(
        psyduck,
        coin_heads=True,
    )
    assert psyduck_restriction is not None
    psyduck_window = create_attack_restriction_window(
        psyduck,
        psyduck_restriction,
        source_player="B",
        other_player="A",
    )
    psyduck_window = begin_turn(psyduck_window, "A")

    active_a = active_restrictions_for_player(
        "A",
        continuous_sources=continuous,
        attack_windows=(psyduck_window,),
    )
    assert len(active_a) == 3
    assert {row.card_id for row in active_a} == {
        "xy7-3",
        "sv10-113",
        "sm9-26",
    }

    projection_a = project_source_scoped_permissions(active_a)
    assert not action_allowed(
        projection_a,
        CardActionAttempt("item", "hand"),
    )
    assert not action_allowed(
        projection_a,
        CardActionAttempt("supporter", "hand"),
    )
    assert not action_allowed(
        projection_a,
        CardActionAttempt(
            "pokemon",
            "hand",
            card_tags=frozenset({"has_ability"}),
        ),
    )
    assert action_allowed(
        projection_a,
        CardActionAttempt("pokemon", "hand"),
    )

    active_b = active_restrictions_for_player(
        "B",
        continuous_sources=continuous,
        attack_windows=(psyduck_window,),
    )
    assert len(active_b) == 1
    assert active_b[0].card_id == "xy7-3"

    projection_b = project_source_scoped_permissions(active_b)
    assert not action_allowed(
        projection_b,
        CardActionAttempt("item", "hand"),
    )
    assert action_allowed(
        projection_b,
        CardActionAttempt("supporter", "hand"),
    )
    assert action_allowed(
        projection_b,
        CardActionAttempt(
            "pokemon",
            "hand",
            card_tags=frozenset({"has_ability"}),
        ),
    )

    suppressed_arbok = ContinuousRestrictionSource(
        profile=arbok,
        context=ContinuousRestrictionContext(
            source_in_play=True,
            ability_enabled=False,
            source_active=True,
        ),
        source_player="B",
        other_player="A",
    )
    active_a_suppressed = active_restrictions_for_player(
        "A",
        continuous_sources=(continuous[0], suppressed_arbok),
        attack_windows=(psyduck_window,),
    )
    assert {row.card_id for row in active_a_suppressed} == {
        "xy7-3",
        "sm9-26",
    }

    print(
        json.dumps(
            {
                "player_a_simultaneous_restrictions": len(active_a),
                "player_b_simultaneous_restrictions": len(active_b),
                "symmetric_self_lock_preserved": True,
                "opponent_continuous_scope_preserved": True,
                "temporal_attack_scope_preserved": True,
                "suppressed_continuous_source_removed": True,
                "combined_permission_projection_verified": True,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
