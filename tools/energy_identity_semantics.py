from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from tools.build_expanded_legality_baseline import classify_effective_legality

OFFICIAL_BAN_OVERLAY = {
    "swsh2-22",
    "swsh45sv-SV013",
    "swsh10tg-TG02",
    "swshp-SWSH022",
    "swsh7-83",
    "swsh7-185",
    "swsh7-186",
}

ENERGY_TYPES = (
    "Grass",
    "Fire",
    "Water",
    "Lightning",
    "Psychic",
    "Fighting",
    "Darkness",
    "Metal",
    "Fairy",
)

BASIC_TYPED = re.compile(
    r"\bBasic (Grass|Fire|Water|Lightning|Psychic|Fighting|Darkness|Metal|Fairy) Energy\b",
    re.IGNORECASE,
)

TYPE_OVERRIDE = re.compile(
    r"All Energy attached to (?:this Pokémon|your Pokémon) are "
    r"(Grass|Fire|Water|Lightning|Psychic|Fighting|Darkness|Metal|Fairy) "
    r"Energy instead of their usual type",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class AttachedEnergyState:
    card_name: str
    is_basic: bool
    units: int
    provided_types: frozenset[str]

    def matches_basic_named(self, energy_type: str) -> bool:
        return self.is_basic and self.card_name == f"Basic {energy_type} Energy"

    def can_satisfy_typed_cost(self, energy_type: str) -> bool:
        return energy_type in self.provided_types


def normalize(text: str) -> str:
    return " ".join(text.split())


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def iter_text_fields(card: dict[str, Any]):
    for attack in card.get("attacks") or []:
        yield "attack", attack["name"], normalize(attack.get("text") or "")
    for ability in card.get("abilities") or []:
        yield "ability", ability["name"], normalize(ability.get("text") or "")
    for index, rule in enumerate(card.get("rules") or []):
        yield "rule", str(index), normalize(rule)


def build(resources_root: Path) -> dict[str, Any]:
    sets = load_json(resources_root / "sets" / "en.json")
    expanded_sets = {
        entry["id"]
        for entry in sets
        if (entry.get("legalities") or {}).get("expanded") == "Legal"
    }

    references: list[dict[str, Any]] = []
    overrides: list[dict[str, Any]] = []
    multiplicity: list[dict[str, Any]] = []

    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        if path.stem not in expanded_sets:
            continue
        for card in load_json(path):
            if classify_effective_legality(card)[0] == "Banned":
                continue

            for source_kind, source_name, text in iter_text_fields(card):
                named_types = sorted(
                    {match.group(1).title() for match in BASIC_TYPED.finditer(text)}
                )
                if named_types:
                    references.append(
                        {
                            "card_id": card["id"],
                            "card_name": card["name"],
                            "source_kind": source_kind,
                            "source_name": source_name,
                            "text": text,
                            "basic_energy_names": named_types,
                        }
                    )

                override = TYPE_OVERRIDE.search(text)
                if override:
                    overrides.append(
                        {
                            "card_id": card["id"],
                            "card_name": card["name"],
                            "source_kind": source_kind,
                            "source_name": source_name,
                            "override_type": override.group(1).title(),
                            "text": text,
                        }
                    )

                if named_types and re.search(r"\bprovides?\b", text, re.IGNORECASE):
                    multiplicity.append(
                        {
                            "card_id": card["id"],
                            "card_name": card["name"],
                            "source_kind": source_kind,
                            "source_name": source_name,
                            "text": text,
                            "basic_energy_names": named_types,
                        }
                    )

    distinct_reference_texts = {row["text"] for row in references}
    reference_kind_counts = Counter(row["source_kind"] for row in references)
    reference_type_counts = Counter(
        energy_type
        for row in references
        for energy_type in row["basic_energy_names"]
    )
    override_signatures = {
        (row["card_name"], row["source_kind"], row["source_name"], row["text"])
        for row in overrides
    }
    multiplicity_signatures = {
        (row["card_name"], row["source_kind"], row["source_name"], row["text"])
        for row in multiplicity
    }

    energy_burn_grass = AttachedEnergyState(
        card_name="Basic Grass Energy",
        is_basic=True,
        units=2,
        provided_types=frozenset({"Fire"}),
    )
    double_dragon = AttachedEnergyState(
        card_name="Double Dragon Energy",
        is_basic=False,
        units=2,
        provided_types=frozenset(ENERGY_TYPES),
    )

    return {
        "basic_named_references": {
            "print_text_instances": len(references),
            "distinct_texts": len(distinct_reference_texts),
            "by_source_kind": dict(sorted(reference_kind_counts.items())),
            "by_basic_energy_name": dict(sorted(reference_type_counts.items())),
        },
        "type_override_effects": {
            "print_instances": len(overrides),
            "distinct_signatures": len(override_signatures),
            "rows": overrides,
        },
        "basic_named_multiplicity_effects": {
            "print_instances": len(multiplicity),
            "distinct_signatures": len(multiplicity_signatures),
            "rows": multiplicity,
        },
        "semantic_regressions": {
            "basic_grass_under_energy_burn_and_wild_growth": {
                "matches_basic_grass_name": energy_burn_grass.matches_basic_named("Grass"),
                "matches_basic_fire_name": energy_burn_grass.matches_basic_named("Fire"),
                "can_pay_fire": energy_burn_grass.can_satisfy_typed_cost("Fire"),
                "can_pay_grass": energy_burn_grass.can_satisfy_typed_cost("Grass"),
                "energy_units": energy_burn_grass.units,
            },
            "double_dragon": {
                "matches_basic_psychic_name": double_dragon.matches_basic_named("Psychic"),
                "can_pay_psychic": double_dragon.can_satisfy_typed_cost("Psychic"),
                "energy_units": double_dragon.units,
            },
        },
    }


def main() -> None:
    import sys

    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("resources")
    print(json.dumps(build(root), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
