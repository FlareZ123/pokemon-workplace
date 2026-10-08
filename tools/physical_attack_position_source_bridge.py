"""Apply exact attack-source position effects on conserved physical boards.

This bridge consumes a completed copied-attack damage replay and applies the
source attack's Active/Bench movement during the attack-effect step. It keeps
the copy actor and defending side as separate StackBoardMaterialState values,
preserves physical card identity, and updates the defender-side copy replay
when the movement acts on the opponent.

Only PositionEffectProfile rows compiled from complete attack-text bodies are
accepted. Damage, Energy payment, coin generation, and effect-immunity
eligibility remain owned by their existing layers.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from attack_copy_physical_ko_bridge import AttackCopyPhysicalBoardResolution
from board_position_state import clear_for_bench, validate_state
from position_effect_profile_compiler import (
    EffectTargetGeometry,
    PositionEffectKind,
    PositionEffectProfile,
)
from stack_knockout_conservation import StackBoardMaterialState


@dataclass(frozen=True)
class PhysicalAttackPositionApplication:
    actor_state: StackBoardMaterialState
    updated_copy_resolution: AttackCopyPhysicalBoardResolution
    profile: PositionEffectProfile
    body_event: str
    attacking_pokemon_id: str
    chosen_pokemon_id: str | None
    targeted_pokemon_id: str | None
    moved: bool


def _switch_active(
    state: StackBoardMaterialState,
    replacement_id: str,
) -> StackBoardMaterialState | None:
    board = state.board
    if board is None:
        raise ValueError("position effect requires an in-play board")
    if replacement_id not in board.bench_ids:
        return None

    outgoing = clear_for_bench(board.get(board.active_id))
    next_board = replace(
        board,
        pokemon=tuple(
            outgoing if pokemon.pokemon_id == outgoing.pokemon_id else pokemon
            for pokemon in board.pokemon
        ),
        active_id=replacement_id,
    )
    validate_state(next_board)
    return StackBoardMaterialState(state.ledger, next_board)


def _validated_choice(
    state: StackBoardMaterialState,
    chosen_pokemon_id: str | None,
) -> str | None:
    board = state.board
    if board is None:
        raise ValueError("position effect requires an in-play board")
    if not board.bench_ids:
        if chosen_pokemon_id is not None:
            raise ValueError("choice supplied when no Benched Pokemon exists")
        return None
    if chosen_pokemon_id is None:
        raise ValueError("a legal Benched replacement must be chosen")
    if chosen_pokemon_id not in board.bench_ids:
        raise ValueError("chosen replacement is not currently Benched")
    return chosen_pokemon_id


def apply_physical_attack_position_effect(
    replay: AttackCopyPhysicalBoardResolution,
    actor_state: StackBoardMaterialState,
    profile: PositionEffectProfile,
    *,
    attacking_pokemon_id: str,
    chosen_pokemon_id: str | None = None,
    coin_heads: bool | None = None,
    take_optional: bool | None = None,
    blocked_actor_effect_target_ids: frozenset[str] = frozenset(),
    blocked_defender_effect_target_ids: frozenset[str] = frozenset(),
) -> PhysicalAttackPositionApplication:
    """Apply one complete attack-source movement body after attack damage.

    The returned copy resolution contains the moved defender board when the
    source effect acts on the opponent. Self-switches instead update actor_state.

    Coin-gated and optional effects require explicit branch inputs. If the
    branch does not execute, or if the affected side has no Benched Pokemon,
    the attack remains resolved and the movement is reported as not moved.
    """

    if profile.source_kind != "attack" or profile.attack_index is None:
        raise ValueError("physical attack bridge requires an exact attack profile")
    body_event = f"body:{profile.card_id}:attack:{profile.attack_index}"
    if body_event not in replay.resolution.state.events:
        raise ValueError("copy-body trace did not execute this position source")

    actor_board = actor_state.board
    defender_board = replay.state.board
    if actor_board is None or defender_board is None:
        raise ValueError("position effect requires both physical boards in play")
    try:
        actor_board.get(attacking_pokemon_id)
    except StopIteration as exc:
        raise ValueError("attacking Pokemon is not on the actor board") from exc

    if profile.coin_heads_required:
        if coin_heads is None:
            raise ValueError("coin-gated position effect requires a coin result")
        if not coin_heads:
            return PhysicalAttackPositionApplication(
                actor_state, replay, profile, body_event,
                attacking_pokemon_id, chosen_pokemon_id, None, False,
            )
    elif coin_heads is not None:
        raise ValueError("ungated position effect does not consume a coin result")

    if profile.optional:
        if take_optional is None:
            raise ValueError("optional position effect requires an explicit choice")
        if not take_optional:
            return PhysicalAttackPositionApplication(
                actor_state, replay, profile, body_event,
                attacking_pokemon_id, chosen_pokemon_id, None, False,
            )
    elif take_optional is not None:
        raise ValueError("mandatory position effect has no optional branch")

    if profile.kind == PositionEffectKind.SELF_SWITCH:
        if profile.effect_target != EffectTargetGeometry.ACTOR_ACTIVE:
            raise ValueError("self-switch profile has inconsistent target geometry")
        if actor_board.active_id != attacking_pokemon_id:
            raise ValueError("self-switch source no longer has the attacker Active")
        chosen = _validated_choice(actor_state, chosen_pokemon_id)
        target_id = attacking_pokemon_id
        if chosen is None or target_id in blocked_actor_effect_target_ids:
            return PhysicalAttackPositionApplication(
                actor_state, replay, profile, body_event,
                attacking_pokemon_id, chosen, target_id, False,
            )
        moved_actor = _switch_active(actor_state, chosen)
        assert moved_actor is not None
        return PhysicalAttackPositionApplication(
            moved_actor, replay, profile, body_event,
            attacking_pokemon_id, chosen, target_id, True,
        )

    if profile.kind == PositionEffectKind.OPPONENT_FORCED_SWITCH:
        if profile.effect_target != EffectTargetGeometry.OPPONENT_ACTIVE:
            raise ValueError("forced-switch profile has inconsistent target geometry")
        chosen = _validated_choice(replay.state, chosen_pokemon_id)
        target_id = defender_board.active_id
        if chosen is None or target_id in blocked_defender_effect_target_ids:
            return PhysicalAttackPositionApplication(
                actor_state, replay, profile, body_event,
                attacking_pokemon_id, chosen, target_id, False,
            )
        moved_defender = _switch_active(replay.state, chosen)
        assert moved_defender is not None
        return PhysicalAttackPositionApplication(
            actor_state,
            replace(replay, state=moved_defender),
            profile,
            body_event,
            attacking_pokemon_id,
            chosen,
            target_id,
            True,
        )

    if profile.kind == PositionEffectKind.TARGETED_GUST:
        if profile.effect_target != EffectTargetGeometry.SELECTED_OPPONENT_BENCH:
            raise ValueError("targeted-gust profile has inconsistent target geometry")
        chosen = _validated_choice(replay.state, chosen_pokemon_id)
        target_id = chosen
        if chosen is None or chosen in blocked_defender_effect_target_ids:
            return PhysicalAttackPositionApplication(
                actor_state, replay, profile, body_event,
                attacking_pokemon_id, chosen, target_id, False,
            )
        moved_defender = _switch_active(replay.state, chosen)
        assert moved_defender is not None
        return PhysicalAttackPositionApplication(
            actor_state,
            replace(replay, state=moved_defender),
            profile,
            body_event,
            attacking_pokemon_id,
            chosen,
            target_id,
            True,
        )

    raise ValueError(f"unsupported position effect kind: {profile.kind}")
