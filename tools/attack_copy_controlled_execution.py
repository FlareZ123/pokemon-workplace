"""Execute a directly declared compiled copy attack through its outer control."""

from __future__ import annotations

from dataclasses import dataclass, replace

from attack_copy_kernel import (
    AttackDef,
    ChoicePolicy,
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

    This adapter intentionally governs only the directly declared attack.
    Control semantics encountered through nested copied bodies remain a separate
    research question.
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
