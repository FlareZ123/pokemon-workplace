"""Catalog paper-Expanded full-hand discard-and-draw reset effects."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
import re

from build_expanded_legality_baseline import classify_effective_legality


RESET_RE = re.compile(r"Discard your hand and draw\s+(\d+)\s+cards?", re.IGNORECASE)
PROFESSOR_RESEARCH_VARIANT = re.compile(
    r"^Professor's Research \(Professor (?:Magnolia|Oak|Sada|Turo)\)$"
)


@dataclass(frozen=True)
class ResetFamily:
    name: str
    source_kind: str
    effect_name: str
    draw_count: int
    supporter: bool
    mentions_first_turn: bool
    ends_turn: bool
    once_per_game: bool
    position_sensitive: bool
    print_ids: tuple[str, ...]


def _canonical_name(name: str) -> str:
    if PROFESSOR_RESEARCH_VARIANT.match(name):
        return "Professor's Research"
    return name


def _entries(card: dict):
    for rule in card.get("rules") or []:
        yield "trainer", "", rule
    for ability in card.get("abilities") or []:
        yield "ability", ability.get("name") or "", ability.get("text") or ""
    for attack in card.get("attacks") or []:
        yield "attack", attack.get("name") or "", attack.get("text") or ""


def catalog_full_hand_resets(
    resources_root: Path = Path("resources"),
) -> tuple[ResetFamily, ...]:
    grouped: dict[tuple, list[str]] = {}

    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        cards = json.loads(path.read_text(encoding="utf-8"))
        for card in cards:
            status, _ = classify_effective_legality(card)
            if status != "Legal":
                continue

            supporter = "Supporter" in set(card.get("subtypes") or [])
            for source_kind, effect_name, text in _entries(card):
                match = RESET_RE.search(text)
                if not match:
                    continue

                draw_count = int(match.group(1))
                normalized = " ".join(text.split())
                key = (
                    _canonical_name(card["name"]),
                    source_kind,
                    effect_name,
                    draw_count,
                    supporter,
                    "first turn" in normalized.lower(),
                    source_kind == "attack" or "your turn ends" in normalized.lower(),
                    "VSTAR Power" in normalized or "GX attack" in normalized,
                    "top card" in normalized.lower() or "bottom of your deck" in normalized.lower(),
                )
                grouped.setdefault(key, []).append(card["id"])

    families = []
    for key, print_ids in grouped.items():
        (
            name,
            source_kind,
            effect_name,
            draw_count,
            supporter,
            mentions_first_turn,
            ends_turn,
            once_per_game,
            position_sensitive,
        ) = key
        families.append(
            ResetFamily(
                name=name,
                source_kind=source_kind,
                effect_name=effect_name,
                draw_count=draw_count,
                supporter=supporter,
                mentions_first_turn=mentions_first_turn,
                ends_turn=ends_turn,
                once_per_game=once_per_game,
                position_sensitive=position_sensitive,
                print_ids=tuple(sorted(print_ids)),
            )
        )

    return tuple(
        sorted(
            families,
            key=lambda row: (
                row.source_kind,
                row.name,
                row.effect_name,
                row.draw_count,
            ),
        )
    )


def main() -> None:
    families = catalog_full_hand_resets()
    print(
        json.dumps(
            {
                "family_count": len(families),
                "print_count": sum(len(row.print_ids) for row in families),
                "families": [asdict(row) for row in families],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
