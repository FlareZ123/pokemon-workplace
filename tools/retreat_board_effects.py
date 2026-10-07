"""Derive Retreat destination effects from exact opponent-board sources."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from board_object_kernel import BoardState
from retreat_energy_transaction import (
    RetreatEnergyTransactionResult,
    RetreatEnergyTransactionState,
    retreat_with_energy_destinations,
)


@dataclass(frozen=True, order=True)
class ScoopUpBlockSource:
    print_id: str
    card_name: str
    ability_name: str = "Scoop-Up Block"


SCOOP_UP_BLOCK_SOURCES = (
    ScoopUpBlockSource("sm9-66", "Mr. Mime"),
)
_SCOOP_UP_BLOCK_KEYS = frozenset(
    (source.print_id, source.card_name)
    for source in SCOOP_UP_BLOCK_SOURCES
)


@dataclass(frozen=True)
class BoardDerivedRetreatResult:
    """Retreat transaction plus the opponent-board sources that affected it."""

    transaction: RetreatEnergyTransactionResult
    scoop_up_block_source_ids: tuple[str, ...] = ()


def active_scoop_up_block_source_ids(
    opponent_board: BoardState,
) -> tuple[str, ...]:
    """Return active exact-print Scoop-Up Block sources on the opponent board.

    The current paper Expanded card pool has one exact source: Mr. Mime
    `sm9-66`. Its Ability text is not position-gated, so either Active or Bench
    residency is sufficient. `abilities_enabled` is the board-level resolved
    Ability-suppression fact.
    """

    return tuple(sorted(
        pokemon.object_id
        for pokemon in opponent_board.objects
        if pokemon.abilities_enabled
        and (pokemon.print_id, pokemon.card_name) in _SCOOP_UP_BLOCK_KEYS
    ))


def retreat_with_opponent_board_effects(
    state: RetreatEnergyTransactionState,
    bench_object_id: str,
    *,
    retreat_cost: int,
    discard_energy_ids: Iterable[str],
    opponent_board: BoardState,
    prism_star_energy_ids: Iterable[str] = (),
) -> BoardDerivedRetreatResult | None:
    """Execute Retreat while deriving Scoop-Up Block from opponent board state."""

    source_ids = active_scoop_up_block_source_ids(opponent_board)
    transaction = retreat_with_energy_destinations(
        state,
        bench_object_id,
        retreat_cost=retreat_cost,
        discard_energy_ids=discard_energy_ids,
        opposing_scoop_up_block_active=bool(source_ids),
        prism_star_energy_ids=prism_star_energy_ids,
    )
    if transaction is None:
        return None
    return BoardDerivedRetreatResult(
        transaction=transaction,
        scoop_up_block_source_ids=source_ids,
    )
