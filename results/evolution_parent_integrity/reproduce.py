"""Reproduce source-wide Stage 1/Stage 2 printed evolution-parent anomalies."""

import json
from pathlib import Path

from tools.build_expanded_legality_baseline import load_json
from tools.verified_card_metadata import normalize_verified_card_metadata

ROOT = Path(__file__).resolve().parents[2]
archive = [
    card
    for path in sorted((ROOT / "resources" / "cards" / "en").glob("*.json"))
    for card in load_json(path)
]
names = {card["name"] for card in archive}
evolutions = [
    card for card in archive
    if card.get("supertype") == "Pokémon"
    and bool({"Stage 1", "Stage 2"} & set(card.get("subtypes") or ()))
]


def analyze(cards: list[dict]) -> tuple[list[str], list[tuple[str, str]]]:
    missing = sorted(c["id"] for c in cards if not c.get("evolvesFrom"))
    unknown = sorted(
        (c["id"], c["evolvesFrom"])
        for c in cards
        if c.get("evolvesFrom") and c["evolvesFrom"] not in names
    )
    return missing, unknown


assert len(archive) == 20635
assert len(evolutions) == 6901
raw_missing, raw_unknown = analyze(evolutions)
assert raw_missing == ["me55-96"]
assert raw_unknown == [
    ("rsv10pt5-131", "Antiuqe Plume Fossil"),
    ("rsv10pt5-50", "Antiuqe Plume Fossil"),
    ("xy12-109", "タマタマ[Exeggcute]"),
]

repaired = [normalize_verified_card_metadata(c) for c in evolutions]
fixed_missing, fixed_unknown = analyze(repaired)
assert fixed_missing == []
assert fixed_unknown == [("xy12-109", "タマタマ[Exeggcute]")]

assert "Antique Plume Fossil" in names
assert "Zorua" in names
assert "Exeggcute" in names
print("Evolution parent source-wide integrity audit: PASS")
print("Total source cards:", len(archive))
print("Stage 1/Stage 2 cards:", len(evolutions))
print("Missing raw parents:", raw_missing)
print("Unknown raw parent names:", json.dumps(raw_unknown, ensure_ascii=True))
print("Remaining unknown after official-print corrections:", json.dumps(fixed_unknown, ensure_ascii=True))
