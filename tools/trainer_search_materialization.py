"""Materialize typed Trainer deck-search payloads into the physical zone ledger.

The typed search adapter already proves which physical target groups a legal
connector action consumes. This module carries that exact target-cost witness
into ``IdentityLedger`` by moving exchangeable copies from deck to hand.

It deliberately materializes only the search payload. Trainer play, discard
payments, action-window consumption, and deck shuffling remain in their existing
semantic layers.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from identity_materialization import IdentityLedger, assert_conserved
from resource_constrained_connectors import (
    ResourceActionProfile,
    ResourceConnectorResult,
)
from trainer_search_state_adapter import (
    RESOURCE_NAMES,
    TypedTrainerSearchAdaptation,
)


@dataclass(frozen=True)
class SearchTargetBinding:
    """Bind one typed target resource to one exchangeable card class."""

    resource_name: str
    card_class: str
    card_name: str

    def __post_init__(self) -> None:
        if not self.resource_name:
            raise ValueError("resource_name must be non-empty")
        if not self.card_class:
            raise ValueError("card_class must be non-empty")
        if not self.card_name:
            raise ValueError("card_name must be non-empty")


@dataclass(frozen=True)
class SearchTargetMove:
    """One exact class-level deck-to-hand move executed from a search witness."""

    resource_name: str
    card_class: str
    card_name: str
    amount: int


@dataclass(frozen=True)
class SearchMaterialization:
    """Physical ledger after applying one or more typed search payloads."""

    ledger: IdentityLedger
    moves: tuple[SearchTargetMove, ...]


def _target_resource_names(
    adaptation: TypedTrainerSearchAdaptation,
) -> tuple[str, ...]:
    prefix = adaptation.resource_names[: len(RESOURCE_NAMES)]
    if prefix != RESOURCE_NAMES:
        raise ValueError("typed search adaptation has an unexpected resource prefix")
    return adaptation.resource_names[len(RESOURCE_NAMES) :]


def _validate_bindings(
    adaptation: TypedTrainerSearchAdaptation,
    bindings: Sequence[SearchTargetBinding],
) -> tuple[SearchTargetBinding, ...]:
    bound = tuple(bindings)
    expected = _target_resource_names(adaptation)
    actual = tuple(binding.resource_name for binding in bound)
    if actual != expected:
        raise ValueError(
            "target bindings must match adaptation target resources in exact order"
        )

    classes = [binding.card_class for binding in bound]
    if len(classes) != len(set(classes)):
        raise ValueError(
            "one exchangeable card class cannot be represented by multiple target resources"
        )
    return bound


def selected_target_counts(
    adaptation: TypedTrainerSearchAdaptation,
    action: ResourceActionProfile,
) -> tuple[int, ...]:
    """Return the physical target-count slice encoded in one adapted action."""

    if action not in adaptation.connector.profiles:
        raise ValueError("action is not a profile from this typed search adaptation")
    if len(action.cost) != len(adaptation.resource_names):
        raise ValueError("action cost length does not match adaptation resources")
    return action.cost[len(RESOURCE_NAMES) :]


def materialize_search_action(
    ledger: IdentityLedger,
    adaptation: TypedTrainerSearchAdaptation,
    action: ResourceActionProfile,
    bindings: Sequence[SearchTargetBinding],
) -> SearchMaterialization:
    """Move the exact target classes selected by one action from deck to hand."""

    bound = _validate_bindings(adaptation, bindings)
    selected = selected_target_counts(adaptation, action)
    if len(selected) != len(bound):
        raise ValueError("selected target count length does not match bindings")

    next_ledger = ledger
    moves: list[SearchTargetMove] = []
    for binding, amount in zip(bound, selected, strict=True):
        if amount == 0:
            continue
        if amount < 0:
            raise ValueError("selected target counts must be non-negative")
        next_exchangeable = next_ledger.exchangeable.move(
            binding.card_class,
            "deck",
            "hand",
            amount=amount,
        )
        next_ledger = IdentityLedger(
            exchangeable=next_exchangeable,
            instances=next_ledger.instances,
        )
        moves.append(
            SearchTargetMove(
                resource_name=binding.resource_name,
                card_class=binding.card_class,
                card_name=binding.card_name,
                amount=amount,
            )
        )

    assert_conserved(ledger, next_ledger)
    return SearchMaterialization(next_ledger, tuple(moves))


def materialize_search_witness(
    ledger: IdentityLedger,
    adaptation: TypedTrainerSearchAdaptation,
    result: ResourceConnectorResult,
    bindings: Sequence[SearchTargetBinding],
) -> SearchMaterialization:
    """Execute every use in an exact connector witness against the zone ledger."""

    if result.witness_actions is None:
        raise ValueError("connector result has no exact witness to materialize")

    bound = _validate_bindings(adaptation, bindings)
    next_ledger = ledger
    all_moves: list[SearchTargetMove] = []
    for connector_name, action in result.witness_actions:
        if connector_name != adaptation.connector.name:
            raise ValueError(
                "witness contains a connector outside this typed search adaptation"
            )
        step = materialize_search_action(
            next_ledger,
            adaptation,
            action,
            bound,
        )
        next_ledger = step.ledger
        all_moves.extend(step.moves)

    assert_conserved(ledger, next_ledger)
    return SearchMaterialization(next_ledger, tuple(all_moves))
