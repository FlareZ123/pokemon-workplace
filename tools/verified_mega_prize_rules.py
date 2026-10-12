from __future__ import annotations

from copy import deepcopy
from typing import Any

EX_TWO_PRIZE_RULE = (
    "Pokémon ex rule: When your Pokémon ex is Knocked Out, "
    "your opponent takes 2 Prize cards."
)
MEGA_THREE_PRIZE_RULE = (
    "Mega Evolution ex Rule: When your Mega Evolution Pokémon ex is Knocked Out, "
    "your opponent takes 3 Prize cards."
)

# Audited exact printing IDs in Ascended Heroes and Perfect Order.
# The source archive's implicit ordinary-ex rule does not appear in the
# physical Mega Evolution ex Rule Box on audited physical prints.
AUDITED_DUPLICATED_RULE_PRINTS = frozenset(
    """me2pt5-10 me2pt5-22 me2pt5-31 me2pt5-43 me2pt5-47 me2pt5-61 me2pt5-89 me2pt5-113 me2pt5-116 me2pt5-125 me2pt5-135 me2pt5-152 me2pt5-172 me2pt5-253 me2pt5-265 me2pt5-266 me2pt5-267 me2pt5-268 me2pt5-269 me2pt5-270 me2pt5-271 me2pt5-272 me2pt5-273 me2pt5-274 me2pt5-275 me2pt5-278 me2pt5-282 me2pt5-283 me2pt5-284 me2pt5-285 me2pt5-290 me2pt5-294 me2pt5-295 me3-21 me3-31 me3-47 me3-55 me3-102 me3-103 me3-104 me3-106 me3-118 me3-119 me3-120 me3-124""".split()
)


def normalize_verified_mega_prize_rules(card: dict[str, Any]) -> dict[str, Any]:
    """Remove the extra ordinary-ex rule only on the audited Mega ex prints.

    Preserve original source data and accept an already-corrected print.
    Reject unexpected changes to any audited physical print.
    """
    card_id = card.get("id")
    if card_id not in AUDITED_DUPLICATED_RULE_PRINTS:
        return card

    if (
        not isinstance(card.get("name"), str)
        or not card["name"].startswith("Mega ")
        or not card["name"].endswith(" ex")
        or card.get("supertype") != "Pokémon"
        or not {"MEGA", "ex"}.issubset(set(card.get("subtypes") or ()))
    ):
        raise ValueError(f"Audited Mega ex identity changed: {card_id}")

    rules = card.get("rules")
    if rules == [MEGA_THREE_PRIZE_RULE]:
        return card
    if rules != [EX_TWO_PRIZE_RULE, MEGA_THREE_PRIZE_RULE]:
        raise ValueError(f"Unexpected Mega ex Rule Box text: {card_id}")

    normalized = deepcopy(card)
    normalized["rules"] = [MEGA_THREE_PRIZE_RULE]
    return normalized
