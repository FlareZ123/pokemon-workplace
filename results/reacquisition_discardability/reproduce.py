"""Reproduce payload discardability created by same-line reacquisition."""

from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from temporal_resource_ledger import TemporalAction, minimum_initial_filler


def compact_discards(witness):
    return [
        {
            "action": action.action,
            "discarded": [
                {"card": card, "origin": origin, "count": count}
                for card, origin, count in action.discarded
            ],
        }
        for action in witness.actions
    ]


def structural_gate_probe(trials: int = 200_000, seed: int = 20261007):
    deck_counts = {
        "Pidgey": 2,
        "Pidgeotto": 2,
        "Pidgeot ex": 2,
        "Oddish": 2,
        "Gloom": 2,
        "Vileplume": 2,
        "Vileplume-GX": 1,
        "Lillipup": 2,
        "Herdier": 2,
        "Stoutland": 1,
        "Bunnelby": 2,
        "Fan Rotom": 1,
        "Relicanth": 1,
        "Mr. Mime": 1,
        "Girafarig": 1,
        "Budew": 1,
        "Jirachi": 1,
        "Guzma & Hala": 4,
        "Guzma": 2,
        "Cassius": 1,
        "Karen": 1,
        "Plumeria": 1,
        "Gladion": 1,
        "Faba": 1,
        "Lusamine": 1,
        "Bellelba & Brycen-Man": 1,
        "Peonia": 1,
        "Team Yell's Cheer": 1,
        "Tag Call": 4,
        "Stealthy Hood": 3,
        "Technical Machine: Evolution": 2,
        "Counter Gain": 1,
        "Artazon": 2,
        "Secret Box": 1,
        "Capture Energy": 2,
        "Jet Energy": 2,
        "Memory Energy": 1,
        "Grass Energy": 1,
    }
    basics = {
        "Pidgey",
        "Oddish",
        "Lillipup",
        "Bunnelby",
        "Fan Rotom",
        "Relicanth",
        "Mr. Mime",
        "Girafarig",
        "Budew",
        "Jirachi",
    }
    deck = tuple(card for card, copies in deck_counts.items() for _ in range(copies))
    assert len(deck) == 60

    rng = random.Random(seed)
    counts = Counter()
    for _ in range(trials):
        while True:
            order = rng.sample(range(60), 60)
            opening = [deck[index] for index in order[:7]]
            if any(card in basics for card in opening):
                break

        prizes = [deck[index] for index in order[7:13]]
        draw = deck[order[13]]
        top_five = [deck[index] for index in order[14:19]]
        opening_basics = [card for card in opening if card in basics]
        if "Jirachi" in opening_basics:
            active = "Jirachi"
        else:
            non_bunnelby = [card for card in opening_basics if card != "Bunnelby"]
            active = non_bunnelby[0] if non_bunnelby else "Bunnelby"

        hand = Counter(opening + [draw])
        hand[active] -= 1
        if hand[active] == 0:
            del hand[active]

        remaining = Counter(deck)
        for card in opening + prizes + [draw]:
            remaining[card] -= 1

        box_in_hand = hand["Secret Box"] > 0
        box_stellar = (
            not box_in_hand
            and active == "Jirachi"
            and "Secret Box" in top_five
        )
        if not (box_in_hand or box_stellar):
            continue

        counts["accessible"] += 1
        tm_double = remaining["Technical Machine: Evolution"] == 2
        artazon_double = remaining["Artazon"] == 2
        counts["tm_double"] += int(tm_double)
        counts["artazon_double"] += int(artazon_double)
        counts["either_double"] += int(tm_double or artazon_double)
        counts["both_double"] += int(tm_double and artazon_double)
        counts["neither_double"] += int(not tm_double and not artazon_double)

    return counts


def main() -> None:
    secret_box = TemporalAction(
        "Secret Box",
        consumes=("Secret Box",),
        discard_cost=3,
        generates=(
            "Guzma & Hala",
            "Tag Call",
            "Technical Machine: Evolution",
            "Artazon",
        ),
    )
    gnh_without_reacquisition = TemporalAction(
        "Guzma & Hala",
        consumes=("Guzma & Hala",),
        discard_cost=2,
        generates=("Jet Energy",),
    )
    gnh_tool_reacquisition = TemporalAction(
        "Guzma & Hala",
        consumes=("Guzma & Hala",),
        discard_cost=2,
        generates=("Technical Machine: Evolution", "Jet Energy"),
    )
    gnh_stadium_reacquisition = TemporalAction(
        "Guzma & Hala",
        consumes=("Guzma & Hala",),
        discard_cost=2,
        generates=("Artazon", "Jet Energy"),
    )
    gnh_full_reacquisition = TemporalAction(
        "Guzma & Hala",
        consumes=("Guzma & Hala",),
        discard_cost=2,
        generates=(
            "Technical Machine: Evolution",
            "Artazon",
            "Jet Energy",
        ),
    )
    requirement_profiles = {
        "aichi_core": {
            "Technical Machine: Evolution": 1,
            "Artazon": 1,
            "Jet Energy": 1,
        },
        "item_also_independent": {
            "Tag Call": 1,
            "Technical Machine: Evolution": 1,
            "Artazon": 1,
            "Jet Energy": 1,
        },
    }

    second_actions = (
        ("no_reacquisition", gnh_without_reacquisition),
        ("tool_reacquisition", gnh_tool_reacquisition),
        ("stadium_reacquisition", gnh_stadium_reacquisition),
        ("tool_and_stadium_reacquisition", gnh_full_reacquisition),
    )
    profiles = {}
    for profile_name, requirements in requirement_profiles.items():
        scenarios = {}
        for name, second_action in second_actions:
            fillers, witness = minimum_initial_filler(
                ("Secret Box",),
                (secret_box, second_action),
                final_hand_requirements=requirements,
                max_fillers=6,
            )
            scenarios[name] = {
                "minimum_initial_filler": fillers,
                "initial_discards": witness.initial_discards,
                "total_discards": witness.total_discards,
                "discard_witness": compact_discards(witness),
            }
        profiles[profile_name] = scenarios

    expected = {
        "aichi_core": {
            "no_reacquisition": 4,
            "tool_reacquisition": 3,
            "stadium_reacquisition": 3,
            "tool_and_stadium_reacquisition": 3,
        },
        "item_also_independent": {
            "no_reacquisition": 5,
            "tool_reacquisition": 4,
            "stadium_reacquisition": 4,
            "tool_and_stadium_reacquisition": 3,
        },
    }
    for profile_name, scenarios in profiles.items():
        for scenario_name, scenario in scenarios.items():
            assert (
                scenario["minimum_initial_filler"]
                == expected[profile_name][scenario_name]
            )
            assert scenario["total_discards"] == 5

    counts = structural_gate_probe()
    assert counts == Counter(
        {
            "accessible": 27552,
            "either_double": 23665,
            "tm_double": 16874,
            "artazon_double": 16873,
            "both_double": 10082,
            "neither_double": 3887,
        }
    )

    accessible = counts["accessible"]
    output = {
        "deterministic_ledger": profiles,
        "aichi_raw_secret_box_access_probe": {
            "trials": 200_000,
            "seed": 20261007,
            "accessible_states": accessible,
            "either_tm_or_artazon_has_both_copies_remaining": counts["either_double"],
            "either_rate_given_access": counts["either_double"] / accessible,
            "both_have_both_copies_remaining": counts["both_double"],
            "both_rate_given_access": counts["both_double"] / accessible,
            "neither_has_both_copies_remaining": counts["neither_double"],
            "neither_rate_given_access": counts["neither_double"] / accessible,
        },
    }
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
