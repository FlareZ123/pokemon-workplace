"""Reproduce the source-scoped direct action-restriction audit."""

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
    resources = ROOT / "resources"
    rows = build_source_scoped_action_restrictions(resources)

    assert len(rows) == 106
    assert len({row.card_name for row in rows}) == 63
    assert Counter(row.source.split(":", 1)[0] for row in rows) == {
        "attack": 77,
        "ability": 29,
    }
    assert Counter(row.target_scope for row in rows) == {
        "opponent": 101,
        "both": 5,
    }
    assert Counter(row.required_target_relation for row in rows) == {
        None: 102,
        "defending_pokemon": 4,
    }
    assert Counter(
        dimension
        for row in rows
        for dimension in row.dimensions
    ) == {
        "item": 42,
        "stadium": 22,
        "special_energy_play": 20,
        "tool": 13,
        "supporter": 10,
        "all_cards_from_hand": 7,
        "evolution": 6,
        "trainer": 5,
        "special_energy_attach": 2,
        "ace_spec": 2,
        "ability_pokemon_play": 2,
        "energy_attach_to_target": 2,
        "tool_attach": 1,
    }
    assert {row.prohibited_source_zone for row in rows} == {"hand"}

    vileplume = _one(rows, "xy7-3", "Irritating Pollen")
    assert restriction_blocks_attempt(
        vileplume,
        CardActionAttempt("item", "hand"),
    )
    assert not restriction_blocks_attempt(
        vileplume,
        CardActionAttempt("item", "prize_pending"),
    )

    dark_moon = _one(rows, "sm11-125", "Dark Moon-GX")
    assert restriction_blocks_attempt(
        dark_moon,
        CardActionAttempt("tool", "hand", mode="attach"),
    )
    assert not restriction_blocks_attempt(
        dark_moon,
        CardActionAttempt("pokemon", "hand"),
    )

    horror_house = _one(rows, "sm9-53", "Horror House-GX")
    assert restriction_blocks_attempt(
        horror_house,
        CardActionAttempt("basic_energy", "hand", mode="attach"),
    )
    assert not restriction_blocks_attempt(
        horror_house,
        CardActionAttempt("basic_energy", "discard", mode="attach"),
    )

    spiritomb = _one(rows, "bw11-87", "Sealing Scream")
    assert restriction_blocks_attempt(
        spiritomb,
        CardActionAttempt(
            "item",
            "hand",
            card_tags=frozenset({"ace_spec"}),
        ),
    )
    assert not restriction_blocks_attempt(
        spiritomb,
        CardActionAttempt("item", "hand"),
    )

    arbok = _one(rows, "sv10-113", "Potent Glare")
    assert restriction_blocks_attempt(
        arbok,
        CardActionAttempt(
            "pokemon",
            "hand",
            card_tags=frozenset({"has_ability"}),
        ),
    )
    assert not restriction_blocks_attempt(
        arbok,
        CardActionAttempt(
            "pokemon",
            "hand",
            card_tags=frozenset({"has_ability", "team_rocket"}),
        ),
    )
    assert not restriction_blocks_attempt(
        arbok,
        CardActionAttempt("pokemon", "hand"),
    )

    time_freeze = _one(rows, "xyp-XY77", "Time Freeze")
    assert restriction_blocks_attempt(
        time_freeze,
        CardActionAttempt(
            "pokemon",
            "hand",
            mode="evolve",
            target_relation="defending_pokemon",
        ),
    )
    assert not restriction_blocks_attempt(
        time_freeze,
        CardActionAttempt(
            "pokemon",
            "hand",
            mode="evolve",
            target_relation="other",
        ),
    )

    cross_slicer = _one(rows, "xyp-XY75", "Cross Slicer")
    assert restriction_blocks_attempt(
        cross_slicer,
        CardActionAttempt(
            "basic_energy",
            "hand",
            mode="attach",
            target_relation="defending_pokemon",
        ),
    )
    assert not restriction_blocks_attempt(
        cross_slicer,
        CardActionAttempt(
            "basic_energy",
            "hand",
            mode="attach",
            target_relation="other",
        ),
    )
    assert not restriction_blocks_attempt(
        cross_slicer,
        CardActionAttempt(
            "basic_energy",
            "discard",
            mode="attach",
            target_relation="defending_pokemon",
        ),
    )

    goodra = _one(rows, "xy4-77", "Slip Trip")
    assert restriction_blocks_attempt(
        goodra,
        CardActionAttempt("tool", "hand", mode="attach"),
    )

    barbaracle = _one(rows, "xy10-23", "Hand Block")
    assert restriction_blocks_attempt(
        barbaracle,
        CardActionAttempt("special_energy", "hand", mode="attach"),
    )
    assert not restriction_blocks_attempt(
        barbaracle,
        CardActionAttempt("basic_energy", "hand", mode="attach"),
    )

    print(
        json.dumps(
            {
                "print_level_restrictions": len(rows),
                "unique_card_names": len({row.card_name for row in rows}),
                "attack_rows": 77,
                "ability_rows": 29,
                "source_zones": ["hand"],
                "vileplume_hand_item_blocked": True,
                "vileplume_prize_item_blocked": False,
                "all_card_lock_blocks_hand_energy": True,
                "team_rocket_exception_preserved": True,
                "target_specific_restrictions_preserved": True,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
