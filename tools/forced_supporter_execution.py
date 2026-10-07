"""Model Hypno Hand Control as an out-of-turn forced Supporter play."""

from __future__ import annotations

import json
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Iterable, Literal

from build_expanded_legality_baseline import classify_effective_legality
from turn_action_budget import TurnAction, TurnActionBudget

def _normalize(text: str) -> str:
    return " ".join(text.split())

def iter_legal_expanded_cards(resources_root: Path) -> Iterable[dict[str, Any]]:
    sets = json.loads((resources_root / "sets" / "en.json").read_text(encoding="utf-8"))
    expanded_sets = {
        row["id"] for row in sets
        if (row.get("legalities") or {}).get("expanded") == "Legal"
    }
    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        if path.stem not in expanded_sets:
            continue
        for card in json.loads(path.read_text(encoding="utf-8")):
            status, _ = classify_effective_legality(card)
            if status == "Legal":
                yield card

def forced_supporter_play_rows(resources_root: Path) -> list[dict[str, str]]:
    rows = []
    for card in iter_legal_expanded_cards(resources_root):
        for attack in card.get("attacks") or []:
            text = _normalize(attack.get("text", ""))
            if "opponent plays that Supporter card" in text:
                rows.append({
                    "id": card["id"],
                    "name": card["name"],
                    "attack_name": attack["name"],
                    "text": text,
                })
    return rows

@dataclass(frozen=True)
class SupporterInstance:
    copy_id: str
    name: str

    def __post_init__(self) -> None:
        if not self.copy_id or not self.name:
            raise ValueError("Supporter instance identity must be non-empty")

@dataclass(frozen=True)
class ForcedSupporterEvent:
    turn_owner: str
    card_player: str
    decision_controller: str
    source_attack: str
    supporter_copy_id: str

@dataclass(frozen=True)
class ForcedSupporterState:
    current_player: str
    other_player: str
    current_budget: TurnActionBudget
    other_budget: TurnActionBudget
    other_hand: tuple[SupporterInstance, ...] = ()
    resolving_supporter: SupporterInstance | None = None
    other_discard: tuple[SupporterInstance, ...] = ()
    other_hand_return: tuple[SupporterInstance, ...] = ()
    other_prize: tuple[SupporterInstance, ...] = ()
    event: ForcedSupporterEvent | None = None
    out_of_turn_supporter_plays: int = 0

    def __post_init__(self) -> None:
        if self.current_player == self.other_player:
            raise ValueError("players must be distinct")
        cards = list(self.other_hand) + list(self.other_discard)
        cards += list(self.other_hand_return) + list(self.other_prize)
        if self.resolving_supporter is not None:
            cards.append(self.resolving_supporter)
        ids = [card.copy_id for card in cards]
        if len(ids) != len(set(ids)):
            raise ValueError("a Supporter instance cannot occupy two zones")

def begin_hand_control(
    state: ForcedSupporterState,
    supporter_copy_id: str,
) -> ForcedSupporterState | None:
    if state.event is not None or state.resolving_supporter is not None:
        return None
    if not state.current_budget.can(TurnAction.ATTACK):
        return None

    selected = None
    remaining = []
    for card in state.other_hand:
        if card.copy_id == supporter_copy_id and selected is None:
            selected = card
        else:
            remaining.append(card)
    if selected is None:
        return None

    event = ForcedSupporterEvent(
        turn_owner=state.current_player,
        card_player=state.other_player,
        decision_controller=state.current_player,
        source_attack="Hand Control",
        supporter_copy_id=selected.copy_id,
    )
    return replace(
        state,
        other_hand=tuple(remaining),
        resolving_supporter=selected,
        event=event,
        out_of_turn_supporter_plays=state.out_of_turn_supporter_plays + 1,
    )

def finish_hand_control(
    state: ForcedSupporterState,
    *,
    final_destination: Literal["discard", "hand", "prize"] = "discard",
) -> ForcedSupporterState | None:
    if state.event is None or state.resolving_supporter is None:
        return None
    if state.event.turn_owner != state.current_player:
        return None
    if state.event.card_player != state.other_player:
        return None

    ended = state.current_budget.consume(TurnAction.ATTACK)
    if ended is None:
        return None

    card = state.resolving_supporter
    discard = state.other_discard
    hand_return = state.other_hand_return
    prize = state.other_prize
    if final_destination == "discard":
        discard = discard + (card,)
    elif final_destination == "hand":
        hand_return = hand_return + (card,)
    else:
        prize = prize + (card,)

    return replace(
        state,
        current_budget=ended,
        other_discard=discard,
        other_hand_return=hand_return,
        other_prize=prize,
        resolving_supporter=None,
        event=None,
    )
