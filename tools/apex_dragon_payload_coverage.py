"""Audit the execution-contract coverage of legal Dragon discard attack sources.

Apex Dragon selects attacks belonging to Dragon Pokémon in the discard pile.
This is a source-card pool inventory, not a deck, discard-access, or in-game
feasibility model. Distinct physical attack prints and lexical body
signatures are reported separately.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from attack_text_coverage_inventory import classify_attack_text
from simple_attack_board_semantics import compile_attack, legal_cards


@dataclass(frozen=True)
class DragonPayloadPrint:
    print_id: str
    card_name: str
    attack_index: int
    attack_name: str
    raw_damage: str
    attack_text: str
    text_coverage_kind: str
    requires_handlers: tuple[str, ...]
    gx_attack: bool
    nested_copy: bool

    @property
    def body_signature(self) -> tuple[str, str, str]:
        return (self.attack_name, self.raw_damage, self.attack_text)

    @property
    def attack_id(self) -> str:
        return f"{self.print_id}:attack:{self.attack_index}"


def build_payload_coverage(resources_root: Path) -> dict:
    cards = tuple(
        card for card in legal_cards(resources_root)
        if card.get("supertype") == "Pokémon"
        and "Dragon" in (card.get("types") or ())
    )
    rows: list[DragonPayloadPrint] = []
    for card in cards:
        for i, _attack in enumerate(card.get("attacks") or ()):
            source = compile_attack(card, i)
            coverage = classify_attack_text(source)
            rows.append(DragonPayloadPrint(
                print_id=source.card_id,
                card_name=source.card_name,
                attack_index=i,
                attack_name=source.attack_name,
                raw_damage=source.raw_damage,
                attack_text=source.raw_text,
                text_coverage_kind=coverage.kind,
                requires_handlers=coverage.requires_handlers,
                gx_attack=source.is_gx_attack,
                nested_copy="as this attack" in source.raw_text.casefold(),
            ))

    signatures: dict[tuple[str, str, str], DragonPayloadPrint] = {}
    for row in rows:
        signatures.setdefault(row.body_signature, row)

    counted = Counter(row.text_coverage_kind for row in rows)
    unique_counted = Counter(
        row.text_coverage_kind for row in signatures.values()
    )
    safe_kinds = {"plain_fixed_or_gx_rule", "exact_damage_counter_clause"}
    def damage_only_safe(row: DragonPayloadPrint) -> bool:
        return (
            row.text_coverage_kind in safe_kinds
            and "gx_budget" not in row.requires_handlers
        )

    return {
        "dragon_card_prints": len(cards),
        "payload_attack_prints": len(rows),
        "unique_lexical_bodies": len(signatures),
        "kinds_per_print": dict(sorted(counted.items())),
        "kinds_per_body": dict(sorted(unique_counted.items())),
        "damage_only_verified_prints": sum(damage_only_safe(r) for r in rows),
        "damage_only_verified_bodies": sum(
            damage_only_safe(r) for r in signatures.values()
        ),
        "gx_attack_prints": sum(row.gx_attack for row in rows),
        "nested_copy_prints": sum(row.nested_copy for row in rows),
        "rows": tuple(rows),
        "signature_representatives": tuple(signatures.values()),
    }
