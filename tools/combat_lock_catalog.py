from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from tools.build_expanded_legality_baseline import (
    OFFICIAL_BAN_OVERLAY,
    gameplay_fingerprint,
    load_json,
)

CANT_ACTION = re.compile(
    r"(?P<subject>[^.]{0,180}?)\bcan(?:'|’)t (?P<action>retreat|attack|use attacks)\b",
    re.IGNORECASE,
)


def _normalize(text: str) -> str:
    return " ".join(text.split())


def _opponent_dimensions(text: str) -> tuple[str, ...]:
    dimensions: set[str] = set()
    sentences = re.split(r"(?<=[.!?])\s+", text)
    previous = ""

    for sentence in sentences:
        for match in CANT_ACTION.finditer(sentence):
            subject = match.group("subject").lower().strip()
            action = match.group("action").lower()

            if subject.endswith(("this pokémon", "this pokemon", "this card")):
                continue

            context = f"{previous} {sentence}".lower()
            opponent_target = (
                "defending pokémon" in subject
                or "defending pokemon" in subject
                or (
                    ("your opponent's" in subject or "your opponent’s" in subject)
                    and ("pokémon" in subject or "pokemon" in subject)
                )
                or (
                    "their " in subject
                    and ("pokémon" in subject or "pokemon" in subject)
                    and "opponent" in subject
                )
                or (
                    ("that pokémon" in subject or "that pokemon" in subject or subject.endswith("it"))
                    and "opponent" in previous.lower()
                )
                or (
                    ("new active pokémon" in subject or "new active pokemon" in subject)
                    and "opponent" in context
                )
                or (
                    "both yours and your opponent" in subject
                    and ("pokémon" in subject or "pokemon" in subject)
                )
            )
            if opponent_target:
                dimensions.add("retreat" if action == "retreat" else "attack")
        previous = sentence

    return tuple(sorted(dimensions))


def _activation(source_kind: str, text: str, subtypes: tuple[str, ...]) -> str:
    if source_kind == "attack":
        return "attack_applied"
    if "Stadium" in subtypes:
        return "stadium"
    if source_kind == "rule":
        return "one_shot"
    if re.search(
        r"as long as this Pok[eé]mon is (?:your )?Active Pok[eé]mon"
        r"|as long as this Pok[eé]mon is in the Active Spot",
        text,
        re.IGNORECASE,
    ):
        return "active"
    if re.search(r"as long as this Pok[eé]mon is on your Bench", text, re.IGNORECASE):
        return "bench"
    return "passive"


def _is_legal(card: dict[str, Any]) -> bool:
    status = (card.get("legalities") or {}).get("expanded")
    return card["id"] not in OFFICIAL_BAN_OVERLAY and status != "Banned"


def _effects(card: dict[str, Any]) -> list[tuple[str, str, str]]:
    rows = [
        ("ability", effect.get("name", ""), effect.get("text", ""))
        for effect in card.get("abilities") or []
    ]
    rows.extend(
        ("attack", effect.get("name", ""), effect.get("text", ""))
        for effect in card.get("attacks") or []
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
    source_prints: set[str] = set()
    source_variants: set[str] = set()

    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        if path.stem not in expanded_sets:
            continue
        for card in load_json(path):
            if not _is_legal(card):
                continue

            fingerprint = gameplay_fingerprint(card)
            subtypes = tuple(card.get("subtypes") or [])
            for source_kind, effect_name, raw_text in _effects(card):
                text = _normalize(raw_text)
                dimensions = _opponent_dimensions(text)
                if not dimensions:
                    continue

                payload = {
                    "card_name": card["name"],
                    "source_kind": source_kind,
                    "effect_name": effect_name,
                    "text": text,
                    "dimensions": dimensions,
                    "activation": _activation(source_kind, text, subtypes),
                    "stochastic": "flip a coin" in text.lower(),
                }
                signature = hashlib.sha256(
                    json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
                ).hexdigest()[:16]
                row = signatures.setdefault(
                    signature,
                    {**payload, "signature": signature, "print_ids": [], "gameplay_fingerprints": []},
                )
                if card["id"] not in row["print_ids"]:
                    row["print_ids"].append(card["id"])
                if fingerprint not in row["gameplay_fingerprints"]:
                    row["gameplay_fingerprints"].append(fingerprint)
                source_prints.add(card["id"])
                source_variants.add(fingerprint)

    effects = sorted(signatures.values(), key=lambda row: (row["card_name"], row["effect_name"], row["signature"]))
    for row in effects:
        row["dimensions"] = list(row["dimensions"])
        row["print_ids"].sort()
        row["gameplay_fingerprints"].sort()

    dimensions = Counter(dimension for row in effects for dimension in row["dimensions"])
    activation = Counter(row["activation"] for row in effects)
    source_kinds = Counter(row["source_kind"] for row in effects)

    return {
        "counts": {
            "source_prints": len(source_prints),
            "source_gameplay_variants": len(source_variants),
            "effect_signatures": len(effects),
            "print_effect_instances": sum(len(row["print_ids"]) for row in effects),
            "stochastic_signatures": sum(row["stochastic"] for row in effects),
        },
        "dimensions": dict(sorted(dimensions.items())),
        "activation": dict(sorted(activation.items())),
        "source_kinds": dict(sorted(source_kinds.items())),
        "effects": effects,
    }
