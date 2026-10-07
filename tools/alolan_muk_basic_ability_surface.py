"""Audit legal Basic-Pokémon Abilities suppressed by Alolan Muk Power of Alchemy."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import re

from build_expanded_legality_baseline import classify_effective_legality, load_json
from card_search_target_index import BASIC_POKEMON, semantic_tags_for_card


HAND_BENCH_TRIGGER = "hand_bench_trigger"
ACTIVE = "active_required"
BENCH = "bench_required"
OFF_BOARD = "off_board_zone"
IN_PLAY = "in_play_or_unspecified"


@dataclass(frozen=True)
class BasicAbilityRow:
    card_id: str
    card_name: str
    ability_name: str
    ability_text: str
    geometry: str


def classify_basic_ability_geometry(text: str) -> str:
    normalized = " ".join(
        text.casefold().replace("pokémon", "pokemon").split()
    )

    if (
        "when you play this pokemon from your hand onto your bench"
        in normalized
        or "when you play this pokemon from your hand to your bench"
        in normalized
    ):
        return HAND_BENCH_TRIGGER

    if re.search(
        r"if this pokemon is in your (?:hand|discard pile|deck|prize cards)",
        normalized,
    ):
        return OFF_BOARD

    if re.search(
        r"(?:as long as|if) this pokemon is "
        r"(?:your active pokemon|in the active spot)",
        normalized,
    ):
        return ACTIVE

    if re.search(
        r"(?:as long as|if) this pokemon is on your bench",
        normalized,
    ):
        return BENCH

    return IN_PLAY


def build_basic_ability_surface(
    resources_root: Path = Path("resources"),
) -> tuple[BasicAbilityRow, ...]:
    sets = load_json(resources_root / "sets" / "en.json")
    expanded_sets = {
        row["id"]
        for row in sets
        if (row.get("legalities") or {}).get("expanded") == "Legal"
    }

    rows: list[BasicAbilityRow] = []
    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        if path.stem not in expanded_sets:
            continue
        for card in load_json(path):
            status, _source = classify_effective_legality(card)
            if status != "Legal" or card.get("supertype") != "Pokémon":
                continue
            if BASIC_POKEMON not in semantic_tags_for_card(card):
                continue

            for ability in card.get("abilities") or ():
                text = ability.get("text") or ""
                if not text:
                    continue
                rows.append(
                    BasicAbilityRow(
                        card_id=card["id"],
                        card_name=card["name"],
                        ability_name=ability.get("name") or "",
                        ability_text=text,
                        geometry=classify_basic_ability_geometry(text),
                    )
                )

    return tuple(
        sorted(
            rows,
            key=lambda row: (
                row.card_id,
                row.ability_name,
                row.ability_text,
            ),
        )
    )


def summarize_surface(
    rows: tuple[BasicAbilityRow, ...],
) -> dict[str, object]:
    return {
        "ability_rows": len(rows),
        "exact_prints": len({row.card_id for row in rows}),
        "unique_card_names": len({row.card_name for row in rows}),
        "geometry": dict(
            sorted(Counter(row.geometry for row in rows).items())
        ),
        "hand_bench_trigger_rows": sum(
            row.geometry == HAND_BENCH_TRIGGER for row in rows
        ),
        "hand_bench_trigger_names": len(
            {
                row.card_name
                for row in rows
                if row.geometry == HAND_BENCH_TRIGGER
            }
        ),
    }
