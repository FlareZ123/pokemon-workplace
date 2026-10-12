from __future__ import annotations

from copy import deepcopy
from typing import Any

BENCH_GUARD_RULE = (
    "As long as this Pokémon is on your Bench, prevent all damage done to "
    "this Pokémon by attacks (both yours and your opponent's)."
)
EX_TWO_PRIZE_RULE = (
    "Pokémon ex rule: When your Pokémon ex is Knocked Out, "
    "your opponent takes 2 Prize cards."
)
TERA_DUPLICATE_RULE = "Tera: " + BENCH_GUARD_RULE
CORRECT_RULES = [BENCH_GUARD_RULE, EX_TWO_PRIZE_RULE]
DUPLICATED_RULES = [BENCH_GUARD_RULE, EX_TWO_PRIZE_RULE, TERA_DUPLICATE_RULE]

AUDITED_DUPLICATE_TERA_PRINTS = frozenset(
    """sv5-60 sv5-108 sv5-190 sv5-194 sv6-25 sv6-29 sv6-40 sv6-64 sv6-106 sv6-112 sv6-130 sv6-190 sv6-191 sv6-192 sv6-194 sv6-198 sv6-199 sv6-200 sv6-211 sv6-212 sv6-213 sv6-214 sv6-215 sv6-221""".split()
)


def normalize_verified_tera_duplicate_rules(card: dict[str, Any]) -> dict[str, Any]:
    """Remove a duplicated Tera Bench effect on exactly 24 audited prints."""
    card_id = card.get("id")
    if card_id not in AUDITED_DUPLICATE_TERA_PRINTS:
        return card

    if (
        card.get("supertype") != "Pokémon"
        or not {"Tera", "ex"}.issubset(set(card.get("subtypes") or ()))
    ):
        raise ValueError(f"Audited Tera ex identity changed: {card_id}")

    rules = card.get("rules")
    if rules == CORRECT_RULES:
        return card
    if rules != DUPLICATED_RULES:
        raise ValueError(f"Unexpected Tera ex Bench rule text: {card_id}")

    normalized = deepcopy(card)
    normalized["rules"] = list(CORRECT_RULES)
    return normalized
