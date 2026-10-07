"""Reachability surface for multiple simultaneously matching type modifiers."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from pokemon_card_profile import build_pokemon_card_profile_index


def build_type_match_surface(resources_root: Path) -> dict[str, object]:
    profiles = tuple(build_pokemon_card_profile_index(resources_root).values())
    attacker_type_sets = tuple(
        sorted(
            {tuple(sorted(profile.types)) for profile in profiles},
            key=lambda row: (len(row), row),
        )
    )

    ambiguous_weakness = []
    ambiguous_resistance = []
    for target in profiles:
        for attacker_types in attacker_type_sets:
            attacker = set(attacker_types)
            weakness_matches = tuple(
                row.energy_type
                for row in target.weaknesses
                if row.energy_type in attacker
            )
            resistance_matches = tuple(
                row.energy_type
                for row in target.resistances
                if row.energy_type in attacker
            )
            if len(weakness_matches) > 1:
                ambiguous_weakness.append(
                    {
                        "target_id": target.print_id,
                        "target_name": target.name,
                        "attacker_types": attacker_types,
                        "matching_types": weakness_matches,
                    }
                )
            if len(resistance_matches) > 1:
                ambiguous_resistance.append(
                    {
                        "target_id": target.print_id,
                        "target_name": target.name,
                        "attacker_types": attacker_types,
                        "matching_types": resistance_matches,
                    }
                )

    type_counts = Counter(profile.types for profile in profiles)
    return {
        "profile_count": len(profiles),
        "distinct_attacker_type_sets": len(attacker_type_sets),
        "multi_type_profile_count": sum(
            count for types, count in type_counts.items() if len(types) > 1
        ),
        "multi_weakness_profile_count": sum(
            1 for profile in profiles if len(profile.weaknesses) > 1
        ),
        "multi_resistance_profile_count": sum(
            1 for profile in profiles if len(profile.resistances) > 1
        ),
        "ambiguous_weakness_cases": ambiguous_weakness,
        "ambiguous_resistance_cases": ambiguous_resistance,
    }
