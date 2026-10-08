"""Inventory complete versus residual attack text in the simple copy compiler.

This classifies exact text clauses only. A recognized text signature identifies
semantic handlers still needed by downstream executors. It does not certify
Energy-payment feasibility, attack legality, live modifiers, or game state.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from board_position_state import BoardState
from attack_copy_physical_ko_bridge import PhysicalBoardEventProgram
from attack_status_text_contracts import parse_exact_attack_status_text
from energy_disruption_profile_compiler import (
    parse_exact_attack_energy_disruption_text,
)
from healing_profile_compiler import parse_exact_attack_healing_text
from position_effect_profile_compiler import parse_exact_attack_position_text
from simple_attack_board_semantics import (
    CompiledAttackBoardSemantics,
    compile_legal_index,
    materialize_opponent_board_program,
)


_GX_RULE = "(You can't use more than 1 GX attack in a game.)"
_EXACT_TYPE_CLAUSES = frozenset((
    "This attack's damage isn't affected by Weakness or Resistance.",
    "This attack's damage isn't affected by Weakness.",
    "This attack's damage isn't affected by Resistance.",
))
_EXACT_EFFECT_CLAUSES = frozenset((
    "This attack's damage isn't affected by any effects on your opponent's Active Pokémon.",
    "This attack's damage isn't affected by any effects on the Defending Pokémon.",
))
_EXACT_EXTRA_TURN = frozenset((
    "Take another turn after this one.",
    "Take another turn after this one. (Skip the between-turns step.)",
    "Take another turn after this one. (Skip Pokémon Checkup.)",
))


@dataclass(frozen=True)
class AttackTextCoverage:
    attack_id: str
    kind: str
    printed_fixed_supported: bool
    requires_handlers: tuple[str, ...]
    raw_text: str


def classify_attack_text(
    row: CompiledAttackBoardSemantics,
) -> AttackTextCoverage:
    """Classify one full normalized text, without clause-fragment optimism."""
    if row.fixed_damage is None:
        return AttackTextCoverage(
            row.attack_id, "unsupported_printed_damage", False,
            ("printed_damage_expression",), row.raw_text,
        )

    original = row.raw_text
    core = original
    if core.endswith(" " + _GX_RULE):
        core = core[:-(len(_GX_RULE) + 1)]
    elif core == _GX_RULE:
        core = ""
    if not core:
        kind = "plain_fixed_or_gx_rule"
        handlers = ()
    elif row.counter_effect is not None:
        kind = "exact_damage_counter_clause"
        handlers = ("counter_placement",)
    elif core in _EXACT_TYPE_CLAUSES:
        kind = "exact_type_modifier_bypass"
        handlers = ("typed_damage",)
    elif core in _EXACT_EFFECT_CLAUSES:
        kind = "exact_defender_effect_bypass"
        handlers = ("defender_effects",)
    elif core in _EXACT_EXTRA_TURN:
        kind = "exact_extra_turn"
        handlers = ("turn_boundary",)
    elif (status := parse_exact_attack_status_text(core)) is not None:
        kind = "exact_special_condition"
        handlers = (
            ("status_condition", "coin_flip")
            if status[1] is not None else ("status_condition",)
        )
    elif (position := parse_exact_attack_position_text(core)) is not None:
        kind = "exact_position_effect"
        handlers = ("position_effect",)
        if position.coin_heads_required:
            handlers += ("coin_flip",)
        if position.optional:
            handlers += ("optional_choice",)
    elif parse_exact_attack_healing_text(core) is not None:
        kind = "exact_self_healing"
        handlers = ("healing",)
    elif (
        disruption := parse_exact_attack_energy_disruption_text(core)
    ) is not None:
        kind = "exact_energy_disruption"
        handlers = ("energy_disruption",)
        if disruption[2]:
            handlers += ("coin_flip",)
    else:
        kind = "uncompiled_effect_text"
        handlers = ("source_specific_effects",)

    if original.endswith(_GX_RULE) or original == _GX_RULE:
        handlers += ("gx_budget",)

    return AttackTextCoverage(
        row.attack_id, kind, True, handlers, original,
    )


def build_coverage(resources_root: Path) -> dict:
    index = compile_legal_index(resources_root)
    compiled = tuple(row for entries in index.values() for row in entries)
    coverage = tuple(classify_attack_text(row) for row in compiled)
    counts = Counter(row.kind for row in coverage)
    unresolved = tuple(
        (source, result)
        for source, result in zip(compiled, coverage)
        if result.kind == "uncompiled_effect_text"
    )
    unguarded = tuple(
        (source, result)
        for source, result in unresolved
        if not (
            source.has_uncompiled_damage_text
            or source.has_uncompiled_knockout_text
            or source.has_uncompiled_attack_gate
        )
    )
    examples = {}
    for source, result in zip(compiled, coverage):
        examples.setdefault(result.kind, {
            "card_id": source.card_id,
            "card_name": source.card_name,
            "attack_name": source.attack_name,
            "printed_damage": source.raw_damage,
            "attack_text": source.raw_text,
        })
    return {
        "rows": coverage,
        "total": len(coverage),
        "counts": dict(sorted(counts.items())),
        "uncompiled_unguarded": len(unguarded),
        "guarded_uncompiled": len(unresolved) - len(unguarded),
        "examples": examples,
    }


def materialize_damage_only_verified(
    row: CompiledAttackBoardSemantics,
    board: BoardState,
    *,
    counter_allocation: tuple[tuple[str, int], ...] = (),
) -> PhysicalBoardEventProgram:
    """Only accept source text whose entire board effect this path handles.

    This conservative entry point is for damage-only board replays. It
    excludes GX budget, type bypass, extra turns, defender-effect bypass,
    and any unresolved attack text that needs a different execution layer.
    """
    classified = classify_attack_text(row)
    if classified.kind not in {
        "plain_fixed_or_gx_rule", "exact_damage_counter_clause"
    } or "gx_budget" in classified.requires_handlers:
        raise ValueError(
            f"attack requires additional semantic handlers: {row.attack_id}"
        )
    return materialize_opponent_board_program(
        row, board, counter_allocation=counter_allocation,
    )
