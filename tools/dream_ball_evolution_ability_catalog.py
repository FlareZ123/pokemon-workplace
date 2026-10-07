"""Catalog Evolution-Pokemon Abilities exposed by Dream Ball direct entry.

Dream Ball can put any Pokemon from deck onto the Bench. For Evolution Pokemon,
that bypasses the ordinary evolution stack. This catalog conservatively
classifies whether an Ability's own location/entry wording is compatible with
that direct Bench entry. Compatibility is not a claim that every remaining
condition of the Ability is satisfied.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import re

from build_expanded_legality_baseline import classify_effective_legality, load_json
from card_search_target_index import semantic_tags_for_card
from typed_search_target_allocator import EVOLUTION_POKEMON


GEOMETRY_IN_PLAY = "in_play"
GEOMETRY_BENCH = "bench_required"
GEOMETRY_ACTIVE = "active_required"
GEOMETRY_HAND_EVOLVE_TRIGGER = "hand_evolution_trigger"
GEOMETRY_HAND_BENCH_TRIGGER = "hand_bench_trigger"
GEOMETRY_OFF_BOARD = "off_board_zone"

ACTIVATION_TURN_ACTION = "turn_action"
ACTIVATION_TRIGGERED = "triggered"
ACTIVATION_PASSIVE = "passive_or_continuous"


@dataclass(frozen=True)
class EvolutionAbilityCandidate:
    card_id: str
    card_name: str
    subtypes: tuple[str, ...]
    evolves_from: str | None
    ability_name: str
    ability_text: str
    geometry: str
    activation: str

    @property
    def dream_ball_geometry_compatible(self) -> bool:
        return self.geometry in {GEOMETRY_IN_PLAY, GEOMETRY_BENCH}


def _normalized(text: str) -> str:
    return " ".join(
        text.casefold().replace("pokémon", "pokemon").split()
    )


def classify_ability_geometry(text: str) -> str:
    """Classify only explicit source/location constraints in Ability text."""

    normalized = _normalized(text)

    if (
        "when you play this pokemon from your hand to evolve" in normalized
        or re.search(
            r"when you evolve .* by playing this card from your hand",
            normalized,
        )
    ):
        return GEOMETRY_HAND_EVOLVE_TRIGGER

    if (
        "when you play this pokemon from your hand onto your bench"
        in normalized
        or "when you play this pokemon from your hand to your bench"
        in normalized
    ):
        return GEOMETRY_HAND_BENCH_TRIGGER

    if re.search(
        r"if this pokemon is in your (?:hand|discard pile|deck|prize cards)",
        normalized,
    ):
        return GEOMETRY_OFF_BOARD

    if re.search(
        r"(?:as long as|if) this pokemon is "
        r"(?:your active pokemon|in the active spot)",
        normalized,
    ):
        return GEOMETRY_ACTIVE

    if re.search(
        r"(?:as long as|if) this pokemon is on your bench",
        normalized,
    ):
        return GEOMETRY_BENCH

    return GEOMETRY_IN_PLAY


def classify_ability_activation(text: str) -> str:
    normalized = _normalized(text)
    if (
        "once during your turn" in normalized
        or "as often as you like during your turn" in normalized
    ):
        return ACTIVATION_TURN_ACTION
    if normalized.startswith("when ") or normalized.startswith("whenever "):
        return ACTIVATION_TRIGGERED
    return ACTIVATION_PASSIVE


def build_dream_ball_evolution_ability_catalog(
    resources_root: Path = Path("resources"),
) -> tuple[EvolutionAbilityCandidate, ...]:
    """Return exact legal Evolution-Pokemon Ability rows in paper Expanded."""

    sets = load_json(resources_root / "sets" / "en.json")
    expanded_sets = {
        row["id"]
        for row in sets
        if (row.get("legalities") or {}).get("expanded") == "Legal"
    }

    rows: list[EvolutionAbilityCandidate] = []
    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        if path.stem not in expanded_sets:
            continue
        for card in load_json(path):
            status, _source = classify_effective_legality(card)
            if status != "Legal" or card.get("supertype") != "Pokémon":
                continue
            tags = semantic_tags_for_card(card)
            if EVOLUTION_POKEMON not in tags:
                continue

            for ability in card.get("abilities") or ():
                text = ability.get("text") or ""
                if not text:
                    continue
                rows.append(
                    EvolutionAbilityCandidate(
                        card_id=card["id"],
                        card_name=card["name"],
                        subtypes=tuple(card.get("subtypes") or ()),
                        evolves_from=card.get("evolvesFrom"),
                        ability_name=ability.get("name") or "",
                        ability_text=text,
                        geometry=classify_ability_geometry(text),
                        activation=classify_ability_activation(text),
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


def summarize_catalog(
    rows: tuple[EvolutionAbilityCandidate, ...],
) -> dict[str, object]:
    geometry = Counter(row.geometry for row in rows)
    activation = Counter(row.activation for row in rows)
    compatible = tuple(row for row in rows if row.dream_ball_geometry_compatible)
    compatible_activation = Counter(row.activation for row in compatible)
    return {
        "ability_rows": len(rows),
        "exact_prints": len({row.card_id for row in rows}),
        "geometry": dict(sorted(geometry.items())),
        "activation": dict(sorted(activation.items())),
        "dream_ball_geometry_compatible_rows": len(compatible),
        "dream_ball_geometry_compatible_prints": len(
            {row.card_id for row in compatible}
        ),
        "compatible_activation": dict(sorted(compatible_activation.items())),
    }
