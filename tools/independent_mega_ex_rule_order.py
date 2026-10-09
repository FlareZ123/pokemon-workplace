from __future__ import annotations

from typing import Any

MEGA_RULE = (
    "Mega Evolution rule: When 1 of your Pokémon becomes a Mega Evolution "
    "Pokémon, your turn ends."
)
EX_RULE = (
    "Pokémon-EX rule: When a Pokémon-EX has been Knocked Out, "
    "your opponent takes 2 Prize cards."
)


def normalize_independent_mega_ex_rules(card: dict[str, Any]) -> dict[str, Any]:
    """Canonicalize only the two exact independent XY-era printed rule texts.

    Evolution ends the turn when that Pokémon becomes a Mega Evolution;
    EX Prize liability applies upon Knock Out. Both are continuous printed
    rule statements bound to different events, so their textual order
    does not change the legal event or outcome space. Unrelated rules
    are left in source order to preserve potentially sequential effects.
    """
    rules = card.get("rules")
    if (
        card.get("supertype") != "Pokémon"
        or not {"MEGA", "EX"}.issubset(set(card.get("subtypes") or ()))
        or rules != [EX_RULE, MEGA_RULE]
    ):
        return card

    normalized = dict(card)
    normalized["rules"] = [MEGA_RULE, EX_RULE]
    return normalized
