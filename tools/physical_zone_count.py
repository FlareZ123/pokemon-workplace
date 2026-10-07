"""Canonical physical zone counts across exchangeable copies and instances."""

from __future__ import annotations

from identity_materialization import IdentityLedger


def physical_zone_count(
    ledger: IdentityLedger,
    zone: str,
    *,
    card_class: str | None = None,
) -> int:
    """Count all physical cards in one zone across both identity layers."""

    if not zone:
        raise ValueError("zone must be non-empty")

    if card_class is None:
        exchangeable = sum(
            count
            for _current_class, current_zone, count in ledger.exchangeable.counts
            if current_zone == zone
        )
        materialized = sum(instance.zone == zone for instance in ledger.instances)
    else:
        if not card_class:
            raise ValueError("card_class must be non-empty when supplied")
        exchangeable = ledger.exchangeable.count(card_class, zone)
        materialized = sum(
            instance.zone == zone and instance.card_class == card_class
            for instance in ledger.instances
        )

    return exchangeable + materialized


def physical_hand_size(ledger: IdentityLedger) -> int:
    return physical_zone_count(ledger, "hand")
