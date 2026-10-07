"""Compile a conservative direct-to-Bench Basic Pokemon search family.

This semantic island covers effectively legal paper-Expanded effects whose
entire search body is a deterministic deck search for one or more Basic Pokemon
that are put directly onto the Bench, followed by a deck shuffle.

The compiler preserves whether the source is a Pokemon attack or a Trainer
card, the maximum number of searched Pokemon, explicit ``up to`` wording, and
simple Trainer play conditions such as Battle VIP Pass's first-turn gate.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Any

from build_expanded_legality_baseline import classify_effective_legality
from trainer_search_profile_compiler import CompiledTrainerSearchProfile, SearchOutput


@dataclass(frozen=True)
class DirectBenchSearchProfile:
    """One literal Basic-Pokemon deck-search effect that benches its payload."""

    card_id: str
    name: str
    source_kind: str
    action_class: str
    source_name: str | None
    output: SearchOutput
    explicit_up_to: bool
    attack_cost: tuple[str, ...] = ()
    play_condition: str | None = None

    def __post_init__(self) -> None:
        if self.source_kind not in {"attack", "trainer"}:
            raise ValueError("source_kind must be 'attack' or 'trainer'")
        if self.output.label != "Basic Pokémon":
            raise ValueError("direct Bench compiler only emits Basic Pokemon")
        if self.output.max_units is None or self.output.max_units < 1:
            raise ValueError("direct Bench search must have a positive finite maximum")
        if self.source_kind == "attack" and not self.source_name:
            raise ValueError("attack profiles require source_name")
        if self.source_kind == "trainer" and self.source_name is not None:
            raise ValueError("Trainer profiles do not use source_name")


_DIRECT_BENCH_RE = re.compile(
    r"^Search your deck for (?:(a)|(?:(up to) )?([0-9]+)) Basic Pok[eé]mon "
    r"and put (?:it|them) onto your Bench\. "
    r"(?:Then, shuffle your deck\.|Shuffle your deck afterward\.)$",
    re.IGNORECASE,
)


def project_direct_bench_trainer_profile(
    profile: DirectBenchSearchProfile,
) -> CompiledTrainerSearchProfile:
    """Project a direct-Bench Trainer onto the shared search transaction schema.

    The shared profile deliberately does not encode destination. Callers must
    pass the direct-Bench staging destination explicitly to the transaction.
    """

    if profile.source_kind != "trainer":
        raise ValueError("only Trainer direct-Bench profiles can be projected")
    return CompiledTrainerSearchProfile(
        card_id=profile.card_id,
        name=profile.name,
        action_class=profile.action_class,
        base_outputs=(profile.output,),
        play_condition=profile.play_condition,
    )


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _normalized(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _legal_expanded_cards(resources_root: Path) -> tuple[dict[str, Any], ...]:
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
            if classify_effective_legality(card)[0] == "Legal":
                rows.append(card)
    return tuple(rows)


def _match_search_body(text: str) -> tuple[int, bool] | None:
    match = _DIRECT_BENCH_RE.fullmatch(_normalized(text))
    if match is None:
        return None
    maximum = 1 if match.group(1) is not None else int(match.group(3))
    return maximum, match.group(2) is not None


def _trainer_action_class(card: dict[str, Any]) -> str | None:
    subtypes = tuple(card.get("subtypes") or ())
    for candidate in ("Item", "Supporter", "Stadium", "Pokémon Tool"):
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


def _trainer_profile(card: dict[str, Any]) -> DirectBenchSearchProfile | None:
    action_class = _trainer_action_class(card)
    if action_class is None:
        return None

    rules = tuple(_normalized(rule) for rule in (card.get("rules") or ()))
    matched = tuple(
        (rule, parsed)
        for rule in rules
        if (parsed := _match_search_body(rule)) is not None
    )
    if len(matched) != 1:
        return None

    search_rule, (maximum, explicit_up_to) = matched[0]
    conditions: list[str] = []
    for rule in rules:
        if rule == search_rule or _is_reminder_rule(rule):
            continue
        lower = rule.casefold()
        if lower.startswith(
            ("you can use this card only", "you can play this card only")
        ):
            conditions.append(rule)
            continue
        return None
    if len(conditions) > 1:
        return None

    return DirectBenchSearchProfile(
        card_id=card["id"],
        name=card["name"],
        source_kind="trainer",
        action_class=action_class,
        source_name=None,
        output=SearchOutput("Basic Pokémon", maximum),
        explicit_up_to=explicit_up_to,
        play_condition=conditions[0] if conditions else None,
    )


def _attack_profiles(
    card: dict[str, Any],
) -> tuple[DirectBenchSearchProfile, ...]:
    if card.get("supertype") != "Pokémon":
        return ()

    profiles: list[DirectBenchSearchProfile] = []
    for attack in card.get("attacks") or ():
        parsed = _match_search_body(attack.get("text") or "")
        if parsed is None:
            continue
        maximum, explicit_up_to = parsed
        profiles.append(
            DirectBenchSearchProfile(
                card_id=card["id"],
                name=card["name"],
                source_kind="attack",
                action_class="Attack",
                source_name=attack["name"],
                output=SearchOutput("Basic Pokémon", maximum),
                explicit_up_to=explicit_up_to,
                attack_cost=tuple(attack.get("cost") or ()),
            )
        )
    return tuple(profiles)


def compile_direct_bench_search_profiles(
    resources_root: Path = Path("resources"),
) -> tuple[DirectBenchSearchProfile, ...]:
    """Compile the validated Basic-Pokemon direct-to-Bench semantic island."""

    profiles: list[DirectBenchSearchProfile] = []
    for card in _legal_expanded_cards(resources_root):
        if card.get("supertype") == "Trainer":
            profile = _trainer_profile(card)
            if profile is not None:
                profiles.append(profile)
        profiles.extend(_attack_profiles(card))

    return tuple(
        sorted(
            profiles,
            key=lambda row: (
                row.name,
                row.card_id,
                row.source_kind,
                row.source_name or "",
            ),
        )
    )
