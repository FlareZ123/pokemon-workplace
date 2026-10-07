"""Audit historical Pokémon Checkup wording in the bundled card database."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class TimingTextRow:
    release_date: str
    series: str
    set_id: str
    card_id: str
    card_name: str
    source_kind: str
    source_name: str
    text: str
    wording: str


def _text_entries(card: dict[str, object]) -> Iterable[tuple[str, str, str]]:
    for ability in card.get("abilities", []) or []:
        yield "ability", str(ability.get("name", "")), str(ability.get("text", ""))
    for attack in card.get("attacks", []) or []:
        yield "attack", str(attack.get("name", "")), str(attack.get("text", ""))
    for index, rule in enumerate(card.get("rules", []) or []):
        yield "rule", str(index), str(rule)


def audit_checkup_wording(resources: Path) -> tuple[TimingTextRow, ...]:
    sets = json.loads((resources / "sets" / "en.json").read_text(encoding="utf-8"))
    set_meta = {row["id"]: row for row in sets}
    cutoff = set_meta["bw1"]["releaseDate"]

    rows: list[TimingTextRow] = []
    for path in sorted((resources / "cards" / "en").glob("*.json")):
        set_id = path.stem
        meta = set_meta.get(set_id)
        if meta is None or meta["releaseDate"] < cutoff:
            continue

        cards = json.loads(path.read_text(encoding="utf-8"))
        for card in cards:
            if card.get("legalities", {}).get("expanded") != "Legal":
                continue
            for source_kind, source_name, text in _text_entries(card):
                lowered = text.lower()
                has_between = "between turns" in lowered
                has_checkup = "pokémon checkup" in lowered
                if not (has_between or has_checkup):
                    continue
                wording = (
                    "both"
                    if has_between and has_checkup
                    else "between_turns"
                    if has_between
                    else "pokemon_checkup"
                )
                rows.append(
                    TimingTextRow(
                        release_date=meta["releaseDate"],
                        series=meta["series"],
                        set_id=set_id,
                        card_id=card["id"],
                        card_name=card["name"],
                        source_kind=source_kind,
                        source_name=source_name,
                        text=text,
                        wording=wording,
                    )
                )
    return tuple(rows)


def semantic_classes(text: str) -> tuple[str, ...]:
    """Coarse mechanics classes for audited timing text."""

    import re

    lowered = text.lower()
    classes: list[str] = []
    if (
        re.search(r"(put|place)\s+\d+\s+(?:more\s+)?damage counter", lowered)
        and "instead of" in lowered
    ):
        classes.append("counter_base_replace")
    if re.search(r"put\s+\d+\s+more damage counter", lowered):
        classes.append("counter_add")
    if re.search(r"flips?\s+2\s+coins?\s+instead of\s+1", lowered):
        classes.append("coin_count")
    if "doesn't recover" in lowered or "isn't removed even if" in lowered:
        classes.append("recovery_suppress")
    if "skip pokémon checkup" in lowered:
        classes.append("skip_checkup")
    if (
        re.search(r"(put|place)\s+\d+\s+damage counter", lowered)
        and "instead of" not in lowered
        and "more damage counter" not in lowered
    ):
        classes.append("direct_counter_put")
    if "heal " in lowered:
        classes.append("heal")
    return tuple(classes)
