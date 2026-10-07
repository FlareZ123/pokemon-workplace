"""Reproduce continuous source-scoped Ability restriction evaluation."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from continuous_source_scoped_restrictions import (
    ContinuousRestrictionContext,
    continuous_restriction_active,
)
from source_scoped_restriction_activation import (
    build_restriction_activation_profiles,
)


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
    continuous = [
        row for row in profiles
        if row.duration_family == "continuous"
    ]
    assert len(continuous) == 29

    disabled = ContinuousRestrictionContext(
        source_in_play=True,
        ability_enabled=False,
        source_active=True,
        tool_attached=True,
        stadium_in_play=True,
        player_pokemon_in_play=1,
        opponent_pokemon_in_play=6,
    )
    absent = ContinuousRestrictionContext(
        source_in_play=False,
        ability_enabled=True,
        source_active=True,
        tool_attached=True,
        stadium_in_play=True,
        player_pokemon_in_play=1,
        opponent_pokemon_in_play=6,
    )
    assert all(
        not continuous_restriction_active(row, disabled)
        for row in continuous
    )
    assert all(
        not continuous_restriction_active(row, absent)
        for row in continuous
    )

    vileplume = _one(profiles, "xy7-3", "Irritating Pollen")
    assert continuous_restriction_active(
        vileplume,
        ContinuousRestrictionContext(
            source_in_play=True,
            ability_enabled=True,
            source_active=False,
        ),
    )

    arbok = _one(profiles, "sv10-113", "Potent Glare")
    assert not continuous_restriction_active(
        arbok,
        ContinuousRestrictionContext(
            source_in_play=True,
            ability_enabled=True,
            source_active=False,
        ),
    )
    assert continuous_restriction_active(
        arbok,
        ContinuousRestrictionContext(
            source_in_play=True,
            ability_enabled=True,
            source_active=True,
        ),
    )

    genesect = _one(profiles, "sv6pt5-40", "ACE Nullifier")
    assert not continuous_restriction_active(
        genesect,
        ContinuousRestrictionContext(
            source_in_play=True,
            ability_enabled=True,
            tool_attached=False,
        ),
    )
    assert continuous_restriction_active(
        genesect,
        ContinuousRestrictionContext(
            source_in_play=True,
            ability_enabled=True,
            tool_attached=True,
        ),
    )

    barbaracle = _one(profiles, "xy10-23", "Hand Block")
    assert not continuous_restriction_active(
        barbaracle,
        ContinuousRestrictionContext(
            source_in_play=True,
            ability_enabled=True,
            stadium_in_play=False,
        ),
    )
    assert continuous_restriction_active(
        barbaracle,
        ContinuousRestrictionContext(
            source_in_play=True,
            ability_enabled=True,
            stadium_in_play=True,
        ),
    )

    omastar = _one(profiles, "sm9-76", "Fossil Bind")
    assert continuous_restriction_active(
        omastar,
        ContinuousRestrictionContext(
            source_in_play=True,
            ability_enabled=True,
            player_pokemon_in_play=3,
            opponent_pokemon_in_play=4,
        ),
    )
    assert not continuous_restriction_active(
        omastar,
        ContinuousRestrictionContext(
            source_in_play=True,
            ability_enabled=True,
            player_pokemon_in_play=4,
            opponent_pokemon_in_play=4,
        ),
    )

    attack = _one(profiles, "sm9-26", "Headache")
    try:
        continuous_restriction_active(
            attack,
            ContinuousRestrictionContext(
                source_in_play=True,
                ability_enabled=True,
            ),
        )
    except ValueError:
        pass
    else:
        raise AssertionError("attack-applied restriction entered continuous evaluator")

    print(
        json.dumps(
            {
                "continuous_profiles": len(continuous),
                "suppressed_ability_disables_all_continuous_profiles": True,
                "absent_source_disables_all_continuous_profiles": True,
                "bench_vileplume_active": True,
                "arbok_requires_active_spot": True,
                "genesect_requires_tool": True,
                "barbaracle_requires_stadium": True,
                "omastar_requires_relative_pokemon_count": True,
                "attack_profiles_rejected": True,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
