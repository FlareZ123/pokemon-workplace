from __future__ import annotations

from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.effect_evolution_timing import (
    build_profiles,
    is_direct_evolution_effect,
    summarize,
)

RESOURCES = ROOT / "resources"


def by_id(profiles, card_id: str):
    rows = [profile for profile in profiles if profile.card_id == card_id]
    assert len(rows) == 1, (card_id, rows)
    return rows[0]


def main() -> None:
    profiles = build_profiles(RESOURCES)
    summary = summarize(profiles)

    assert summary == {
        "print_level_profiles": 115,
        "unique_card_names": 53,
        "by_timing_policy": {
            "blocked": 30,
            "c12_default_permitted": 76,
            "explicit_permitted": 9,
        },
        "by_entry_turn_policy": {
            "blocked": 29,
            "c12_default_permitted": 76,
            "explicit_permitted": 10,
        },
        "by_source_channel": {
            "ability": 22,
            "attack": 61,
            "item": 20,
            "stadium": 1,
            "supporter": 11,
        },
        "by_structural_first_turn_window": {
            "both": 20,
            "none": 30,
            "second_only": 65,
        },
        "c12_default_unique_names": 41,
        "c12_default_both_order_names": [
            "Caterpie",
            "Clefable",
            "Duskull",
            "Eevee",
            "Inkay",
            "Karrablast",
            "Metapod",
            "Pidove",
            "Skiploom",
        ],
    }

    eevee = by_id(profiles, "sm1-101")
    assert eevee.source_name == "Energy Evolution"
    assert eevee.source_channel == "ability"
    assert eevee.timing_policy == "c12_default_permitted"
    assert eevee.entry_turn_policy == "c12_default_permitted"
    assert eevee.structural_first_turn_window == "both"

    salvatore = by_id(profiles, "sv5-160")
    assert salvatore.source_channel == "supporter"
    assert salvatore.timing_policy == "c12_default_permitted"
    assert salvatore.entry_turn_policy == "explicit_permitted"
    assert salvatore.structural_first_turn_window == "second_only"

    wally = by_id(profiles, "xy6-94")
    assert wally.source_channel == "supporter"
    assert wally.timing_policy == "explicit_permitted"
    assert wally.structural_first_turn_window == "second_only"

    boost_shake = by_id(profiles, "swsh7-142")
    assert boost_shake.source_channel == "item"
    assert boost_shake.timing_policy == "explicit_permitted"
    assert boost_shake.structural_first_turn_window == "both"

    exeggcute = by_id(profiles, "sv8-1")
    assert exeggcute.source_name == "Precocious Evolution"
    assert exeggcute.source_channel == "attack"
    assert exeggcute.timing_policy == "explicit_permitted"
    assert exeggcute.entry_turn_policy == "c12_default_permitted"
    assert exeggcute.structural_first_turn_window == "both"

    rare_candy = by_id(profiles, "sv1-191")
    assert rare_candy.source_channel == "item"
    assert rare_candy.timing_policy == "blocked"
    assert rare_candy.entry_turn_policy == "blocked"
    assert rare_candy.structural_first_turn_window == "none"

    grand_tree = by_id(profiles, "sv7-136")
    assert grand_tree.source_channel == "stadium"
    assert grand_tree.timing_policy == "blocked"
    assert grand_tree.entry_turn_policy == "blocked"
    assert grand_tree.structural_first_turn_window == "none"

    meganium = by_id(profiles, "sm8-8")
    assert meganium.source_name == "Quick-Ripening Herb"
    assert meganium.source_channel == "ability"
    assert meganium.timing_policy == "explicit_permitted"
    assert meganium.structural_first_turn_window == "both"

    phantump = by_id(profiles, "me4-38")
    assert phantump.source_name == "Spiteful Evolution"
    assert phantump.source_channel == "ability"
    assert phantump.timing_policy == "blocked"
    assert phantump.entry_turn_policy == "c12_default_permitted"
    assert phantump.structural_first_turn_window == "none"

    tm_evolution = by_id(profiles, "sv4-178")
    assert tm_evolution.source_channel == "attack"
    assert tm_evolution.timing_policy == "c12_default_permitted"
    assert tm_evolution.structural_first_turn_window == "second_only"

    ninjask_like = (
        "When you play this Pokémon from your hand to evolve 1 of your Pokémon during your turn, "
        "you may put Shedinja from your discard pile onto your Bench."
    )
    assert not is_direct_evolution_effect(ninjask_like)

    policy_counts = Counter(profile.timing_policy for profile in profiles)
    print("effect evolution timing regression passed")
    print(f"profiles={len(profiles)} unique_names={summary['unique_card_names']}")
    print(f"timing_policy={dict(sorted(policy_counts.items()))}")


if __name__ == "__main__":
    main()
