"""Reproduce attack-gate materialization for source-scoped restrictions."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from attack_source_scoped_restrictions import materialize_attack_restriction
from source_scoped_action_restrictions import CardActionAttempt, restriction_blocks_attempt
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
    attacks = [
        row for row in profiles
        if row.activation_family == "attack_applied"
    ]
    assert len(attacks) == 77

    unconditional = [
        row for row in attacks
        if row.application_gate == "unconditional"
    ]
    assert len(unconditional) == 71
    assert all(
        materialize_attack_restriction(row) == row.restriction
        for row in unconditional
    )

    heads_only = [
        row for row in attacks
        if row.application_gate == "coin_heads"
    ]
    assert len(heads_only) == 3
    assert all(
        materialize_attack_restriction(row, coin_heads=True)
        == row.restriction
        for row in heads_only
    )
    assert all(
        materialize_attack_restriction(row, coin_heads=False) is None
        for row in heads_only
    )

    chi_yu = _one(profiles, "me1-31", "Scorching Earth")
    assert materialize_attack_restriction(
        chi_yu,
        prerequisite_succeeded=False,
    ) is None
    assert materialize_attack_restriction(
        chi_yu,
        prerequisite_succeeded=True,
    ) == chi_yu.restriction

    crobat = _one(profiles, "sv4-112", "Echoing Madness")
    crobat_item = materialize_attack_restriction(
        crobat,
        selected_dimensions=frozenset({"item"}),
    )
    crobat_supporter = materialize_attack_restriction(
        crobat,
        selected_dimensions=frozenset({"supporter"}),
    )
    assert crobat_item is not None
    assert crobat_supporter is not None
    assert restriction_blocks_attempt(
        crobat_item,
        CardActionAttempt("item", "hand"),
    )
    assert not restriction_blocks_attempt(
        crobat_item,
        CardActionAttempt("supporter", "hand"),
    )
    assert restriction_blocks_attempt(
        crobat_supporter,
        CardActionAttempt("supporter", "hand"),
    )

    allergy = _one(profiles, "swsh11-3", "Allergy Storm")
    allergy_heads = materialize_attack_restriction(
        allergy,
        coin_heads=True,
    )
    allergy_tails = materialize_attack_restriction(
        allergy,
        coin_heads=False,
    )
    assert allergy_heads is not None
    assert allergy_tails is not None
    assert allergy_heads.dimensions == frozenset({"supporter"})
    assert allergy_tails.dimensions == frozenset({"item"})

    for row in (
        heads_only[0],
        chi_yu,
        crobat,
        allergy,
    ):
        try:
            materialize_attack_restriction(row)
        except ValueError:
            pass
        else:
            raise AssertionError("gated attack restriction accepted missing outcome")

    ability = _one(profiles, "xy7-3", "Irritating Pollen")
    try:
        materialize_attack_restriction(ability)
    except ValueError:
        pass
    else:
        raise AssertionError("continuous Ability entered attack materializer")

    print(
        json.dumps(
            {
                "attack_profiles": len(attacks),
                "unconditional_materialized": len(unconditional),
                "heads_only_profiles": len(heads_only),
                "failed_heads_create_no_restriction": True,
                "failed_prerequisite_creates_no_restriction": True,
                "player_choice_resolves_one_dimension": True,
                "allergy_heads_supporter_tails_item": True,
                "missing_gate_outcomes_rejected": True,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
