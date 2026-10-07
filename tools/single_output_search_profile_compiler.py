"""Compile a conservative family of single-output revealed Trainer searches.

This semantic island covers Item and Supporter effects with exactly one explicit
reveal-to-hand search output whose target label is already supported by the
typed target allocator. Extra effect text is rejected unless it is a generic
Trainer reminder, an ACE SPEC deck rule, or one literal play condition.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from build_expanded_legality_baseline import classify_effective_legality
from trainer_search_profile_compiler import (
    CompiledTrainerSearchProfile,
    SearchOutput,
)
from typed_search_target_allocator import (
    UnsupportedSearchSelector,
    selector_from_label,
)


_SEARCH_RE = re.compile(
    r"Search your deck for (?:a|an) (.*?), reveal it, "
    r"and put it into your hand\. Then, shuffle your deck\.",
    re.IGNORECASE,
)
_DIRECT_DISCARD_RE = re.compile(
    r"Discard (?:(a)|([0-9]+)) cards? from your hand\. If you do,",
    re.IGNORECASE,
)
_PLAY_DISCARD_RE = re.compile(
    r"You can (?:play|use) this card only if you discard "
    r"(?:(another|a) card|([0-9]+) other cards) from your hand\.",
    re.IGNORECASE,
)


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _normalized(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _legal_expanded_trainers(resources_root: Path) -> tuple[dict[str, Any], ...]:
    sets = _load_json(resources_root / "sets" / "en.json")
    expanded_sets = {
        entry["id"]
        for entry in sets
        if (entry.get("legalities") or {}).get("expanded") == "Legal"
    }

    rows: list[dict[str, Any]] = []
    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        if path.stem not in expanded_sets:
            continue
        for card in _load_json(path):
            if card.get("supertype") != "Trainer":
                continue
            if classify_effective_legality(card)[0] != "Legal":
                continue
            rows.append(card)
    return tuple(rows)


def _action_class(card: dict[str, Any]) -> str | None:
    subtypes = tuple(card.get("subtypes") or ())
    for candidate in ("Item", "Supporter"):
        if candidate in subtypes:
            return candidate
    return None


def _is_reminder_rule(rule: str) -> bool:
    lower = rule.casefold()
    return (
        lower.startswith("you may play any number of item cards")
        or lower.startswith("you may play as many item cards as you like")
        or lower.startswith("you may play only 1 supporter card")
        or lower.startswith("ace spec:")
    )


def _discard_cost_from_play_condition(rule: str) -> int | None:
    match = _PLAY_DISCARD_RE.fullmatch(rule)
    if match is None:
        return None
    if match.group(1) is not None:
        return 1
    return int(match.group(2))


def _discard_cost_from_direct_prefix(prefix: str) -> int | None:
    match = _DIRECT_DISCARD_RE.fullmatch(prefix)
    if match is None:
        return None
    if match.group(1) is not None:
        return 1
    return int(match.group(2))


def _compile_card(card: dict[str, Any]) -> CompiledTrainerSearchProfile | None:
    action_class = _action_class(card)
    if action_class is None:
        return None

    rules = tuple(_normalized(rule) for rule in (card.get("rules") or ()))
    search_rules = tuple(
        rule
        for rule in rules
        if "search your deck for" in rule.casefold()
    )
    if len(search_rules) != 1:
        return None

    search_rule = search_rules[0]
    match = _SEARCH_RE.search(search_rule)
    if match is None:
        return None

    target_label = _normalized(match.group(1))
    try:
        selector_from_label(target_label)
    except UnsupportedSearchSelector:
        return None

    prefix = search_rule[: match.start()].strip()
    suffix = search_rule[match.end() :].strip()
    if suffix:
        return None

    discard_cost = 0
    inline_condition: str | None = None
    if prefix:
        direct_cost = _discard_cost_from_direct_prefix(prefix)
        play_cost = _discard_cost_from_play_condition(prefix)
        if direct_cost is not None:
            discard_cost = direct_cost
        elif play_cost is not None:
            discard_cost = play_cost
            inline_condition = prefix
        else:
            return None

    other_conditions: list[str] = []
    for rule in rules:
        if rule == search_rule:
            continue
        if _is_reminder_rule(rule):
            continue

        lower = rule.casefold()
        if lower.startswith(
            (
                "you can play this card only if",
                "you can use this card only if",
            )
        ):
            other_conditions.append(rule)
            cost = _discard_cost_from_play_condition(rule)
            if cost is not None:
                discard_cost = max(discard_cost, cost)
            continue
        return None

    conditions = tuple(
        condition
        for condition in (inline_condition, *other_conditions)
        if condition is not None
    )
    if len(conditions) > 1:
        return None

    return CompiledTrainerSearchProfile(
        card_id=card["id"],
        name=card["name"],
        action_class=action_class,
        base_outputs=(SearchOutput(target_label, 1),),
        required_discard_other_cards=discard_cost,
        play_condition=conditions[0] if conditions else None,
    )


def compile_single_output_revealed_search_profiles(
    resources_root: Path = Path("resources"),
) -> tuple[CompiledTrainerSearchProfile, ...]:
    """Compile the validated one-target reveal-to-hand Trainer family."""

    profiles = [
        profile
        for card in _legal_expanded_trainers(resources_root)
        if (profile := _compile_card(card)) is not None
    ]
    return tuple(
        sorted(
            profiles,
            key=lambda profile: (profile.name, profile.card_id),
        )
    )
