"""Compile and execute dependent two-sided Active/Bench movement bodies."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Any, Literal

from board_object_kernel import BoardState, switch_active
from build_expanded_legality_baseline import classify_effective_legality


Connector = Literal["if_you_do", "then"]


@dataclass(frozen=True)
class CompoundPositionProfile:
    card_id: str
    name: str
    source_name: str
    attack_cost: tuple[str, ...]
    attack_damage: str | None
    effect_text: str
    connector: Connector


@dataclass(frozen=True)
class CompoundPositionExecution:
    actor_board: BoardState
    opponent_board: BoardState
    actor_switched: bool
    opponent_switched: bool


_PATTERNS: dict[str, Connector] = {
    (
        "Switch this Pokémon with 1 of your Benched Pokémon. If you do, "
        "switch out your opponent's Active Pokémon to the Bench. "
        "(Your opponent chooses the new Active Pokémon.)"
    ): "if_you_do",
    (
        "Switch this Pokémon with 1 of your Benched Pokémon. Then, your "
        "opponent switches his or her Active Pokémon with 1 of his or her "
        "Benched Pokémon."
    ): "then",
    (
        "Switch this Pokémon with 1 of your Benched Pokémon. If you do, "
        "your opponent switches their Active Pokémon with 1 of their "
        "Benched Pokémon."
    ): "if_you_do",
    (
        "Switch this Pokémon with 1 of your Benched Pokémon. Then, your "
        "opponent switches the Defending Pokémon with 1 of his or her "
        "Benched Pokémon."
    ): "then",
}


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


def compile_compound_position_profiles(
    resources_root: Path = Path("resources"),
) -> tuple[CompoundPositionProfile, ...]:
    profiles: list[CompoundPositionProfile] = []
    for card in _legal_expanded_cards(resources_root):
        if card.get("supertype") != "Pokémon":
            continue
        for move in card.get("attacks") or ():
            effect_text = _normalized(move.get("text") or "")
            connector = _PATTERNS.get(effect_text)
            if connector is None:
                continue
            profiles.append(
                CompoundPositionProfile(
                    card_id=card["id"],
                    name=card["name"],
                    source_name=move["name"],
                    attack_cost=tuple(move.get("cost") or ()),
                    attack_damage=move.get("damage"),
                    effect_text=effect_text,
                    connector=connector,
                )
            )

    return tuple(
        sorted(
            profiles,
            key=lambda row: (row.name, row.card_id, row.source_name),
        )
    )


def execute_compound_position_effect(
    profile: CompoundPositionProfile,
    actor_board: BoardState,
    opponent_board: BoardState,
    *,
    actor_bench_choice: str | None,
    opponent_bench_choice: str | None,
    blocked_actor_effect_targets: frozenset[str] = frozenset(),
    blocked_opponent_effect_targets: frozenset[str] = frozenset(),
) -> CompoundPositionExecution:
    """Resolve the two movement clauses in printed order.

    Both supported connectors require the first self-switch to occur before the
    opponent switch is attempted. If the second clause cannot be applied, the
    already-completed first switch remains.
    """

    if (
        actor_bench_choice is None
        or actor_board.active_id in blocked_actor_effect_targets
    ):
        return CompoundPositionExecution(
            actor_board,
            opponent_board,
            actor_switched=False,
            opponent_switched=False,
        )

    first = switch_active(actor_board, actor_bench_choice)
    if first is None:
        return CompoundPositionExecution(
            actor_board,
            opponent_board,
            actor_switched=False,
            opponent_switched=False,
        )

    if (
        opponent_bench_choice is None
        or opponent_board.active_id in blocked_opponent_effect_targets
    ):
        return CompoundPositionExecution(
            first,
            opponent_board,
            actor_switched=True,
            opponent_switched=False,
        )

    second = switch_active(opponent_board, opponent_bench_choice)
    if second is None:
        return CompoundPositionExecution(
            first,
            opponent_board,
            actor_switched=True,
            opponent_switched=False,
        )

    return CompoundPositionExecution(
        first,
        second,
        actor_switched=True,
        opponent_switched=True,
    )
