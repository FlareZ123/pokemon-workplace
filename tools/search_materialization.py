"""Materialize successful typed deck-search selections into physical hand instances."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from identity_materialization import (
    IdentityLedger,
    assert_conserved,
    materialize,
    move_instance,
)
from typed_search_target_allocator import TargetGroup


@dataclass(frozen=True)
class SearchTargetBinding:
    card_class: str
    card_name: str

    def __post_init__(self) -> None:
        if not self.card_class or not self.card_name:
            raise ValueError("search target binding fields must be non-empty")


@dataclass(frozen=True)
class SearchMaterializationResult:
    ledger: IdentityLedger
    instance_ids: tuple[str, ...]


def validate_search_targets(
    ledger: IdentityLedger,
    targets: Sequence[TargetGroup],
    bindings: Sequence[SearchTargetBinding],
    *,
    source_zone: str = "deck",
) -> None:
    if len(targets) != len(bindings):
        raise ValueError("targets and bindings must have equal length")

    seen_classes: set[str] = set()
    for target, binding in zip(targets, bindings, strict=True):
        if binding.card_class in seen_classes:
            raise ValueError("each target group must map to a distinct card class")
        seen_classes.add(binding.card_class)
        available = ledger.exchangeable.count(binding.card_class, source_zone)
        if available != target.copies:
            raise ValueError(
                f"target capacity mismatch for {binding.card_class!r}: "
                f"typed={target.copies}, ledger={available}"
            )


def materialize_search_to_hand(
    ledger: IdentityLedger,
    targets: Sequence[TargetGroup],
    bindings: Sequence[SearchTargetBinding],
    target_cost: Sequence[int],
    instance_ids: Sequence[Sequence[str]],
    *,
    source_zone: str = "deck",
) -> SearchMaterializationResult:
    validate_search_targets(
        ledger,
        targets,
        bindings,
        source_zone=source_zone,
    )
    if len(target_cost) != len(targets) or len(instance_ids) != len(targets):
        raise ValueError("target cost and instance IDs must align with targets")

    next_ledger = ledger
    created: list[str] = []
    for target, binding, count, ids in zip(
        targets,
        bindings,
        target_cost,
        instance_ids,
        strict=True,
    ):
        if count < 0 or count > target.copies:
            raise ValueError("invalid target consumption")
        if len(ids) != count:
            raise ValueError("instance ID count must equal target consumption")

        for instance_id in ids:
            next_ledger = materialize(
                next_ledger,
                card_class=binding.card_class,
                card_name=binding.card_name,
                source_zone=source_zone,
                instance_id=instance_id,
            )
            next_ledger = move_instance(
                next_ledger,
                instance_id,
                "hand",
            )
            created.append(instance_id)

    assert_conserved(ledger, next_ledger)
    return SearchMaterializationResult(
        next_ledger,
        tuple(created),
    )
