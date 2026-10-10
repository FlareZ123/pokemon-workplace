from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from tools.build_expanded_legality_baseline import (
    classify_effective_legality,
    gameplay_fingerprint,
    load_json,
)


ABILITY_NO_ABILITIES = re.compile(
    r"\bPok[eé]mon\b[^.]{0,180}\b(?:have|has) no Abilities\b", re.IGNORECASE
)
ABILITY_CANNOT_USE = re.compile(r"\bcan't use (?:any |their )?Abilities\b", re.IGNORECASE)
ABILITY_NO_EFFECT = re.compile(r"\bAbilities? (?:have|has) no effect\b", re.IGNORECASE)
PLAY_LOCK = re.compile(
    r"\bcan't play any (?P<categories>[^.]{1,140}?) from (?:their|his or her|your) hand\b",
    re.IGNORECASE,
)


def _normalize(text: str) -> str:
    return " ".join(text.split())


def _categories_to_dimensions(categories: str) -> set[str]:
    categories = categories.lower()
    compact = re.sub(r"\s+", " ", categories).strip()
    dimensions: set[str] = set()
    if compact in {"card", "cards"}:
        dimensions.add("all_cards_from_hand")
    if "trainer" in categories:
        dimensions.add("trainer")
    if "item" in categories:
        dimensions.add("item")
    if "supporter" in categories:
        dimensions.add("supporter")
    if "ace spec" in categories:
        dimensions.add("ace_spec")
    if "pokémon tool" in categories or "pokemon tool" in categories:
        dimensions.add("tool")
    if "stadium" in categories:
        dimensions.add("stadium")
    if "special energy" in categories:
        dimensions.add("special_energy_play")
    if ("pokémon" in categories or "pokemon" in categories) and "ability" in categories:
        dimensions.add("ability_pokemon_play")
    return dimensions


def _dimensions(text: str) -> tuple[str, ...]:
    dimensions: set[str] = set()

    first_clause = text.split(",", 1)[0].lower()
    tests_existing_no_ability = text.lower().startswith("if ") and "has no abilities" in first_clause
    if not tests_existing_no_ability and (
        ABILITY_NO_ABILITIES.search(text)
        or ABILITY_CANNOT_USE.search(text)
        or ABILITY_NO_EFFECT.search(text)
    ):
        dimensions.add("ability")

    for match in PLAY_LOCK.finditer(text):
        dimensions.update(_categories_to_dimensions(match.group("categories")))

    # Crobat Echoing Madness chooses one of two Trainer classes before applying the lock.
    if re.search(
        r"Choose Item cards or Supporter cards\.[^.]*can't play any of the chosen cards from their hand",
        text,
        re.IGNORECASE,
    ):
        dimensions.update({"item", "supporter"})

    patterns = {
        "special_energy_attach": r"\bcan't attach any Special Energy cards? from (?:their|his or her|your) hand\b",
        "energy_attach_to_target": r"\bcan't attach Energy from (?:their|his or her|your) hand\b",
        "tool_attach": r"\bcan't attach any Pok[eé]mon Tool cards? from (?:their|his or her|your) hand\b",
        "evolution": r"\bcan't play any Pok[eé]mon from (?:their|his or her|your) hand to evolve\b",
    }
    for dimension, pattern in patterns.items():
        if re.search(pattern, text, re.IGNORECASE):
            dimensions.add(dimension)

    if re.search(
        r"Pok[eé]mon Tool(?: cards?|s)?[^.]{0,160}\b(?:have|has) no effect\b",
        text,
        re.IGNORECASE,
    ):
        dimensions.add("tool_effect")

    if re.search(
        r"Stadium(?: card| cards)?[^.]{0,160}\b(?:have|has) no effect\b",
        text,
        re.IGNORECASE,
    ):
        dimensions.add("stadium_effect")

    if re.search(
        r"Special Energy[^.]{0,180}(?:have no other effect|other effects stop working)",
        text,
        re.IGNORECASE,
    ):
        dimensions.add("special_energy_effect")

    if (
        re.search(r"Whenever your opponent plays a Trainer card", text, re.IGNORECASE)
        and re.search(r"that card has no effect", text, re.IGNORECASE)
    ):
        dimensions.add("trainer_effect_coin")

    return tuple(sorted(dimensions))


def _activation(source_kind: str, text: str, subtypes: tuple[str, ...]) -> str:
    if source_kind == "attack":
        return "attack_applied"
    if "Stadium" in subtypes:
        return "stadium"
    if "Pokémon Tool" in subtypes:
        return "tool"
    if source_kind == "rule":
        return "one_shot"
    if re.search(
        r"as long as this Pok[eé]mon is (?:your )?Active Pok[eé]mon"
        r"|as long as this Pok[eé]mon is in the Active Spot"
        r"|if this Pok[eé]mon is your Active Pok[eé]mon",
        text,
        re.IGNORECASE,
    ):
        return "active"
    if re.search(
        r"as long as this Pok[eé]mon is on your Bench|if this Pok[eé]mon is on your Bench",
        text,
        re.IGNORECASE,
    ):
        return "bench"
    if re.search(
        r"if this Pok[eé]mon has (?:a Pok[eé]mon Tool(?: card)?|a Memory Capsule) attached",
        text,
        re.IGNORECASE,
    ):
        return "tool_attached"
    if re.search(r"if you have a Stadium card in play", text, re.IGNORECASE):
        return "stadium_required"
    return "passive"


