from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Literal

from tools.build_expanded_legality_baseline import classify_effective_legality, load_json

Severity = Literal["error", "warning"]

ACE_SPEC_RULE = "You can't have more than 1 ACE SPEC card in your deck."
RADIANT_RULE = "Radiant Pokémon Rule: You can't have more than 1 Radiant Pokémon in your deck."
POKEMON_STAR_RULE = "You can't have more than 1 Pokémon Star in your deck."
PRISM_RULE_FRAGMENT = "(Prism Star) Rule: You can't have more than 1 ◇ card with the same name in your deck."


@dataclass(frozen=True)
class DeckEntry:
    card_id: str
    quantity: int


@dataclass(frozen=True)
class CardRecord:
    card_id: str
    name: str
    supertype: str
    subtypes: tuple[str, ...]
    rules: tuple[str, ...]
    effective_status: Literal["Legal", "Banned"]
    legality_source: str

    @property
    def is_basic_energy(self) -> bool:
        return self.supertype == "Energy" and "Basic" in self.subtypes

    @property
    def is_basic_pokemon(self) -> bool:
        return self.supertype == "Pokémon" and "Basic" in self.subtypes


@dataclass(frozen=True)
class ValidationIssue:
    severity: Severity
    code: str
    message: str
    card_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class ValidationReport:
    total_cards: int
    issues: tuple[ValidationIssue, ...]

    @property
    def valid(self) -> bool:
        return not any(issue.severity == "error" for issue in self.issues)


def _card_record(raw: dict) -> CardRecord:
    status, source = classify_effective_legality(raw)
    return CardRecord(
        card_id=raw["id"],
        name=raw["name"],
        supertype=raw["supertype"],
        subtypes=tuple(raw.get("subtypes") or ()),
        rules=tuple(raw.get("rules") or ()),
        effective_status=status,
        legality_source=source,
    )


def load_all_card_records(resources_root: Path) -> dict[str, CardRecord]:
    records: dict[str, CardRecord] = {}
    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        for raw in load_json(path):
            records[raw["id"]] = _card_record(raw)
    return records


def load_expanded_card_records(resources_root: Path) -> dict[str, CardRecord]:
    sets = load_json(resources_root / "sets" / "en.json")
    expanded_sets = {
        entry["id"]
        for entry in sets
        if (entry.get("legalities") or {}).get("expanded") == "Legal"
    }

    records: dict[str, CardRecord] = {}
    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        if path.stem not in expanded_sets:
            continue
        for raw in load_json(path):
            records[raw["id"]] = _card_record(raw)
    return records


def _has_rule(record: CardRecord, text: str) -> bool:
    return any(rule == text or rule.endswith(text) for rule in record.rules)


def _has_prism_rule(record: CardRecord) -> bool:
    return any(PRISM_RULE_FRAGMENT in rule for rule in record.rules)


def _has_self_singleton_rule(record: CardRecord) -> bool:
    target = f"You can't have more than 1 {record.name} in your deck."
    return target in record.rules


def _recognized_copy_constraint(record: CardRecord, rule: str) -> bool:
    if rule == POKEMON_STAR_RULE or rule == RADIANT_RULE:
        return True
    if rule == ACE_SPEC_RULE or rule.endswith(ACE_SPEC_RULE):
        return True
    if PRISM_RULE_FRAGMENT in rule:
        return True
    return rule == f"You can't have more than 1 {record.name} in your deck."


