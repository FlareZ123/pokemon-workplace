from __future__ import annotations

from typing import Any

from tools.attack_empty_field_normalization import normalize_empty_attack_fields
from tools.basic_switch_rule_semantics import normalize_basic_switch_wording
from tools.independent_mega_ex_rule_order import normalize_independent_mega_ex_rules
from tools.build_expanded_legality_baseline import gameplay_fingerprint
from tools.official_print_errata import normalize_print_specific_errata
from tools.tool_category_normalization import normalize_legacy_tool_category
from tools.trainer_boilerplate_normalization import normalize_trainer_boilerplate
from tools.trainer_rule_semantics import normalize_rule_grounded_trainer_semantics
from tools.copycat_number_wording import normalize_copycat_count_wording


def normalize_current_card_semantics(card: dict[str, Any]) -> dict[str, Any]:
    """Apply authoritative repository normalizations for current card meaning."""

    normalized = normalize_print_specific_errata(card)
    normalized = normalize_empty_attack_fields(normalized)
    normalized = normalize_legacy_tool_category(normalized)
    normalized = normalize_trainer_boilerplate(normalized)
    normalized = normalize_rule_grounded_trainer_semantics(normalized)
    normalized = normalize_copycat_count_wording(normalized)
    normalized = normalize_independent_mega_ex_rules(normalized)
    normalized = normalize_basic_switch_wording(normalized)
    return normalized


def current_semantic_fingerprint(card: dict[str, Any]) -> str:
    return gameplay_fingerprint(normalize_current_card_semantics(card))
