"""Attack-triggered turn ending from Energy cards attached from hand.

Legal Slakoth sm11-167 / Lazy Howl and Hypno sv6pt5-17 / Daydream:

"During your opponent's next turn, if they attach an Energy card from
their hand to the Defending Pokémon, their turn ends."

The effect binds to the attacked physical Pokémon. This kernel reacts to
committed hand-origin EnergyAttachmentEvents after the attachment transition,
including Effect-channel attachments, and preserves the ordinary/manual
attachment history already recorded by the physical transition.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
import json

from board_object_kernel import BoardState
from build_expanded_legality_baseline import classify_effective_legality
from energy_hand_attachment_events import (
    EnergyAttachmentEvent,
    EnergyAttachmentState,
)
from turn_action_budget import TurnAction


_TEXT = (
    "During your opponent's next turn, if they attach an Energy card "
    "from their hand to the Defending Pokémon, their turn ends."
)
_SUPPORTED = {
    "sm11-167": "Lazy Howl",
    "sv6pt5-17": "Daydream",
}


@dataclass(frozen=True)
class HandAttachmentTurnEndWindow:
    source_print_id: str
    source_player: str
    affected_player: str
    target_object_id: str
    target_card_name: str
    phase: str = "waiting"
    target_effect_live: bool = True

    def __post_init__(self) -> None:
        if self.source_print_id not in _SUPPORTED:
            raise ValueError("unsupported printed hand-attachment reaction")
        if not self.source_player or not self.affected_player:
            raise ValueError("player identifiers must be nonempty")
        if self.source_player == self.affected_player:
            raise ValueError("effect source and affected player must differ")
        if not self.target_object_id or not self.target_card_name:
            raise ValueError("target identity must be nonempty")
        if self.phase not in {"waiting", "active", "expired"}:
            raise ValueError("unknown attack effect phase")

    def begin_turn(self, player: str) -> "HandAttachmentTurnEndWindow":
        if player not in {self.source_player, self.affected_player}:
            raise ValueError("turn belongs to neither participant")
        if self.phase == "waiting" and player == self.affected_player:
            return replace(self, phase="active")
        return self

    def end_turn(self, player: str) -> "HandAttachmentTurnEndWindow":
        if player not in {self.source_player, self.affected_player}:
            raise ValueError("turn belongs to neither participant")
        if self.phase == "active" and player == self.affected_player:
            return replace(self, phase="expired")
        return self

    def remove_attack_effects(self) -> "HandAttachmentTurnEndWindow":
        return replace(self, phase="expired")

    def advance_target_binding(
        self, before: BoardState, after: BoardState
    ) -> "HandAttachmentTurnEndWindow":
        """Cancel if the originally Defending Pokémon leaves Active or evolves."""
        if not self.target_effect_live:
            return self
        original = before.get(self.target_object_id)
        if original.card_name != self.target_card_name:
            raise ValueError("stale before-board target identity")
        try:
            current = after.get(self.target_object_id)
        except KeyError:
            return replace(self, target_effect_live=False)

        left_active = (
            before.active_id == self.target_object_id
            and after.active_id != self.target_object_id
        )
        evolved_or_replaced = current.card_name != self.target_card_name
        if left_active or evolved_or_replaced:
            return replace(self, target_effect_live=False)
        return self


@dataclass(frozen=True)
class AttachmentTurnEndOutcome:
    state: EnergyAttachmentState
    window: HandAttachmentTurnEndWindow
    trigger: EnergyAttachmentEvent | None

    @property
    def ended_by_attachment(self) -> bool:
        return self.trigger is not None


def from_printed_attack(
    resources: Path,
    *,
    print_id: str,
    source_player: str,
    affected_player: str,
    target_board: BoardState,
) -> HandAttachmentTurnEndWindow:
    """Validate exact Expanded source print and bind its original target."""
    if print_id not in _SUPPORTED:
        raise ValueError("unsupported attachment reaction source")
    cards = json.loads(
        (resources / "cards" / "en" / f"{print_id.split('-')[0]}.json")
        .read_text(encoding="utf-8")
    )
    card = next(row for row in cards if row["id"] == print_id)
    if classify_effective_legality(card)[0] != "Legal":
        raise ValueError("attack print is not legal in bundled Expanded snapshot")
    attacks = [attack for attack in card["attacks"]
               if attack["name"] == _SUPPORTED[print_id]]
    if len(attacks) != 1 or attacks[0]["text"] != _TEXT:
        raise ValueError("attack text changed, re-audit reaction semantics")

    target = target_board.get(target_board.active_id)
    return HandAttachmentTurnEndWindow(
        source_print_id=print_id,
        source_player=source_player,
        affected_player=affected_player,
        target_object_id=target.object_id,
        target_card_name=target.card_name,
    )


def resolve_committed_hand_attachments(
    previous: EnergyAttachmentState,
    committed: EnergyAttachmentState,
    window: HandAttachmentTurnEndWindow,
) -> AttachmentTurnEndOutcome:
    """React to new hand-origin events after an atomic attachment action.

    Previous events must be an exact prefix of committed events, preventing
    the same old event from ending another turn. The caller separately owns
    advancement of this temporal/physical target binding.
    """
    n = len(previous.events)
    if committed.events[:n] != previous.events:
        raise ValueError("attachment journal must extend previous events")

    trigger = next(
        (
            event for event in committed.events[n:]
            if window.phase == "active"
            and window.target_effect_live
            and event.source_zone == "hand"
            and event.player == window.affected_player
            and event.target_id == window.target_object_id
        ),
        None,
    )
    if trigger is None:
        return AttachmentTurnEndOutcome(committed, window, None)

    budget = committed.budget
    if not budget.turn_ended:
        ended = budget.consume(TurnAction.END_TURN)
        if ended is None:
            raise AssertionError("active turn failed to close after trigger")
        committed = replace(committed, budget=ended)
    return AttachmentTurnEndOutcome(committed, window, trigger)
