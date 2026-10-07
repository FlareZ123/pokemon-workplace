from __future__ import annotations

from typing import Any

from tools.build_expanded_legality_baseline import gameplay_fingerprint
from tools.official_print_errata import normalize_print_specific_errata
from tools.tool_category_normalization import normalize_legacy_tool_category


def normalize_current_card_semantics(card: dict[str, Any]) -> dict[str, Any]:
    """Apply authoritative repository normalizations for current card meaning."""

    normalized = normalize_print_specific_errata(card)
    normalized = normalize_legacy_tool_category(normalized)
    return normalized


def current_semantic_fingerprint(card: dict[str, Any]) -> str:
    return gameplay_fingerprint(normalize_current_card_semantics(card))
