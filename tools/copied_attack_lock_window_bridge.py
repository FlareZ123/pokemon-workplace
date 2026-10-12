"""Create an attack-applied turn restriction from a verified copied-body event.

Only complete lock-only or self-contained coin/choice-gated lock text is
accepted. Other effects require their own physical execution before any
whole-attack completeness claim.
"""
from __future__ import annotations

from dataclasses import dataclass

from attack_copy_kernel import Resolution
from attack_lock_whole_text_audit import AttackLockAudit
from attack_restriction_turn_windows import (
    AttackRestrictionWindow, create_attack_restriction_window,
)
from attack_source_scoped_restrictions import materialize_attack_restriction
from source_scoped_action_restrictions import SourceScopedActionRestriction


_HANDLED_GATE_EFFECTS = frozenset({"coin_flip", "player_choice"})


@dataclass(frozen=True)
class CopiedAttackLockApplication:
    body_event: str
    restriction: SourceScopedActionRestriction | None
    window: AttackRestrictionWindow | None


def create_copied_attack_lock_window(
    resolution: Resolution,
    audit: AttackLockAudit,
    *,
    source_player: str,
    other_player: str,
    coin_heads: bool | None = None,
    selected_dimensions: frozenset[str] | None = None,
) -> CopiedAttackLockApplication:
    """Materialize one source-verified copied hand lock after its body executed.

    The caller still owns actual attack legality, damage/effects, application
    immunity, and the subsequent turn scheduler. Those are deliberately not
    inferred from the presence of a copied-body event.
    """
    if audit.opaque_clauses:
        raise ValueError("copied attack has opaque source clauses")
    unhandled = set(audit.other_handlers) - _HANDLED_GATE_EFFECTS
    if unhandled:
        raise ValueError(
            f"copied attack needs other semantic handlers: {sorted(unhandled)}"
        )
    expected_event = f"body:{audit.attack_id}"
    if resolution.state.events.count(expected_event) != 1:
        raise ValueError("source copied body event was not executed exactly once")
    if not any(
        step.body_attack_id == audit.attack_id
        and step.selected_body_executed is None
        for step in resolution.trace
    ):
        raise ValueError("source copied body lacks an executed leaf trace")
    if source_player == other_player:
        raise ValueError("source and other player must differ")

    restriction = materialize_attack_restriction(
        audit.profile,
        coin_heads=coin_heads,
        selected_dimensions=selected_dimensions,
    )
    window = (
        create_attack_restriction_window(
            audit.profile, restriction,
            source_player=source_player,
            other_player=other_player,
        )
        if restriction is not None else None
    )
    return CopiedAttackLockApplication(expected_event, restriction, window)
