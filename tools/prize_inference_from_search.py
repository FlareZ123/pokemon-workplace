"""Infer exact grouped Prize composition after a full deck inspection."""

from __future__ import annotations

from typing import Mapping

from identity_materialization import IdentityLedger
from prize_belief_kernel import PrizeBelief


def _known_non_prize_count(
    ledger: IdentityLedger,
    card_class: str,
) -> int:
    exchangeable = sum(
        count
        for current_class, zone, count in ledger.exchangeable.counts
        if current_class == card_class and zone != "prize"
    )
    materialized = sum(
        1
        for instance in ledger.instances
        if instance.card_class == card_class and instance.zone != "prize"
    )
    return exchangeable + materialized


def infer_exact_prize_belief_after_full_deck_search(
    ledger: IdentityLedger,
    group_classes: Mapping[str, str],
    group_total_copies: Mapping[str, int],
    *,
    prize_count: int,
) -> PrizeBelief:
    """Collapse grouped Prize uncertainty using decklist and observed non-Prize copies."""

    if set(group_classes) != set(group_total_copies):
        raise ValueError("group mappings must describe the same groups")

    exact: dict[str, int] = {}
    for group, card_class in group_classes.items():
        total = group_total_copies[group]
        if total < 0:
            raise ValueError("group total copies must be non-negative")
        if ledger.total(card_class) != total:
            raise ValueError(
                f"ledger total for {card_class!r} does not match decklist total"
            )

        known_non_prize = _known_non_prize_count(ledger, card_class)
        prized = total - known_non_prize
        if prized < 0:
            raise ValueError("observed non-Prize copies exceed decklist total")
        exact[group] = prized

    return PrizeBelief.from_exact(exact, prize_count)
