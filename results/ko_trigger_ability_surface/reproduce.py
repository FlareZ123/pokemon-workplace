"""Regression for the immediate Knock Out Ability trigger catalog."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from ko_trigger_ability_catalog import build


EXPECTED = {
    "matched_prints": 82,
    "matched_names": 50,
    "distinct_ability_signatures": 54,
    "prints_by_trigger_scope": {
        "allied": 11, "attached": 1, "opponent": 14, "self": 56,
    },
    "signatures_by_trigger_scope": {
        "allied": 5, "attached": 1, "opponent": 5, "self": 43,
    },
    "prints_by_effect_family": {
        "attacker_knockout": 7,
        "damage_counters": 9,
        "deck_mill": 4,
        "deck_search": 9,
        "energy_disruption": 2,
        "energy_relocation": 11,
        "hand_disruption": 3,
        "pokemon_zone_redirect": 7,
        "prize_modifier": 29,
        "promotion_control": 1,
        "special_condition": 1,
    },
    "signatures_by_effect_family": {
        "attacker_knockout": 5,
        "damage_counters": 8,
        "deck_mill": 3,
        "deck_search": 7,
        "energy_disruption": 1,
        "energy_relocation": 7,
        "hand_disruption": 3,
        "pokemon_zone_redirect": 5,
        "prize_modifier": 14,
        "promotion_control": 1,
        "special_condition": 1,
    },
    "unclassified_effect_prints": 0,
}


def main() -> None:
    catalog = build(ROOT / "resources")
    assert catalog["summary"] == EXPECTED
    rows = {row["card_id"]: row for row in catalog["rows"]}

    witnesses = {
        "me55-90": ("self", "attacker_knockout"),
        "sv10-55": ("allied", "energy_relocation"),
        "sm8-121": ("opponent", "pokemon_zone_redirect"),
        "sm8-95": ("attached", "prize_modifier"),
        "sm10-67": ("self", "deck_search"),
        "sm10-72": ("opponent", "promotion_control"),
        "bw8-39": ("self", "special_condition"),
    }
    for card_id, (scope, family) in witnesses.items():
        assert scope in rows[card_id]["trigger_scopes"]
        assert family in rows[card_id]["effect_families"]

    for card_id in ("bw11-80", "bw3-47", "me2pt5-142", "sm12-69"):
        assert card_id not in rows

    print("immediate KO Ability trigger surface regressions passed")


if __name__ == "__main__":
    main()
