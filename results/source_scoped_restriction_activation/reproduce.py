"""Reproduce activation and duration geometry for source-scoped restrictions."""

from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

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

    assert len(profiles) == 106
    activation = Counter(row.activation_family for row in profiles)
    duration = Counter(row.duration_family for row in profiles)
    gates = Counter(row.application_gate for row in profiles)

    assert activation == {
        "attack_applied": 77,
        "active_spot": 22,
        "in_play": 4,
        "relative_pokemon_count": 1,
        "tool_attached": 1,
        "stadium_required": 1,
    }
    assert duration == {
        "opponent_next_turn": 76,
        "continuous": 29,
        "until_end_of_own_next_turn": 1,
    }
    assert gates == {
        "unconditional": 71,
        "continuous_condition": 29,
        "coin_heads": 3,
        "stadium_discard_if_you_do": 1,
        "player_choice": 1,
        "coin_branch": 1,
    }

    attacks = [
        row for row in profiles
        if row.activation_family == "attack_applied"
    ]
    abilities = [
        row for row in profiles
        if row.duration_family == "continuous"
    ]
    assert all(not row.requires_source_in_play for row in attacks)
    assert all(not row.requires_ability_enabled for row in attacks)
    assert all(row.requires_source_in_play for row in abilities)
    assert all(row.requires_ability_enabled for row in abilities)

    vanilluxe = _one(profiles, "xy8-45", "Frigid Breath")
    assert vanilluxe.duration_family == "until_end_of_own_next_turn"
    assert vanilluxe.application_gate == "unconditional"

    crobat = _one(profiles, "sv4-112", "Echoing Madness")
    assert crobat.application_gate == "player_choice"
    assert crobat.restriction.exclusive_dimension_options

    allergy = _one(profiles, "swsh11-3", "Allergy Storm")
    assert allergy.application_gate == "coin_branch"
    assert allergy.restriction.exclusive_dimension_options

    chi_yu = _one(profiles, "me1-31", "Scorching Earth")
    assert chi_yu.application_gate == "stadium_discard_if_you_do"

    heads_only = {
        row.restriction.card_id
        for row in profiles
        if row.application_gate == "coin_heads"
    }
    assert heads_only == {"sm9-26", "sv1-87", "xy1-71"}

    vileplume = _one(profiles, "xy7-3", "Irritating Pollen")
    assert vileplume.activation_family == "in_play"

    arbok = _one(profiles, "sv10-113", "Potent Glare")
    assert arbok.activation_family == "active_spot"

    genesect = _one(profiles, "sv6pt5-40", "ACE Nullifier")
    assert genesect.activation_family == "tool_attached"

    barbaracle = _one(profiles, "xy10-23", "Hand Block")
    assert barbaracle.activation_family == "stadium_required"

    omastar = _one(profiles, "sm9-76", "Fossil Bind")
    assert omastar.activation_family == "relative_pokemon_count"

    print(
        json.dumps(
            {
                "restriction_profiles": len(profiles),
                "activation_family_counts": dict(activation),
                "duration_family_counts": dict(duration),
                "application_gate_counts": dict(gates),
                "attack_locks_survive_source_departure": True,
                "continuous_ability_locks_require_live_source": True,
                "vanilluxe_cross_turn_window_preserved": True,
                "exclusive_branch_gates_preserved": True,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
