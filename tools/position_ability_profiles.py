"""Compile and execute a conservative semantic island of movement Abilities."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Any, Literal

from board_object_kernel import BoardState, switch_active
from build_expanded_legality_baseline import classify_effective_legality
from dream_ball_evolution_ability_catalog import (
    ACTIVATION_TRIGGERED,
    GEOMETRY_ACTIVE,
    GEOMETRY_BENCH,
    GEOMETRY_HAND_BENCH_TRIGGER,
    GEOMETRY_HAND_EVOLVE_TRIGGER,
    classify_ability_activation,
    classify_ability_geometry,
)
from position_effect_profile_compiler import (
    ChoiceAuthority,
    PositionEffectKind,
)


SelfSelection = Literal["any_bench", "source_bench"]


@dataclass(frozen=True)
class PositionAbilityProfile:
    card_id: str
    name: str
    ability_name: str
    ability_text: str
    kind: PositionEffectKind
    chooser: ChoiceAuthority
    source_geometry: str
    activation: str
    self_selection: SelfSelection | None = None

    @property
    def event_triggered(self) -> bool:
        return self.activation == ACTIVATION_TRIGGERED


_ALLOWED_TEXTS = frozenset(
    {
        "Once during your turn (before your attack), you may switch your Active Pokémon with 1 of your Benched Pokémon.",
        "Once during your turn, you may use this Ability. Switch your Active Pokémon with 1 of your Benched Pokémon.",
        "Once during your turn, you may switch your Active Pokémon with 1 of your Benched Pokémon.",
        "Once during your turn (before your attack), if this Pokémon is on your Bench, you may switch this Pokémon with your Active Pokémon.",
        "Once during your turn (before your attack), if this Pokémon is on your Bench, you may switch it with your Active Pokémon.",
        "Once during your turn, if this Pokémon is on your Bench, you may switch it with your Active Pokémon.",
        "Once during your turn, you may switch out your opponent's Active Pokémon to the Bench. (Your opponent chooses the new Active Pokémon.)",
        "When you play this Pokémon from your hand to evolve 1 of your Pokémon during your turn, you may switch 1 of your opponent's Benched Pokémon with their Active Pokémon.",
        "When you play this Pokémon from your hand to evolve 1 of your Pokémon, you may switch 1 of your opponent's Benched Pokémon with his or her Active Pokémon.",
        "When you attach a Plasma Energy from your hand to this Pokémon, you may switch 1 of your opponent's Benched Pokémon with his or her Active Pokémon.",
        "If this Pokémon is your Active Pokémon, once during your turn (before your attack), you may switch 1 of your opponent's Benched Pokémon with their Active Pokémon.",
        "Once during your turn (before your attack), if this Pokémon is your Active Pokémon, you may have your opponent switch their Active Pokémon with 1 of their Benched Pokémon.",
        "Once during your turn (before your attack), if this Pokémon is your Active Pokémon, you may have your opponent switch his or her Active Pokémon with 1 of his or her Benched Pokémon.",
        "Once during your turn, you may have your opponent switch their Active Pokémon with 1 of their Benched Pokémon.",
        "Once during your turn (before your attack), you may have your opponent switch their Active Pokémon with 1 of their Benched Pokémon.",
        "Once during your turn (before your attack), you may have your opponent switch his or her Active Pokémon with 1 of his or her Benched Pokémon.",
        "When you play this Pokémon from your hand onto your Bench, you may have your opponent switch their Active Pokémon with 1 of their Benched Pokémon.",
        "When you play this Pokémon from your hand onto your Bench, you may have your opponent switch his or her Active Pokémon with 1 of his or her Benched Pokémon.",
        "When you play this Pokémon from your hand onto your Bench during your turn, you may have your opponent switch their Active Pokémon with 1 of their Benched Pokémon.",
        "When you play this Pokémon from your hand to evolve 1 of your Pokémon during your turn, you may switch in 1 of your opponent's Benched Pokémon to the Active Spot.",
        "Once during your turn, when you play this Pokémon from your hand to evolve 1 of your Pokémon, you may use this Ability. Switch in 1 of your opponent's Benched Pokémon to the Active Spot.",
    }
)


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _normalized(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _legal_expanded_cards(resources_root: Path) -> tuple[dict[str, Any], ...]:
    sets = _load_json(resources_root / "sets" / "en.json")
    expanded_sets = {
        row["id"]
        for row in sets
        if (row.get("legalities") or {}).get("expanded") == "Legal"
    }

    cards: list[dict[str, Any]] = []
    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        if path.stem not in expanded_sets:
            continue
        for card in _load_json(path):
            if classify_effective_legality(card)[0] == "Legal":
                cards.append(card)
    return tuple(cards)


def _movement_semantics(text: str) -> tuple[PositionEffectKind, ChoiceAuthority, SelfSelection | None]:
    if "have your opponent switch" in text or "switch out your opponent's Active" in text:
        return PositionEffectKind.OPPONENT_FORCED_SWITCH, ChoiceAuthority.OPPONENT, None
    if "opponent's Benched" in text:
        return PositionEffectKind.TARGETED_GUST, ChoiceAuthority.ACTOR, None
    if (
        "switch this Pokémon with your Active Pokémon" in text
        or "switch it with your Active Pokémon" in text
    ):
        return PositionEffectKind.SELF_SWITCH, ChoiceAuthority.ACTOR, "source_bench"
    return PositionEffectKind.SELF_SWITCH, ChoiceAuthority.ACTOR, "any_bench"


def compile_position_ability_profiles(
    resources_root: Path = Path("resources"),
) -> tuple[PositionAbilityProfile, ...]:
    profiles: list[PositionAbilityProfile] = []
    for card in _legal_expanded_cards(resources_root):
        if card.get("supertype") != "Pokémon":
            continue
        for ability in card.get("abilities") or ():
            text = _normalized(ability.get("text") or "")
            if text not in _ALLOWED_TEXTS:
                continue
            kind, chooser, self_selection = _movement_semantics(text)
            profiles.append(
                PositionAbilityProfile(
                    card_id=card["id"],
                    name=card["name"],
                    ability_name=ability["name"],
                    ability_text=text,
                    kind=kind,
                    chooser=chooser,
                    source_geometry=classify_ability_geometry(text),
                    activation=classify_ability_activation(text),
                    self_selection=self_selection,
                )
            )

    return tuple(
        sorted(
            profiles,
            key=lambda row: (row.kind.value, row.name, row.card_id, row.ability_name),
        )
    )


def _source_is_present(
    profile: PositionAbilityProfile,
    actor_board: BoardState,
    source_object_id: str,
) -> bool:
    in_active = source_object_id == actor_board.active_id
    in_bench = source_object_id in actor_board.bench_ids

    if profile.source_geometry == GEOMETRY_ACTIVE:
        return in_active
    if profile.source_geometry in {GEOMETRY_BENCH, GEOMETRY_HAND_BENCH_TRIGGER}:
        return in_bench
    if profile.source_geometry == GEOMETRY_HAND_EVOLVE_TRIGGER:
        return in_active or in_bench
    return in_active or in_bench


def execute_position_ability(
    profile: PositionAbilityProfile,
    actor_board: BoardState,
    opponent_board: BoardState,
    *,
    source_object_id: str,
    chosen_actor_bench: str | None = None,
    chosen_opponent_bench: str | None = None,
    abilities_enabled: bool = True,
    trigger_satisfied: bool = False,
) -> tuple[BoardState, BoardState] | None:
    """Execute only the movement body after ordinary Ability prerequisites.

    Triggered profiles require an explicit trigger_satisfied=True so they cannot
    be accidentally called as free turn actions. Usage quotas and any trigger
    resource such as the Plasma Energy attachment remain upstream.
    """

    if not abilities_enabled:
        return None
    if profile.event_triggered and not trigger_satisfied:
        return None
    if not _source_is_present(profile, actor_board, source_object_id):
        return None

    if profile.kind == PositionEffectKind.SELF_SWITCH:
        target = (
            source_object_id
            if profile.self_selection == "source_bench"
            else chosen_actor_bench
        )
        if target is None:
            return None
        moved = switch_active(actor_board, target)
        return None if moved is None else (moved, opponent_board)

    if chosen_opponent_bench is None:
        return None
    moved = switch_active(opponent_board, chosen_opponent_bench)
    return None if moved is None else (actor_board, moved)
