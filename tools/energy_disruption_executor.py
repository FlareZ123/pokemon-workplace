"""Execute one-card opponent Energy discard on conserved stack state."""

from __future__ import annotations

from dataclasses import dataclass, replace

from board_position_state import AttachmentKind, replace_pokemon
from energy_disruption_profile_compiler import (
    EnergyDisruptionProfile,
    EnergyRestriction,
    OpponentTargetScope,
)
from identity_materialization import (
    assert_conserved,
    dematerialize,
    detach_instance,
)
from stack_knockout_conservation import StackBoardMaterialState


@dataclass(frozen=True)
class EnergyDisruptionOutcome:
    state: StackBoardMaterialState
    discarded_instance_id: str | None
    coin_heads: bool | None


def _eligible_energy_ids(
    profile: EnergyDisruptionProfile,
    state: StackBoardMaterialState,
    *,
    special_energy_instance_ids: frozenset[str],
) -> tuple[tuple[str, str], ...]:
    if state.board is None:
        return ()

    rows: list[tuple[str, str]] = []
    for pokemon in state.board.pokemon:
        if (
            profile.target_scope == OpponentTargetScope.ACTIVE
            and pokemon.pokemon_id != state.board.active_id
        ):
            continue
        for attachment in pokemon.attachments:
            if attachment.kind != AttachmentKind.ENERGY:
                continue
            if (
                profile.energy_restriction == EnergyRestriction.SPECIAL
                and attachment.card_id not in special_energy_instance_ids
            ):
                continue
            rows.append((pokemon.pokemon_id, attachment.card_id))
    return tuple(rows)


def resolve_energy_disruption(
    profile: EnergyDisruptionProfile,
    state: StackBoardMaterialState,
    *,
    target_pokemon_id: str | None = None,
    energy_instance_id: str | None = None,
    special_energy_instance_ids: frozenset[str] = frozenset(),
    coin_heads: bool | None = None,
    preserve_identity: bool = False,
) -> EnergyDisruptionOutcome | None:
    """Resolve the compiled discard effect against the opponent-side board.

    A Trainer profile is unplayable when no eligible Energy exists. An attack
    profile with no eligible Energy simply has no discard effect.
    """

    eligible = _eligible_energy_ids(
        profile,
        state,
        special_energy_instance_ids=special_energy_instance_ids,
    )

    if not eligible:
        if profile.source_kind == "trainer":
            return None
        return EnergyDisruptionOutcome(state, None, coin_heads)

    if profile.coin_heads_required:
        if coin_heads is None:
            raise ValueError("coin_heads is required for coin-gated disruption")
        if not coin_heads:
            return EnergyDisruptionOutcome(state, None, False)
    elif coin_heads is not None:
        raise ValueError("coin_heads must be omitted for deterministic disruption")

    if target_pokemon_id is None or energy_instance_id is None:
        raise ValueError("successful disruption requires an exact target and Energy")

    if (target_pokemon_id, energy_instance_id) not in eligible:
        return None

    assert state.board is not None
    pokemon = state.board.get(target_pokemon_id)
    attachment = next(
        card
        for card in pokemon.attachments
        if card.card_id == energy_instance_id
    )
    next_pokemon = replace(
        pokemon,
        attachments=tuple(
            card
            for card in pokemon.attachments
            if card.card_id != energy_instance_id
        ),
    )
    board = replace_pokemon(state.board, next_pokemon)

    ledger = detach_instance(
        state.ledger,
        attachment.card_id,
        "discard",
    )
    if not preserve_identity:
        ledger = dematerialize(ledger, attachment.card_id)

    next_state = StackBoardMaterialState(ledger, board)
    assert_conserved(state.ledger, next_state.ledger)
    return EnergyDisruptionOutcome(
        next_state,
        attachment.card_id,
        True if profile.coin_heads_required else None,
    )
