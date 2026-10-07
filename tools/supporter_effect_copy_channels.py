"""Catalog and model Supporter-effect copying channels in Expanded.

A Supporter card can contribute its printed effect through more than one source
action class. In particular, several attacks execute a Supporter's effect as the
effect of the attack. The physical Supporter card and the action whose effect is
currently executing must therefore remain distinct.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Iterable

from build_expanded_legality_baseline import classify_effective_legality
from turn_action_budget import TurnAction, TurnActionBudget


COPY_PATTERN = re.compile(
    r"use the effect of .* as the effect of (?:this attack|this card)",
    re.IGNORECASE,
)


def _normalize(text: str) -> str:
    return " ".join(text.split())


def iter_legal_expanded_cards(resources_root: Path) -> Iterable[dict[str, Any]]:
    sets = json.loads(
        (resources_root / "sets" / "en.json").read_text(encoding="utf-8")
    )
    expanded_sets = {
        row["id"]
        for row in sets
        if (row.get("legalities") or {}).get("expanded") == "Legal"
    }
    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        if path.stem not in expanded_sets:
            continue
        for card in json.loads(path.read_text(encoding="utf-8")):
            status, _ = classify_effective_legality(card)
            if status == "Legal":
                yield card


def supporter_effect_copy_rows(resources_root: Path) -> list[dict[str, Any]]:
    """Return legal print-level effects that copy a Supporter effect."""

    rows: list[dict[str, Any]] = []
    for card in iter_legal_expanded_cards(resources_root):
        for attack in card.get("attacks") or []:
            text = _normalize(attack.get("text", ""))
            if "supporter" in text.lower() and COPY_PATTERN.search(text):
                rows.append(
                    {
                        "id": card["id"],
                        "name": card["name"],
                        "source_class": "Attack",
                        "effect_name": attack.get("name"),
                        "text": text,
                    }
                )
        if "Supporter" in (card.get("subtypes") or []):
            for rule in card.get("rules") or []:
                text = _normalize(rule)
                if "supporter" in text.lower() and COPY_PATTERN.search(text):
                    rows.append(
                        {
                            "id": card["id"],
                            "name": card["name"],
                            "source_class": "Supporter",
                            "effect_name": None,
                            "text": text,
                        }
                    )
    return rows


@dataclass(frozen=True)
class SupporterCopyCard:
    copy_id: str
    name: str
    printed_effect: str

    def __post_init__(self) -> None:
        if not self.copy_id or not self.name or not self.printed_effect:
            raise ValueError("Supporter copy identity and effect must be non-empty")


@dataclass(frozen=True)
class CopiedSupporterAttackState:
    """Minimal state for Mimikyu-like Supporter-effect attack execution."""

    budget: TurnActionBudget
    hand: tuple[SupporterCopyCard, ...] = ()
    discard: tuple[SupporterCopyCard, ...] = ()
    executed_effect: str | None = None
    effect_source_copy_id: str | None = None
    execution_class: str | None = None

    def __post_init__(self) -> None:
        copy_ids = [card.copy_id for card in self.hand + self.discard]
        if len(copy_ids) != len(set(copy_ids)):
            raise ValueError("A physical Supporter copy cannot occupy two zones")


def execute_impersonation(
    state: CopiedSupporterAttackState,
    supporter_copy_id: str,
) -> CopiedSupporterAttackState | None:
    """Execute a Mimikyu-like copied Supporter effect as an attack effect.

    This models action provenance and physical movement only. It does not
    implement arbitrary Supporter bodies. The selected Supporter is discarded
    by the attack before its printed effect body is delegated to the attack.

    The Supporter-play usage count is preserved. The attack action then closes
    the turn through the canonical budget.
    """

    if not state.budget.can(TurnAction.ATTACK):
        return None

    selected: SupporterCopyCard | None = None
    remaining: list[SupporterCopyCard] = []
    for card in state.hand:
        if card.copy_id == supporter_copy_id and selected is None:
            selected = card
        else:
            remaining.append(card)
    if selected is None:
        return None

    before_supporter_usage = state.budget.supporter_plays_used
    ended = state.budget.consume(TurnAction.ATTACK)
    if ended is None:
        return None
    if ended.supporter_plays_used != before_supporter_usage:
        raise AssertionError("Attack execution must not mutate Supporter-play history")

    return replace(
        state,
        budget=ended,
        hand=tuple(remaining),
        discard=state.discard + (selected,),
        executed_effect=selected.printed_effect,
        effect_source_copy_id=selected.copy_id,
        execution_class="attack_effect",
    )
