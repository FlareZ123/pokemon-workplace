"""Synchronize exact Trainer-search transactions with card-arrival provenance.

The canonical Trainer transaction owns legality and physical zone mutation.
This bridge mirrors one already-validated transaction into ResourceLedgerState,
retaining which action most recently brought a card into hand.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from discard_cost_witness import DiscardCandidate, DiscardSelection
from multicopy_zone_state import ZoneCountState
from search_zone_transition import SearchZoneTarget
from temporal_resource_ledger import ResourceLedgerState
from trainer_search_transaction import (
    RESOLVING_TRAINER_ZONE,
    TrainerSearchExecutionState,
    TrainerSearchTransaction,
)


INITIAL_ORIGIN = "initial"


@dataclass(frozen=True)
class ProvenanceMove:
    card_class: str
    source_origin: str
    source_zone: str
    destination_origin: str
    destination_zone: str
    amount: int


@dataclass(frozen=True)
class ProvenanceTransactionWitness:
    before: ResourceLedgerState
    after: ResourceLedgerState
    physical: TrainerSearchTransaction
    moves: tuple[ProvenanceMove, ...]


@dataclass(frozen=True)
class SynchronizedTrainerState:
    physical: TrainerSearchExecutionState
    provenance: ResourceLedgerState

    def __post_init__(self) -> None:
        projected = project_zones(self.provenance)
        if projected != self.physical.zones:
            raise ValueError("provenance projection does not match physical zone state")



def provenance_from_zones(
    zones: ZoneCountState,
    *,
    origin: str = INITIAL_ORIGIN,
) -> ResourceLedgerState:
    """Label every currently represented physical card with one initial origin."""

    if not origin:
        raise ValueError("origin must be non-empty")
    return ResourceLedgerState.from_mapping(
        {
            (card_class, origin, zone): count
            for card_class, zone, count in zones.counts
        }
    )


def project_zones(state: ResourceLedgerState) -> ZoneCountState:
    """Forget provenance and recover canonical exchangeable zone counts."""

    counts: dict[tuple[str, str], int] = {}
    for card_class, _origin, zone, count in state.counts:
        key = (card_class, zone)
        counts[key] = counts.get(key, 0) + count
    return ZoneCountState.from_mapping(counts)


def _origins_with(
    state: ResourceLedgerState,
    card_class: str,
    zone: str,
) -> tuple[tuple[str, int], ...]:
    return tuple(
        sorted(
            (origin, count)
            for current_class, origin, current_zone, count in state.counts
            if current_class == card_class and current_zone == zone
        )
    )


def _compositions(limits: tuple[int, ...], amount: int) -> tuple[tuple[int, ...], ...]:
    if amount < 0:
        raise ValueError "amount must be non-negative"
    if amount == 0:
        return ((0,) * len(limits),)
    if sum(limits) < amount:
        return ()

    out: list[tuple[int, ...]] = []

    def visit(index: int, left: int, chosen: list[int]) -> None:
        if index == len(limits):
            if left == 0:
                out.append(tuple(chosen))
            return
        upper = min(limits[index], left)
        for value in range(upper + 1):
            chosen.append(value)
            visit(index + 1, left - value, chosen)
            chosen.pop()

    visit(0, amount, [])
    return tuple(out)


def _move_any_origin(
    state: ResourceLedgerState,
    card_class: str,
    source_zone: str,
    destination_zone: str,
    amount: int,
    *,
    destination_origin: str | None = None,
) -> tuple[tuple[ResourceLedgerState, tuple[ProvenanceMove, ...]], ...]:
    origins = _origins_with(state, card_class, source_zone)
    limits = tuple(count for _origin, count in origins)
    outcomes = []

    for allocation in _compositions(limits, amount):
        after = state
        moves = []
        for (source_origin, _available), moved in zip(origins, allocation):
            if moved == 0:
                continue
            if destination_origin is None or destination_origin == source_origin:
                after = after.move(
                    card_class,
                    source_origin,
                    source_zone,
                    destination_zone,
                    amount=moved,
                )
                dest_origin = source_origin
            else:
                after = after.move(
                    card_class,
                    source_origin,
                    source_zone,
                    destination_zone,
                    amount=moved,
                )
                counts = {
                    (c, o, z): n
                    for c, o, z, n in after.counts
                }
                old_key = (card_class, source_origin, destination_zone)
                new_key = (card_class, destination_origin, destination_zone)
                remaining = counts[old_key] - moved
                if remaining:
                    counts[old_key] = remaining
                else:
                    counts.pop(old_key)
                counts[new_key] = counts.get(new_key, 0) + moved
                after = ResourceLedgerState.from_mapping(counts)
                dest_origin = destination_origin

            moves.append(
                ProvenanceMove(
                    card_class=card_class,
                    source_origin=source_origin,
                    source_zone=source_zone,
                    destination_origin=dest_origin,
                    destination_zone=destination_zone,
                    amount=moved,
                )
            )
        outcomes.append((after, tuple(moves)))
    return tuple(outcomes)


def _advance_frontier(
    frontier: tuple[tuple[ResourceLedgerState, tuple[ProvenanceMove, ...]], ...],
    *,
    card_class: str,
    source_zone: str,
    destination_zone: str,
    amount: int,
    destination_origin: str | None = None,
) -> tuple[tuple[ResourceLedgerState, tuple[ProvenanceMove, ...]], ...]:
    following = []
    for state, moves in frontier:
        for after, new_moves in _move_any_origin(
            state,
            card_class,
            source_zone,
            destination_zone,
            amount,
            destination_origin=destination_origin,
        ):
            following.append((after, moves + new_moves))
    return tuple(following)


def mirror_trainer_search_transaction(
    synchronized: SynchronizedTrainerState,
    transaction: TrainerSearchTransaction,
    *,
    action_card_class: str,
    action_name: str,
    step_index: int,
    discard_candidates: Sequence[DiscardCandidate],
    discard_selection: DiscardSelection | None,
    targets: Sequence[SearchZoneTarget],
    target_cost: Sequence[int],
) -> tuple[ProvenanceTransactionWitness, ...]:
    """Mirror one legal physical Trainer transaction into provenance state.

    The played Trainer is removed from hand before discard provenance is chosen,
    matching the canonical resolving-zone semantics. Retrieved targets are moved
    from deck to hand and relabeled with the current action as their hand-arrival
    provenance.
    """

    if synchronized.physical != transaction.before:
        raise ValueError("transaction.before does not match synchronized physical state")
    if not action_name:
        raise ValueError("action_name must be non-empty")
    if step_index < 0:
        raise ValueError("step_index must be non-negative")
    if len(targets) != len(tuple(target_cost)):
        raise ValueError("target_cost length does not match targets")

    candidates = tuple(discard_candidates)
    if discard_selection is None:
        discard_counts = (0,) * len(candidates)
    else:
        if len(discard_selection.counts) != len(candidates):
            raise ValueError "discard selection length does not match candidates"
        discard_counts = discard_selection.counts

    frontier = ((synchronized.provenance, ()),)
    frontier = _advance_frontier(
        frontier,
        card_class=action_card_class,
        source_zone="hand",
        destination_zone=RESOLVING_TRAINER_ZONE,
        amount=1,
    )

    for candidate, amount in zip(candidates, discard_counts):
        if amount == 0:
            continue
        frontier = _advance_frontier(
            frontier,
            card_class=candidate.card_class,
            source_zone="hand",
            destination_zone="discard",
            amount=amount,
        )

    arrival_origin = f"{step_index}:{action_name}"
    for target, amount in zip(targets, tuple(target_cost)):
        if amount == 0:
            continue
        frontier = _advance_frontier(
            frontier,
            card_class=target.card_class,
            source_zone="deck",
            destination_zone="hand",
            amount=amount,
            destination_origin=arrival_origin,
        )

    frontier = _advance_frontier(
        frontier,
        card_class=action_card_class,
        source_zone=RESOLVING_TRAINER_ZONE,
        destination_zone="discard",
        amount=1,
    )

    witnesses = []
    for after, moves in frontier:
        if project_zones(after) != transaction.after.zones:
            continue
        witnesses.append(
            ProvenanceTransactionWitness(
                before=synchronized.provenance,
                after=after,
                physical=transaction,
                moves=moves,
            )
        )

    if not witnesses:
        raise ValueError("no provenance assignment matches the physical transaction")
    return tuple(witnesses)


def advance_synchronized_state(
    witness: ProvenanceTransactionWitness,
) -> SynchronizedTrainerState:
    return SynchronizedTrainerState(
        physical=witness.physical.after,
        provenance=witness.after,
    )
