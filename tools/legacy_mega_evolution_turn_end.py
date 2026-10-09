"""Print-specific legacy Mega Evolution / Primal Reversion turn boundary.

The XY-era Mega Evolution Pokémon-EX rule can end a player's turn on
evolution. A matching, effect-enabled Spirit Link Tool prevents the ending.
The newer Mega Evolution ex Rule instead awards three Prizes on Knock Out
and does not cause evolution to end the turn.

The upstream board transition is responsible for checking ordinary
evolution timing, acting upon a physical card, and retaining attachments.
This adapter checks print identity, evolution origin, exact attached Tool
text, and the canonical turn budget after that physical evolution.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

from board_object_kernel import BoardState
from build_expanded_legality_baseline import classify_effective_legality
from turn_action_budget import TurnAction, TurnActionBudget


_LEGACY_MEGA_RULE = (
    "Mega Evolution rule: When 1 of your Pokémon becomes a Mega Evolution "
    "Pokémon, your turn ends."
)


def _print(resources: Path, print_id: str) -> dict:
    set_id = print_id.split("-")[0]
    cards = json.loads(
        (resources / "cards" / "en" / f"{set_id}.json")
        .read_text(encoding="utf-8")
    )
    card = next(x for x in cards if x["id"] == print_id)
    if classify_effective_legality(card)[0] != "Legal":
        raise ValueError("evolving print or Tool is unavailable in Expanded")
    return card


@dataclass(frozen=True)
class LegacyMegaTurnOutcome:
    budget: TurnActionBudget
    new_print_id: str
    old_name: str
    new_name: str
    legacy_rule: str | None
    prevented_by_spirit_link: bool
    spirit_link_print_id: str | None

    @property
    def ended_by_evolution(self) -> bool:
        return self.legacy_rule is not None and not self.prevented_by_spirit_link


def resolve_evolution_turn_boundary(
    resources: Path,
    *,
    before: BoardState,
    after: BoardState,
    object_id: str,
    budget: TurnActionBudget,
) -> LegacyMegaTurnOutcome:
    """Resolve an already-performed single physical evolution's turn ending."""
    if budget.turn_ended:
        raise ValueError("cannot evolve after the turn has already ended")
    if before.active_id != after.active_id or before.bench_ids != after.bench_ids:
        raise ValueError("evolution bridge requires unchanged board positioning")
    before.validate()
    after.validate()
    old = before.get(object_id)
    current = after.get(object_id)
    if current.print_id is None:
        raise ValueError("evolved Pokémon requires an exact print ID")
    card = _print(resources, current.print_id)
    if card.get("supertype") != "Pokémon":
        raise ValueError("target is not an Evolution Pokémon")
    if card.get("evolvesFrom") != old.card_name:
        raise ValueError("printed evolution origin does not match previous Pokémon")
    if current.card_name != card["name"] or current.card_name == old.card_name:
        raise ValueError("physical new card identity mismatches evolving print")
    if current.tool != old.tool or current.energy != old.energy:
        raise ValueError("ordinary evolution must preserve attached cards")
    if current.damage_counters != old.damage_counters:
        raise ValueError("ordinary evolution must preserve damage counters")

    legacy_rule: str | None = None
    rules = card.get("rules") or ()
    if _LEGACY_MEGA_RULE in rules:
        legacy_rule = "mega_evolution"
    elif (
        f"Primal Reversion rule: When 1 of your Pokémon becomes "
        f"{card['name']}, your turn ends."
    ) in rules:
        legacy_rule = "primal_reversion"

    spirit_print: str | None = None
    prevented = False
    if legacy_rule and current.tool and current.pokemon_state.tool_effect_enabled:
        if current.tool.print_id is not None:
            tool = _print(resources, current.tool.print_id)
            if (
                tool["name"] == current.tool.card_name
                and tool.get("supertype") == "Trainer"
                and "Pokémon Tool" in (tool.get("subtypes") or ())
                and (
                    f"Your turn does not end if the Pokémon this card is "
                    f"attached to becomes {card['name']}."
                ) in (tool.get("rules") or ())
            ):
                spirit_print = current.tool.print_id
                prevented = True

    next_budget = budget
    if legacy_rule and not prevented:
        consumed = budget.consume(TurnAction.END_TURN)
        if consumed is None:
            raise AssertionError("available turn failed to close on evolution")
        next_budget = consumed

    return LegacyMegaTurnOutcome(
        budget=next_budget,
        new_print_id=current.print_id,
        old_name=old.card_name,
        new_name=current.card_name,
        legacy_rule=legacy_rule,
        prevented_by_spirit_link=prevented,
        spirit_link_print_id=spirit_print,
    )
