"""Card-level setup eligibility for paper Expanded.

The ordinary setup rule forces a player to keep an opening hand containing a
legally placeable Basic Pokemon. Some card texts optionally allow non-Basic
cards to be placed during setup, while at least one Basic Pokemon is explicitly
forbidden from being used that way. This module keeps those concepts separate.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from tools.build_expanded_legality_baseline import classify_effective_legality, load_json


@dataclass(frozen=True)
class SetupException:
    card_id: str
    name: str
    supertype: str
    subtypes: tuple[str, ...]
    variant_text: str
    ability_name: str | None
    optional_active: bool
    may_bench: bool
    requires_going_second: bool
    forbidden_basic: bool


@dataclass(frozen=True)
class SetupCatalog:
    legal_print_count: int
    legal_basic_print_count: int
    forced_basic_print_ids: frozenset[str]
    optional_exceptions: tuple[SetupException, ...]
    forbidden_basic_exceptions: tuple[SetupException, ...]
    setup_text_audit: tuple[SetupException, ...]

    def forced_basic_count(self) -> int:
        return len(self.forced_basic_print_ids)

    def optional_active_ids(self, *, going_second: bool) -> frozenset[str]:
        return frozenset(
            row.card_id
            for row in self.optional_exceptions
            if going_second or not row.requires_going_second
        )


def _effective_status(card: dict[str, object]) -> str:
    """Use the shared print-level ban policy, including tournament-only exclusions."""
    return classify_effective_legality(card)[0]


def _text_blocks(card: dict[str, object]) -> list[tuple[str | None, str]]:
    blocks: list[tuple[str | None, str]] = []
    for ability in card.get("abilities") or []:  # type: ignore[union-attr]
        text = str(ability.get("text") or "")
        if text:
            blocks.append((str(ability.get("name") or "") or None, text))
    for rule in card.get("rules") or []:  # type: ignore[union-attr]
        text = str(rule)
        if text:
            blocks.append((None, text))
    return blocks


def _exception_from_block(
    card: dict[str, object], ability_name: str | None, text: str
) -> SetupException:
    lower = " ".join(text.lower().split())
    optional_active = (
        "setting up to play" in lower
        and "may put" in lower
        and "face down" in lower
        and ("active pokémon" in lower or "active pokemon" in lower or "active spot" in lower)
    )
    forbidden_basic = (
        "setting up to play" in lower
        and "cannot put it face down" in lower
        and ("active pokémon" in lower or "active pokemon" in lower or "active spot" in lower)
    )
    return SetupException(
        card_id=str(card["id"]),
        name=str(card["name"]),
        supertype=str(card.get("supertype") or ""),
        subtypes=tuple(card.get("subtypes") or ()),  # type: ignore[arg-type]
        variant_text=text,
        ability_name=ability_name,
        optional_active=optional_active,
        may_bench="on your bench" in lower,
        requires_going_second="if you go second" in lower,
        forbidden_basic=forbidden_basic,
    )


def build_setup_catalog(resources_root: Path) -> SetupCatalog:
    sets = load_json(resources_root / "sets" / "en.json")
    expanded_sets = {
        entry["id"]
        for entry in sets
        if (entry.get("legalities") or {}).get("expanded") == "Legal"
    }

    legal_print_count = 0
    legal_basic_print_count = 0
    forced_basic_ids: set[str] = set()
    optional: list[SetupException] = []
    forbidden: list[SetupException] = []
    audit: list[SetupException] = []

    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        if path.stem not in expanded_sets:
            continue
        for card in load_json(path):
            if _effective_status(card) != "Legal":
                continue
            legal_print_count += 1
            is_basic = card.get("supertype") == "Pokémon" and "Basic" in (card.get("subtypes") or [])
            if is_basic:
                legal_basic_print_count += 1

            card_exceptions: list[SetupException] = []
            for ability_name, text in _text_blocks(card):
                if "setting up to play" not in text.lower():
                    continue
                row = _exception_from_block(card, ability_name, text)
                audit.append(row)
                card_exceptions.append(row)
                if row.optional_active:
                    optional.append(row)
                if row.forbidden_basic:
                    forbidden.append(row)

            is_forbidden = any(row.forbidden_basic for row in card_exceptions)
            if is_basic and not is_forbidden:
                forced_basic_ids.add(str(card["id"]))

    optional.sort(key=lambda row: row.card_id)
    forbidden.sort(key=lambda row: row.card_id)
    audit.sort(key=lambda row: row.card_id)
    return SetupCatalog(
        legal_print_count=legal_print_count,
        legal_basic_print_count=legal_basic_print_count,
        forced_basic_print_ids=frozenset(forced_basic_ids),
        optional_exceptions=tuple(optional),
        forbidden_basic_exceptions=tuple(forbidden),
        setup_text_audit=tuple(audit),
    )
