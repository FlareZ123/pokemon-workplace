"""Compile exact card metadata needed by source-scoped action restrictions."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from build_expanded_legality_baseline import classify_effective_legality, load_json
from source_scoped_action_restrictions import CardActionAttempt


@dataclass(frozen=True)
class CardActionMetadata:
    card_id: str
    name: str
    card_kind: str
    tags: frozenset[str]

    def attempt(
        self,
        source_zone: str,
        *,
        mode: str = "play",
        target_relation: str = "any",
    ) -> CardActionAttempt:
        return CardActionAttempt(
            self.card_kind,
            source_zone,
            mode=mode,
            card_tags=self.tags,
            target_relation=target_relation,
        )


def _card_kind(card: dict) -> str | None:
    supertype = card.get("supertype")
    subtypes = set(card.get("subtypes") or ())
    if supertype == "Pokémon":
        return "pokemon"
    if supertype == "Energy":
        return "basic_energy" if "Basic" in subtypes else "special_energy"
    if supertype == "Trainer":
        if any(subtype.startswith("Pokémon Tool") for subtype in subtypes):
            return "tool"
        for subtype, kind in (
            ("Item", "item"),
            ("Supporter", "supporter"),
            ("Stadium", "stadium"),
        ):
            if subtype in subtypes:
                return kind
    return None


def _action_tags(card: dict) -> frozenset[str]:
    tags: set[str] = set()
    subtypes = set(card.get("subtypes") or ())
    if "ACE SPEC" in subtypes:
        tags.add("ace_spec")
    if card.get("supertype") == "Pokémon" and card.get("abilities"):
        tags.add("has_ability")
    if (card.get("name") or "").startswith("Team Rocket's "):
        tags.add("team_rocket")
    return frozenset(tags)


def load_card_action_metadata(
    resources_root: Path,
) -> tuple[CardActionMetadata, ...]:
    sets = load_json(resources_root / "sets" / "en.json")
    expanded_sets = {
        row["id"]
        for row in sets
        if (row.get("legalities") or {}).get("expanded") == "Legal"
    }
    rows: list[CardActionMetadata] = []
    seen: set[str] = set()
    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        if path.stem not in expanded_sets:
            continue
        for card in load_json(path):
            status, _source = classify_effective_legality(card)
            if status != "Legal":
                continue
            card_id = card["id"]
            if card_id in seen:
                raise ValueError(f"duplicate card ID: {card_id}")
            seen.add(card_id)
            card_kind = _card_kind(card)
            if card_kind is None:
                continue
            rows.append(
                CardActionMetadata(
                    card_id=card_id,
                    name=card["name"],
                    card_kind=card_kind,
                    tags=_action_tags(card),
                )
            )
    return tuple(sorted(rows, key=lambda row: row.card_id))


def card_action_metadata_by_id(
    resources_root: Path,
) -> dict[str, CardActionMetadata]:
    return {row.card_id: row for row in load_card_action_metadata(resources_root)}
