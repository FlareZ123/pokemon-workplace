"""Compile conservative target geometry for direct Pokemon zone-exit effects."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any

from pokemon_zone_exit_catalog import catalog_pokemon_zone_exits


@dataclass(frozen=True)
class ZoneExitTargetProfile:
    card_id: str
    name: str
    source_kind: str
    effect_name: str
    target_geometry: str
    pokemon_destination: str
    attachment_destination: str
    text: str


def _target_geometry(text: str, routing_text: str) -> str:
    lower = text.lower()
    routing_lower = routing_text.lower()

    if "each player's active pokémon" in routing_lower:
        return "both_active"

    if (
        "choose 1 of your opponent's benched pokémon" in lower
        and "shuffle this pokémon" in lower
        and lower.count("shuffle") >= 2
    ):
        return "opponent_bench_one_and_self"

    if (
        "all of your opponent's benched pokémon that you didn't choose"
        in routing_lower
    ):
        return "opponent_bench_all_except_one"

    if "all of their benched pokémon" in routing_lower:
        return "opponent_bench_all"

    if "any number of your pokémon in play" in routing_lower:
        return "own_any_number"

    if (
        "your opponent's active pokémon" in routing_lower
        or "their active pokémon" in routing_lower
    ):
        return "opponent_active"

    if (
        "choose 1 of your opponent's benched pokémon" in lower
        or re.search(
            r"(?:shuffle|put)\s+1 of your opponent's benched pokémon",
            routing_text,
            re.IGNORECASE,
        )
    ):
        return "opponent_bench_one"

    if (
        "choose 1 of your opponent's pokémon" in lower
        and "that pokémon" in routing_lower
    ):
        return "opponent_one"

    if re.search(
        r"(?:put|shuffle)\s+this pokémon",
        routing_text,
        re.IGNORECASE,
    ):
        return "self"

    if (
        re.search(
            r"(?:put|shuffle)\s+1 of your benched pokémon",
            routing_text,
            re.IGNORECASE,
        )
        or (
            "choose 1 of your benched combee" in lower
            and "that pokémon" in routing_lower
        )
    ):
        return "own_bench_one"

    if re.search(
        r"(?:put|shuffle)\s+1 of your [^.]{0,80}pokémon",
        routing_text,
        re.IGNORECASE,
    ):
        return "own_one"

    if re.search(
        r"put 1 pokémon into your hand",
        routing_text,
        re.IGNORECASE,
    ):
        return "unqualified_one_to_your_hand"

    raise ValueError(
        "Unclassified direct zone-exit target geometry: "
        f"text={text!r}, routing_text={routing_text!r}"
    )


def compile_zone_exit_target_profiles(
    resources_root: Path = Path("resources"),
) -> dict[str, Any]:
    catalog = catalog_pokemon_zone_exits(resources_root)
    profiles: list[ZoneExitTargetProfile] = []

    for row in catalog["rows"]:
        if row["timing_class"] != "direct_effect":
            continue
        profiles.append(
            ZoneExitTargetProfile(
                card_id=row["id"],
                name=row["name"],
                source_kind=row["source_kind"],
                effect_name=row["effect_name"],
                target_geometry=_target_geometry(
                    row["text"],
                    row["routing_text"],
                ),
                pokemon_destination=row["pokemon_destination"],
                attachment_destination=row["attachment_destination"],
                text=row["text"],
            )
        )

    print_counts = Counter(
        profile.target_geometry
        for profile in profiles
    )
    unique_names: dict[str, set[str]] = {}
    for profile in profiles:
        unique_names.setdefault(
            profile.target_geometry,
            set(),
        ).add(profile.name)

    return {
        "summary": {
            "profiles": len(profiles),
            "unique_names": len(
                {profile.name for profile in profiles}
            ),
            "geometry_print_counts": dict(
                sorted(print_counts.items())
            ),
            "geometry_unique_name_counts": {
                geometry: len(names)
                for geometry, names in sorted(
                    unique_names.items()
                )
            },
        },
        "profiles": tuple(profiles),
    }
