"""Execute a directly declared compiled copy attack through its outer control."""

from __future__ import annotations

from dataclasses import dataclass, replace

from attack_copy_kernel import (
    AttackDef,
    ChoicePolicy,
    CopiedBodyGatePolicy,
    Resolution,
    SourceChoicePolicy,
    State,
    resolve_attack,
)
from attack_copy_kernel_compiler import CompiledCopyAttack
from attack_copy_outer_control import ControlOutcome, evaluate_outer_control


@dataclass(frozen=True)
class ControlledCopyExecution:
    outcome: ControlOutcome
    resolution: Resolution | None


class UnresolvedCopiedBodyControl(RuntimeError):
    pass


def copied_body_gate_policy(
    compiled_rows: tuple[CompiledCopyAttack, ...],
    *,
    actor_hand_size: int | None = None,
    opponent_prizes_remaining: int | None = None,
    coin_heads_by_attack_id: dict[str, bool] | None = None,
) -> CopiedBodyGatePolicy:
    """Build a gate for controlled attacks reached as selected copied bodies."""

    controls = {
        row.guarded_definition.attack_id: row.outer_control
        for row in compiled_rows
        if row.guarded_definition is not None and row.outer_control is not None
    }
    coin_outcomes = coin_heads_by_attack_id or {}

    def gate(body: AttackDef, _state: State) -> bool:
        control = controls.get(body.attack_id)
        if control is None:
            return True
        outcome = evaluate_outer_control(
            control,
            actor_hand_size=actor_hand_size,
            opponent_prizes_remaining=opponent_prizes_remaining,
            coin_heads=coin_outcomes.get(body.attack_id),
            invocation_mode="copied_body",
        )
        if outcome == "random_outcome_required":
            raise UnresolvedCopiedBodyControl(
                f"missing coin outcome for copied body {body.attack_id}"
            )
        if outcome == "declaration_illegal":
            raise AssertionError(
                "copied-body evaluation cannot reject direct declaration"
            )
        return outcome == "proceed"

    return gate


def resolve_declared_compiled_copy_attack(
    compiled: CompiledCopyAttack,
    *,
    actor_player: str,
    actor_card_id: str,
    attacks: dict[str, AttackDef],
    state: State,
    choose: ChoicePolicy,
    choose_opponent: ChoicePolicy | None = None,
    choose_source: SourceChoicePolicy | None = None,
    actor_hand_size: int | None = None,
    opponent_prizes_remaining: int | None = None,
    coin_heads: bool | None = None,
) -> ControlledCopyExecution:
    """Resolve one directly declared copy attack with its compiled outer control.

    Declaration gates return before the core attack resolver. Body gates that
    fail still resolve the declared attack and record its attack history, while
    suppressing the conditional copy branch. Random body gates require the
    caller to supply an explicit outcome.

    This adapter governs the directly declared attack. Nested controlled bodies
    can be handled by passing `copied_body_gate_policy()` to the core kernel in
    workflows that assemble guarded definitions as legal copy targets.
    """

    definition = compiled.definition
    if definition is None:
        definition = compiled.guarded_definition
    if definition is None:
        raise ValueError("compiled copy attack has no executable definition")

    outcome = evaluate_outer_control(
        compiled.outer_control,
        actor_hand_size=actor_hand_size,
        opponent_prizes_remaining=opponent_prizes_remaining,
        coin_heads=coin_heads,
    )
    if outcome in {"declaration_illegal", "random_outcome_required"}:
        return ControlledCopyExecution(outcome, None)

    root = definition
    if outcome == "resolve_without_copy":
        root = replace(root, copy_selector=None)

    executable_attacks = dict(attacks)
    executable_attacks[root.attack_id] = root
    resolution = resolve_attack(
        actor_player=actor_player,
        actor_card_id=actor_card_id,
        declared_attack_id=root.attack_id,
        attacks=executable_attacks,
        state=state,
        choose=choose,
        choose_opponent=choose_opponent,
        choose_source=choose_source,
    )
    return ControlledCopyExecution(outcome, resolution)
