from __future__ import annotations

from copy import deepcopy
from typing import Any

# The Tournament Handbook certifies Copycat TRR 83 -> CES 127 as
# functionally identical. These two additional historical Supporter prints
# describe the same count, shuffle, and draw transition as TRR 83.
SOURCE_IDS = frozenset({"col1-77", "hgss1-90"})
SOURCE_TEXT = (
    "Shuffle your hand into your deck. Then, draw a number of cards "
    "equal to the number of cards in your opponent's hand."
)
REFERENCE_TEXT = (
    "Shuffle your hand into your deck. Then, count the number of cards "
    "in your opponent's hand and draw that many cards."
)


def normalize_copycat_count_wording(card: dict[str, Any]) -> dict[str, Any]:
    """Rewrite only two audited Copycat print-specific semantic synonyms.

    The card-ID and complete effect-text guards prevent accidental
    equivalence propagation to other historical printings or Trainer names.
    """
    normalized = deepcopy(card)
    if normalized.get("id") not in SOURCE_IDS:
        return normalized
    if normalized.get("name") != "Copycat":
        raise ValueError("Audited Copycat source ID now has a different name")
    if normalized.get("supertype") != "Trainer" or "Supporter" not in (
        normalized.get("subtypes") or []
    ):
        raise ValueError("Audited Copycat source lost its Supporter classification")
    rules = list(normalized.get("rules") or [])
    if rules.count(REFERENCE_TEXT) == 1 and SOURCE_TEXT not in rules:
        return normalized
    if rules.count(SOURCE_TEXT) != 1:
        raise ValueError("Audited Copycat source text changed")
    normalized["rules"] = [
        REFERENCE_TEXT if text == SOURCE_TEXT else text for text in rules
    ]
    return normalized