def _validate_with_records(
    entries: Iterable[DeckEntry],
    records: dict[str, CardRecord],
    *,
    deck_size: int,
    enforce_format_legality: bool,
    unknown_scope: str,
) -> ValidationReport:
    quantities: Counter[str] = Counter()
    issues: list[ValidationIssue] = []
    total_cards = 0

    for entry in entries:
        if isinstance(entry.quantity, bool) or not isinstance(entry.quantity, int) or entry.quantity <= 0:
            issues.append(ValidationIssue(
                "error",
                "invalid_quantity",
                f"{entry.card_id} has invalid quantity {entry.quantity!r}; quantities must be positive integers.",
                (entry.card_id,),
            ))
            continue
        quantities[entry.card_id] += entry.quantity
        total_cards += entry.quantity

    if total_cards != deck_size:
        issues.append(ValidationIssue(
            "error",
            "deck_size",
            f"Deck has {total_cards} cards; competitive Pokémon TCG decks require exactly {deck_size}.",
        ))

    known: dict[str, CardRecord] = {}
    for card_id in sorted(quantities):
        record = records.get(card_id)
        if record is None:
            issues.append(ValidationIssue(
                "error",
                "unknown_print",
                f"Card ID {card_id} is not present in the {unknown_scope}.",
                (card_id,),
            ))
            continue
        known[card_id] = record
        if enforce_format_legality:
            if record.effective_status == "Banned":
                issues.append(ValidationIssue(
                    "error",
                    "illegal_print",
                    f"{record.name} ({card_id}) is excluded from the research format by {record.legality_source}.",
                    (card_id,),
                ))
            elif record.legality_source == "set_fallback":
                issues.append(ValidationIssue(
                    "warning",
                    "set_fallback_legality",
                    f"{record.name} ({card_id}) is treated as legal via set-level fallback because its card-level Expanded field is absent.",
                    (card_id,),
                ))

        for rule in record.rules:
            low = rule.lower()
            if "can't have more than" in low and "deck" in low and not _recognized_copy_constraint(record, rule):
                issues.append(ValidationIssue(
                    "warning",
                    "unrecognized_deck_constraint",
                    f"{record.name} ({card_id}) has an unrecognized deck-construction rule: {rule}",
                    (card_id,),
                ))

    if not any(record.is_basic_pokemon for record in known.values()):
        issues.append(ValidationIssue(
            "error",
            "missing_basic_pokemon",
            "Deck must contain at least one Basic Pokémon.",
        ))

    name_counts: Counter[str] = Counter()
    limited_name_counts: Counter[str] = Counter()
    ids_by_name: dict[str, list[str]] = defaultdict(list)
    for card_id, quantity in quantities.items():
        record = known.get(card_id)
        if record is None:
            continue
        name_counts[record.name] += quantity
        ids_by_name[record.name].append(card_id)
        if not record.is_basic_energy:
            limited_name_counts[record.name] += quantity

    for name, quantity in sorted(limited_name_counts.items()):
        if quantity > 4:
            issues.append(ValidationIssue(
                "error",
                "name_copy_limit",
                f"{name} appears {quantity} times; non-Basic-Energy cards are limited to 4 cards with the same name.",
                tuple(sorted(ids_by_name[name])),
            ))

    ace_spec_ids = [
        card_id for card_id, record in known.items()
        if "ACE SPEC" in record.subtypes or _has_rule(record, ACE_SPEC_RULE)
    ]
    ace_spec_count = sum(quantities[card_id] for card_id in ace_spec_ids)
    if ace_spec_count > 1:
        issues.append(ValidationIssue(
            "error",
            "ace_spec_limit",
            f"Deck contains {ace_spec_count} ACE SPEC cards; the deck-wide limit is 1.",
            tuple(sorted(ace_spec_ids)),
        ))

    radiant_ids = [
        card_id for card_id, record in known.items()
        if "Radiant" in record.subtypes or RADIANT_RULE in record.rules
    ]
    radiant_count = sum(quantities[card_id] for card_id in radiant_ids)
    if radiant_count > 1:
        issues.append(ValidationIssue(
            "error",
            "radiant_limit",
            f"Deck contains {radiant_count} Radiant Pokémon; the deck-wide limit is 1.",
            tuple(sorted(radiant_ids)),
        ))

    star_ids = [
        card_id for card_id, record in known.items()
        if "Star" in record.subtypes or POKEMON_STAR_RULE in record.rules
    ]
    star_count = sum(quantities[card_id] for card_id in star_ids)
    if star_count > 1:
        issues.append(ValidationIssue(
            "error",
            "pokemon_star_limit",
            f"Deck contains {star_count} Pokémon Star cards; the deck-wide limit is 1.",
            tuple(sorted(star_ids)),
        ))

    prism_names = {
        record.name
        for record in known.values()
        if "Prism Star" in record.subtypes or _has_prism_rule(record)
    }
    for name in sorted(prism_names):
        if name_counts[name] > 1:
            issues.append(ValidationIssue(
                "error",
                "prism_star_name_limit",
                f"{name} appears {name_counts[name]} times; Prism Star cards are limited to 1 card with the same name.",
                tuple(sorted(ids_by_name[name])),
            ))

    self_singleton_names = {
        record.name for record in known.values() if _has_self_singleton_rule(record)
    }
    for name in sorted(self_singleton_names):
        if name_counts[name] > 1:
            issues.append(ValidationIssue(
                "error",
                "self_named_singleton_limit",
                f"{name} appears {name_counts[name]} times; its card text limits the deck to 1 copy.",
                tuple(sorted(ids_by_name[name])),
            ))

    return ValidationReport(total_cards=total_cards, issues=tuple(issues))


def validate_deck_construction(
    entries: Iterable[DeckEntry],
    resources_root: Path,
    *,
    deck_size: int = 60,
) -> ValidationReport:
    """Validate deck-construction rules against every exact print in the snapshot."""

    return _validate_with_records(
        entries,
        load_all_card_records(resources_root),
        deck_size=deck_size,
        enforce_format_legality=False,
        unknown_scope="bundled card snapshot",
    )


def validate_deck(
    entries: Iterable[DeckEntry],
    resources_root: Path,
    *,
    deck_size: int = 60,
) -> ValidationReport:
    return _validate_with_records(
        entries,
        load_expanded_card_records(resources_root),
        deck_size=deck_size,
        enforce_format_legality=True,
        unknown_scope="Expanded-scope card index",
    )
