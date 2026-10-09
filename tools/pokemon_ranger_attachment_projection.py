"""Pokémon Ranger removes both beneficial and adverse attack-granted permissions.

This local projection covers two concrete source effects:
- Dragonair sm1-95 / Dragon's Wish (unbounded next-turn manual Energy)
- Slakoth sm11-167 Lazy Howl or Hypno sv6pt5-17 Daydream (end next
  turn on attaching Energy from hand to originally Defending Pokémon)

Pokémon Ranger xy11-104 says "Remove all effects of attacks on each player
and his or her Pokémon." Its Supporter use also consumes turn bandwidth.
A full physical Supporter executor must validate hand ownership, locks and
card displacement before calling this projection.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
import json

from build_expanded_legality_baseline import classify_effective_legality
from energy_hand_attachment_events import EnergyAttachmentState
from hand_attachment_turn_end import HandAttachmentTurnEndWindow
from next_turn_attachment_window import NextTurnAttachmentWindow
from turn_action_budget import TurnAction


_RANGER_PRINT = "xy11-104"
_REMOVAL_TEXT = "Remove all effects of attacks on each player and his or her Pokémon."


@dataclass(frozen=True)
class RangerAttachmentProjection:
    state: EnergyAttachmentState
    manual_permission: NextTurnAttachmentWindow
    reactive_window: HandAttachmentTurnEndWindow


def validate_printed_ranger(resources: Path) -> None:
    """Audit text and legal source print of the Supporter before execution."""
    cards = json.loads(
        (resources / "cards" / "en" / "xy11.json").read_text(encoding="utf-8")
    )
    ranger = next(row for row in cards if row["id"] == _RANGER_PRINT)
    if classify_effective_legality(ranger)[0] != "Legal":
        raise ValueError("Pokémon Ranger is not legal in this Expanded snapshot")
    if ranger["name"] != "Pokémon Ranger" or "Supporter" not in ranger["subtypes"]:
        raise ValueError("source is no longer a Pokémon Ranger Supporter")
    if _REMOVAL_TEXT not in (ranger.get("rules") or ()):
        raise ValueError("Ranger printed effect changed; audit projection")


def play_ranger_attachment_projection(
    state: EnergyAttachmentState,
    *,
    manual_permission: NextTurnAttachmentWindow,
    reactive_window: HandAttachmentTurnEndWindow,
) -> RangerAttachmentProjection | None:
    """Consume an available Supporter, removing both source attack effects.

    This validates the turn/Supporter budget and the two affected windows.
    It does not materialize the physical Pokémon Ranger card itself.
    """
    wish_live = bool(manual_permission.pending_for or manual_permission.active_for)
    reaction_live = (
        reactive_window.phase != "expired"
        and reactive_window.target_effect_live
    )
    if not wish_live and not reaction_live:
        return None

    used = state.budget.consume(TurnAction.SUPPORTER)
    if used is None:
        return None

    return RangerAttachmentProjection(
        state=replace(state, budget=used),
        manual_permission=manual_permission.remove_attack_effects(),
        reactive_window=reactive_window.remove_attack_effects(),
    )
