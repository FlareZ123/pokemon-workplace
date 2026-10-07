"""Focused executor for the Regidrago Timeless-GX -> Phantom Dive ALS."""

from __future__ import annotations

from dataclasses import dataclass

from board_object_kernel import BoardState
from canonical_turn_sequence_owner import (
    TurnScheduleState,
    advance_turn,
    close_turn_with_attack,
)
from damage_board_bridge import (
    EffectCounterPlacement,
    apply_attack_damage,
    knocked_out_ids,
    resolve_attack_damage_phase,
)
from damage_calculation_kernel import AttackDamage, DamageContext
from position_effect_execution import execute_position_effect
from position_effect_profile_compiler import PositionEffectProfile
from turn_action_budget import TurnAction, TurnActionBudget
from unified_state_kernel import consume_turn_action, make_state


@dataclass(frozen=True)
class TimelessPhantomResult:
    board_after_timeless: BoardState
    board_after_second_gust: BoardState
    final_board: BoardState
    first_attack_knocked_out_ids: tuple[str, ...]
    final_attack_knocked_out_ids: tuple[str, ...]
    extra_turn_supporter_available: bool


def execute_timeless_phantom_line(
    actor_board: BoardState,
    opponent_board: BoardState,
    *,
    first_target_id: str,
    second_target_id: str,
    hp_by_object_id: dict[str, int],
    boss_profile: PositionEffectProfile,
) -> TimelessPhantomResult | None:
    """Execute the two-turn gust -> Timeless -> gust -> Phantom Dive sequence.

    Attack-copy source eligibility, Energy payment, and GX-use availability are
    upstream prerequisites. This function owns the position, damage, and generic
    per-turn Supporter/attack-window consequences after those prerequisites hold.
    """

    if first_target_id == second_target_id:
        return None

    actor_turn = make_state({}, turn_budget=TurnActionBudget())
    other_turn = make_state({}, turn_budget=TurnActionBudget())
    schedule = TurnScheduleState("actor", "opponent")

    actor_turn = consume_turn_action(actor_turn, TurnAction.SUPPORTER)
    if actor_turn is None:
        return None

    first_gust = execute_position_effect(
        boss_profile,
        actor_board,
        opponent_board,
        chosen_object_id=first_target_id,
    )
    if first_gust is None:
        return None

    after_timeless, _ = apply_attack_damage(
        first_gust.opponent_board,
        first_target_id,
        DamageContext(attack=AttackDamage(150)),
    )
    first_kos = knocked_out_ids(after_timeless, hp_by_object_id)
    if first_target_id in first_kos:
        return None

    closed = close_turn_with_attack(
        schedule,
        actor_turn,
        take_another_turn=True,
        skip_pokemon_checkup=True,
    )
    if closed is None:
        return None
    schedule, actor_turn = closed

    advanced = advance_turn(schedule, actor_turn, other_turn)
    if advanced is None or not advanced.same_player_continues:
        return None
    actor_turn = advanced.current_state
    other_turn = advanced.other_state
    schedule = advanced.schedule

    supporter_available = actor_turn.turn_budget is not None and actor_turn.turn_budget.can(
        TurnAction.SUPPORTER
    )
    if not supporter_available:
        return None
    actor_turn = consume_turn_action(actor_turn, TurnAction.SUPPORTER)
    if actor_turn is None:
        return None

    second_gust = execute_position_effect(
        boss_profile,
        first_gust.actor_board,
        after_timeless,
        chosen_object_id=second_target_id,
    )
    if second_gust is None:
        return None

    phantom = resolve_attack_damage_phase(
        second_gust.opponent_board,
        damage_target_id=second_target_id,
        damage_context=DamageContext(attack=AttackDamage(200)),
        counter_placements=(EffectCounterPlacement(first_target_id, 6),),
        hp_by_object_id=hp_by_object_id,
    )

    closed_second = close_turn_with_attack(
        schedule,
        actor_turn,
        take_another_turn=False,
        skip_pokemon_checkup=False,
    )
    if closed_second is None:
        return None

    return TimelessPhantomResult(
        board_after_timeless=after_timeless,
        board_after_second_gust=second_gust.opponent_board,
        final_board=phantom.board,
        first_attack_knocked_out_ids=first_kos,
        final_attack_knocked_out_ids=phantom.knocked_out_ids,
        extra_turn_supporter_available=supporter_available,
    )
