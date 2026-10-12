from __future__ import annotations

from typing import Any

from tools.verified_stage_metadata_repairs import (
    KNOWN_STAGE_REPAIRS,
    normalize_verified_stage_metadata,
)
from tools.verified_tera_metadata_repairs import (
    CARD_ID as TERAPAGOS_TERA_PRINT_ID,
    normalize_verified_tera_metadata,
)
from tools.verified_mega_prize_rules import (
    AUDITED_DUPLICATED_RULE_PRINTS,
    normalize_verified_mega_prize_rules,
)
from tools.verified_tera_duplicate_rules import (
    AUDITED_DUPLICATE_TERA_PRINTS,
    normalize_verified_tera_duplicate_rules,
)

# Stable compatibility boundary: all audited corrections are applied with
# identical ordering in card identity, deck validation, and future consumers.
AUDITED_CARD_METADATA_IDS = frozenset(KNOWN_STAGE_REPAIRS) | frozenset(
    {TERAPAGOS_TERA_PRINT_ID}
) | AUDITED_DUPLICATED_RULE_PRINTS | AUDITED_DUPLICATE_TERA_PRINTS


def normalize_verified_card_metadata(card: dict[str, Any]) -> dict[str, Any]:
    """Apply exact-print, documented physical-card corrections.

    Source JSON remains immutable. Unrelated records are returned unchanged
    without an unnecessary deepcopy. Every correction has a source-text guard.
    """
    if card.get("id") not in AUDITED_CARD_METADATA_IDS:
        return card

    corrected = normalize_verified_stage_metadata(card)
    corrected = normalize_verified_tera_metadata(corrected)
    corrected = normalize_verified_mega_prize_rules(corrected)
    return normalize_verified_tera_duplicate_rules(corrected)
