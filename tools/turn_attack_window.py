"""Attack-phase continuation over the shared turn-action budget.

The ordinary Pokemon TCG turn closes after one attack. Some card text changes
that boundary, such as Omega Barrage allowing the same Pokemon to attack twice.
This layer keeps ordinary action quotas separate from the attack continuation
window so a second attack does not reopen Supporter, Stadium, attachment, or
Retreat actions.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from turn_action_budget import TurnAction, TurnActionBudget


@dataclass(frozen=True)
class AttackPhaseBudget:
    attack_limit: int = 1
    attacks_used: int = 0
    attacker_object_id: str | None = None
    turn_ended: bool = False

    def __post_init__(self) -> None:
        if self.attack_limit < 0:
            raise ValueError("attack_limit must be non-negative")
        if not 0 <= self.attacks_used <= self.attack_limit:
            raise ValueError("attacks_used must be between zero and attack_limit")
        if self.attacks_used > 0 and self.attacker_object_id is None:
            raise ValueError("an attack history requires attacker_object_id")
        if self.attacker_object_id == "":
            raise ValueError("attacker_object_id must be non-empty when supplied")
        if self.attacks_used == self.attack_limit and self.attacks_used > 0 and not self.turn_ended:
            raise ValueError("exhausting the attack limit must end the turn")

    @property
    def ordinary_actions_open(self) -> bool:
        return not self.turn_ended and self.attacks_used == 0

    def can_attack(self, attacker_object_id: str) -> bool:
        if not attacker_object_id or self.turn_ended:
            return False
        if self.attacks_used >= self.attack_limit:
            return False
        if self.attacker_object_id is None:
            return True
        return self.attacker_object_id == attacker_object_id

    def consume_attack(self, attacker_object_id: str) -> "AttackPhaseBudget | None":
        if not self.can_attack(attacker_object_id):
            return None
        used = self.attacks_used + 1
        return AttackPhaseBudget(
            attack_limit=self.attack_limit,
            attacks_used=used,
            attacker_object_id=self.attacker_object_id or attacker_object_id,
            turn_ended=used >= self.attack_limit,
        )

    def end_turn(self) -> "AttackPhaseBudget | None":
        if self.turn_ended:
            return None
        return replace(self, turn_ended=True)


@dataclass(frozen=True)
class TurnExecutionWindow:
    action_budget: TurnActionBudget = TurnActionBudget()
    attack_phase: AttackPhaseBudget = AttackPhaseBudget()

    def __post_init__(self) -> None:
        if self.action_budget.turn_ended != self.attack_phase.turn_ended:
            raise ValueError("action and attack layers must agree on turn_ended")


def can_take_action(
    state: TurnExecutionWindow,
    action: TurnAction,
    *,
    attacker_object_id: str | None = None,
) -> bool:
    if state.attack_phase.turn_ended:
        return False
    if action is TurnAction.ATTACK:
        return (
            attacker_object_id is not None
            and state.attack_phase.can_attack(attacker_object_id)
        )
    if action is TurnAction.END_TURN:
        return True
    return state.attack_phase.ordinary_actions_open and state.action_budget.can(action)


def consume_action(
    state: TurnExecutionWindow,
    action: TurnAction,
    *,
    attacker_object_id: str | None = None,
) -> TurnExecutionWindow | None:
    if not can_take_action(state, action, attacker_object_id=attacker_object_id):
        return None

    if action is TurnAction.ATTACK:
        assert attacker_object_id is not None
        attack_phase = state.attack_phase.consume_attack(attacker_object_id)
        assert attack_phase is not None
        action_budget = state.action_budget
        if attack_phase.turn_ended:
            action_budget = replace(action_budget, turn_ended=True)
        return TurnExecutionWindow(action_budget, attack_phase)

    if action is TurnAction.END_TURN:
        action_budget = state.action_budget.consume(action)
        attack_phase = state.attack_phase.end_turn()
        assert action_budget is not None and attack_phase is not None
        return TurnExecutionWindow(action_budget, attack_phase)

    action_budget = state.action_budget.consume(action)
    assert action_budget is not None
    return TurnExecutionWindow(action_budget, state.attack_phase)


def fresh_turn(
    *,
    action_budget: TurnActionBudget | None = None,
    attack_limit: int = 1,
) -> TurnExecutionWindow:
    budget = action_budget or TurnActionBudget()
    if budget.turn_ended:
        budget = budget.next_turn()
    return TurnExecutionWindow(
        action_budget=budget,
        attack_phase=AttackPhaseBudget(attack_limit=attack_limit),
    )
