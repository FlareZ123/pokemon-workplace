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
from damage_calculation_kernel import AttackDamage, DamageContext, calculate_damage
from position_effect_execution import execute_position_effect
from position_effect_profile_compiler import PositionEffectProfile
from turn_action_budget import TurnAction, TurnActionBudget
from unified_state_kernel import consume_turn_action, make_state


@dataclass(frozen=True)
class TimelessPhantomPriorDamageBand:
    first_target_min: int
    first_target_max: int
    second_target_min: int


@dataclass(frozen=True)
class TimelessPhantomHpWindow:
    first_damage_before_phantom: int
    first_hp_survival_threshold: int
    first_hp_ko_ceiling: int
    second_damage_total: int
    second_hp_ko_ceiling: int
    phantom_counter_damage: int


@dataclass(frozen=True)
class TimelessPhantomResult:
    board_after_timeless: BoardState
    board_after_second_gust: BoardState
    final_board: BoardState
    first_attack_knocked_out_ids: tuple[str, ...]
    final_attack_knocked_out_ids: tuple[str, ...]
    extra_turn_supporter_available: bool


def derive_timeless_phantom_hp_window(
    *,
    first_prior_damage: int = 0,
    second_prior_damage: int = 0,
    timeless_damage_context: DamageContext | None = None,
    phantom_damage_context: DamageContext | None = None,
    phantom_counter_count: int = 6,
) -> TimelessPhantomHpWindow:
    """Return exact damage thresholds for the delayed double-KO line."""

    if first_prior_damage < 0 or second_prior_damage < 0:
        raise ValueError("prior damage must be non-negative")
    if phantom_counter_count < 0:
        raise ValueError("phantom_counter_count must be non-negative")
    if first_prior_damage % 10 or second_prior_damage % 10:
        raise ValueError("prior damage must be representable in damage counters")

    timeless = calculate_damage(
        timeless_damage_context
        or DamageContext(attack=AttackDamage(150))
    ).final_damage
    phantom = calculate_damage(
        phantom_damage_context
        or DamageContext(attack=AttackDamage(200))
    ).final_damage
    if timeless % 10 or phantom % 10:
        raise ValueError("resolved damage must be representable in damage counters")

    first_before_phantom = first_prior_damage + timeless
    counter_damage = phantom_counter_count * 10
    return TimelessPhantomHpWindow(
        first_damage_before_phantom=first_before_phantom,
        first_hp_survival_threshold=first_before_phantom,
        first_hp_ko_ceiling=first_before_phantom + counter_damage,
        second_damage_total=second_prior_damage + phantom,
        second_hp_ko_ceiling=second_prior_damage + phantom,
        phantom_counter_damage=counter_damage,
    )


def derive_timeless_phantom_prior_damage_band(
    *,
    first_target_hp: int,
    second_target_hp: int,
    timeless_damage_context: DamageContext | None = None,
    phantom_damage_context: DamageContext | None = None,
    phantom_counter_count: int = 6,
) -> TimelessPhantomPriorDamageBand | None:
    """Return 10-damage-step prior-damage requirements for two target HPs."""

    if (
        first_target_hp <= 0
        or second_target_hp <= 0
        or first_target_hp % 10
        or second_target_hp % 10
    ):
        raise ValueError("target HP must be a positive multiple of 10")

    base = derive_timeless_phantom_hp_window(
        timeless_damage_context=timeless_damage_context,
        phantom_damage_context=phantom_damage_context,
        phantom_counter_count=phantom_counter_count,
    )
    timeless = base.first_damage_before_phantom
    phantom = base.second_damage_total
    counter_damage = base.phantom_counter_damage

    first_min = max(0, first_target_hp - timeless - counter_damage)
    first_max = first_target_hp - timeless - 10
    second_min = max(0, second_target_hp - phantom)

    if first_min > first_max or second_min >= second_target_hp:
        return None

    return TimelessPhantomPriorDamageBand(
        first_target_min=first_min,
        first_target_max=first_max,
        second_target_min=second_min,
    )


def execute_timeless_phantom_line(
    actor_board: BoardState,
    opponent_board: BoardState,
    *,
    first_target_id: str,
    second_target_id: str,
    hp_by_object_id: dict[str, int],
    boss_profile: PositionEffectProfile,
    timeless_damage_context: DamageContext | None = None,
    phantom_damage_context: DamageContext | None = None,
    first_target_prevent_phantom_effects: bool = False,
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
        timeless_damage_context
        or DamageContext(attack=AttackDamage(150)),
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
        damage_context=(
            phantom_damage_context
            or DamageContext(attack=AttackDamage(200))
        ),
        counter_placements=(
            EffectCounterPlacement(
                first_target_id,
                6,
                prevent_effects_of_attacks=(
                    first_target_prevent_phantom_effects
                ),
            ),
        ),
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