def _target_scope(text: str) -> str:
    lowered = text.lower()

    # Prefer the actual denial clause over unrelated clauses elsewhere in the effect.
    if re.search(r"your opponent(?:'s)?[^.]{0,180}\b(?:can't play|can't attach|have no abilities|has no abilities)", lowered):
        return "opponent"
    if re.search(r"each player[^.]{0,140}\bcan't", lowered):
        return "both"
    if "both yours and your opponent" in lowered or "each player's" in lowered:
        return "both"
    if lowered.startswith("each pokémon") or lowered.startswith("each pokemon"):
        return "both"
    if "either player" in lowered:
        return "both"
    if re.search(r"\beach pok[eé]mon tool card in play has no effect\b", lowered):
        return "both"
    if re.search(r"\beach (?:stadium|pok[eé]mon tool)", lowered):
        return "both"
    if re.search(r"\ball special energy attached to pok[eé]mon \(both yours and your opponent's\)", lowered):
        return "both"
    if "defending pokémon" in lowered or "defending pokemon" in lowered:
        return "opponent"
    if "your opponent" in lowered:
        return "opponent"
    return "both_or_global"


def _self_vacates(source_kind: str, text: str) -> bool:
    if source_kind != "attack":
        return False
    return bool(
        re.search(
            r"(?:shuffle|put) this Pok[eé]mon(?: and [^.]{0,100})? (?:into|in) your (?:deck|hand)"
            r"|switch this Pok[eé]mon with",
            text,
            re.IGNORECASE,
        )
    )


def _is_legal(card: dict[str, Any]) -> bool:
    return classify_effective_legality(card)[0] == "Legal"


def _effect_rows(card: dict[str, Any]) -> list[tuple[str, str, str]]:
    rows = [
        ("ability", ability.get("name", ""), ability.get("text", ""))
        for ability in card.get("abilities") or []
    ]
    rows.extend(
        ("attack", attack.get("name", ""), attack.get("text", ""))
        for attack in card.get("attacks") or []
    )
    rows.extend(("rule", "", text) for text in card.get("rules") or [])
    return rows


def build_catalog(resources_root: Path) -> dict[str, Any]:
    sets = load_json(resources_root / "sets" / "en.json")
    expanded_sets = {
        row["id"]
        for row in sets
        if (row.get("legalities") or {}).get("expanded") == "Legal"
    }

    signatures: dict[str, dict[str, Any]] = {}
    source_fingerprints: set[str] = set()
    source_prints: set[str] = set()

    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        if path.stem not in expanded_sets:
            continue
        for card in load_json(path):
            if not _is_legal(card):
                continue

            subtypes = tuple(card.get("subtypes") or [])
            fingerprint = gameplay_fingerprint(card)
            for source_kind, effect_name, raw_text in _effect_rows(card):
                text = _normalize(raw_text)
                dimensions = _dimensions(text)
                if not dimensions:
                    continue

                payload = {
                    "card_name": card["name"],
                    "source_kind": source_kind,
                    "effect_name": effect_name,
                    "text": text,
                    "dimensions": dimensions,
                    "activation": _activation(source_kind, text, subtypes),
                    "target_scope": _target_scope(text),
                    "stochastic": "flip a coin" in text.lower(),
                    "exclusive_choice": bool(
                        re.search(r"Choose Item cards or Supporter cards", text, re.IGNORECASE)
                    ),
                    "self_vacates": _self_vacates(source_kind, text),
                    "source_supertype": card.get("supertype"),
                    "source_subtypes": subtypes,
                }
                signature = hashlib.sha256(
                    json.dumps(
                        payload,
                        sort_keys=True,
                        ensure_ascii=False,
                        separators=(",", ":"),
                    ).encode("utf-8")
                ).hexdigest()[:16]

                row = signatures.setdefault(
                    signature,
                    {
                        **payload,
                        "signature": signature,
                        "print_ids": [],
                        "gameplay_fingerprints": [],
                    },
                )
                if card["id"] not in row["print_ids"]:
                    row["print_ids"].append(card["id"])
                if fingerprint not in row["gameplay_fingerprints"]:
                    row["gameplay_fingerprints"].append(fingerprint)
                source_prints.add(card["id"])
                source_fingerprints.add(fingerprint)

    effects = sorted(
        signatures.values(),
        key=lambda row: (row["card_name"], row["effect_name"], row["signature"]),
    )
    for row in effects:
        row["print_ids"].sort()
        row["gameplay_fingerprints"].sort()
        row["dimensions"] = list(row["dimensions"])
        row["source_subtypes"] = list(row["source_subtypes"])

    dimension_counts = Counter(dimension for row in effects for dimension in row["dimensions"])
    activation_counts = Counter(row["activation"] for row in effects)
    source_kind_counts = Counter(row["source_kind"] for row in effects)
    target_scope_counts = Counter(row["target_scope"] for row in effects)

    return {
        "counts": {
            "source_prints": len(source_prints),
            "source_gameplay_variants": len(source_fingerprints),
            "lock_effect_signatures": len(effects),
            "lock_effect_print_instances": sum(len(row["print_ids"]) for row in effects),
            "stochastic_signatures": sum(row["stochastic"] for row in effects),
            "exclusive_choice_signatures": sum(row["exclusive_choice"] for row in effects),
            "self_vacating_attack_signatures": sum(row["self_vacates"] for row in effects),
        },
        "dimensions": dict(sorted(dimension_counts.items())),
        "activation": dict(sorted(activation_counts.items())),
        "source_kinds": dict(sorted(source_kind_counts.items())),
        "target_scope": dict(sorted(target_scope_counts.items())),
        "effects": effects,
    }
