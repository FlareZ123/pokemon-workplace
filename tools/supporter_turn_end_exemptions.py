"""Turn-ending Supporter effects and exact active-Ability exceptions.

Some Supporters end their controller's turn after resolving. Two printed
Expanded-legal active-Pokemon Abilities prevent the closure for a named card:
- Metagross sm7-95 / Extend: Steven's Resolve
- Alcremie swsh9-71, swsh9tg-TG08 / Additional Order: Café Master.

This bridge owns Supporter-quota and turn-closure semantics only. Call after
a legal Supporter card's underlying effect has been resolved; physical card
payment, source restrictions and full board effects are handled upstream.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

from board_object_kernel import BoardState
from build_expanded_legality_baseline import classify_effective_legality
from turn_action_budget import TurnAction, TurnActionBudget


_EXEMPTIONS = {
    "Steven's Resolve": {
        "sm7-95": (
            "Extend",
            "As long as this Pokémon is your Active Pokémon, your turn "
            "does not end when you play Steven's Resolve.",
        )
    },
    "Café Master": {
        "swsh9-71": (
            "Additional Order",
            "As long as this Pokémon is in the Active Spot, your turn "
            "does not end when you use Café Master.",
        ),
        "swsh9tg-TG08": (
            "Additional Order",
            "As long as this Pokémon is in the Active Spot, your turn "
            "does not end when you use Café Master.",
        ),
    },
}


def _card(resources: Path, print_id: str) -> dict:
    stem = print_id.split("-")[0]
    cards = json.loads(
        (resources / "cards" / "en" / f"{stem}.json")
        .read_text(encoding="utf-8")
    )
    card = next(row for row in cards if row["id"] == print_id)
    if classify_effective_legality(card)[0] != "Legal":
        raise ValueError("source print is not legal in bundled Expanded format")
    return card


@dataclass(frozen=True)
class SupporterTurnOutcome:
    budget: TurnActionBudget
    supporter_print_id: str
    supporter_name: str
    printed_ends_turn: bool
    exempted_by_active_ability: bool
    exemption_source_print_id: str | None

    @property
    def ended_by_supporter(self) -> bool:
        return self.printed_ends_turn and not self.exempted_by_active_ability


def resolve_completed_supporter_turn(
    resources: Path,
    *,
    supporter_print_id: str,
    player_board: BoardState,
    budget: TurnActionBudget,
    suppressed_ability_object_ids: frozenset[str] = frozenset(),
) -> SupporterTurnOutcome | None:
    """Apply Supporter bandwidth and any printed end-of-turn consequence.

    The caller has verified the Supporter was legally executable, finished
    its primary effect, and passed the resulting physical board. This
    transition is an atomic quota/turn-end projection of that completion.
    """
    supporter = _card(resources, supporter_print_id)
    if supporter["supertype"] != "Trainer" or "Supporter" not in (
        supporter.get("subtypes") or ()
    ):
        raise ValueError("selected card is not a Supporter")

    spent = budget.consume(TurnAction.SUPPORTER)
    if spent is None:
        return None

    printed_end = any(
        rule.strip().endswith("Your turn ends.")
        for rule in supporter.get("rules") or ()
    )
    active = player_board.get(player_board.active_id)
    exemption_source: str | None = None
    if (
        printed_end
        and active.abilities_enabled
        and active.object_id not in suppressed_ability_object_ids
        and active.print_id in _EXEMPTIONS.get(supporter["name"], {})
    ):
        required_name, required_text = _EXEMPTIONS[supporter["name"]][active.print_id]
        active_print = _card(resources, active.print_id)
        if active.card_name == active_print["name"] and any(
            ability["name"] == required_name and ability["text"] == required_text
            for ability in active_print.get("abilities") or ()
        ):
            exemption_source = active.print_id

    if printed_end and exemption_source is None:
        closed = spent.consume(TurnAction.END_TURN)
        if closed is None:
            raise AssertionError("resolved Supporter failed to end the turn")
        spent = closed

    return SupporterTurnOutcome(
        budget=spent,
        supporter_print_id=supporter_print_id,
        supporter_name=supporter["name"],
        printed_ends_turn=printed_end,
        exempted_by_active_ability=exemption_source is not None,
        exemption_source_print_id=exemption_source,
    )
