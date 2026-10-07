"""One-slot marginal values under connector domination.

This module compares three fixed-deck-size substitutions in the exact
two-channel connector model:

- turn one protected filler slot into an additional target-A out;
- turn one protected filler slot into an additional target-B out;
- turn one protected filler slot into an additional disposable card.

The underlying probabilities come from `connector_domination.py`.
"""

from __future__ import annotations

from dataclasses import dataclass

from connector_domination import (
    ConnectorDominationResult,
    two_channel_connector_access,
)


@dataclass(frozen=True)
class SlotMarginal:
    """Marginal joint-access value of one fixed-size deck substitution."""

    realistic_gain: float
    naive_gated_gain: float
    naive_bias: float
    naive_to_realistic_ratio: float


@dataclass(frozen=True)
class SlotMarginalResult:
    """Baseline plus one-slot substitutions."""

    baseline: ConnectorDominationResult
    add_target_a: SlotMarginal
    add_target_b: SlotMarginal
    add_disposable: SlotMarginal


def _marginal(
    baseline: ConnectorDominationResult,
    changed: ConnectorDominationResult,
) -> SlotMarginal:
    realistic = (
        changed.capacity_aware_gated_access
        - baseline.capacity_aware_gated_access
    )
    naive = (
        changed.naive_shared_connector_gated_access
        - baseline.naive_shared_connector_gated_access
    )
    ratio = naive / realistic if realistic else float("inf")
    return SlotMarginal(
        realistic_gain=realistic,
        naive_gated_gain=naive,
        naive_bias=naive - realistic,
        naive_to_realistic_ratio=ratio,
    )


def connector_slot_marginals(
    deck_size: int,
    prize_count: int,
    *,
    starter_cards: int,
    target_a_copies: int,
    target_b_copies: int,
    disposable_nonstarters: int,
    discard_cost: int,
    opening_hand_size: int = 7,
) -> SlotMarginalResult:
    """Return fixed-size one-slot marginal values.

    Each substitution consumes one protected non-starter filler slot because
    `deck_size` is held fixed while exactly one modeled category increases by
    one card.
    """

    common = dict(
        deck_size=deck_size,
        prize_count=prize_count,
        starter_cards=starter_cards,
        discard_cost=discard_cost,
        opening_hand_size=opening_hand_size,
    )
    baseline = two_channel_connector_access(
        **common,
        target_a_copies=target_a_copies,
        target_b_copies=target_b_copies,
        disposable_nonstarters=disposable_nonstarters,
    )
    add_a = two_channel_connector_access(
        **common,
        target_a_copies=target_a_copies + 1,
        target_b_copies=target_b_copies,
        disposable_nonstarters=disposable_nonstarters,
    )
    add_b = two_channel_connector_access(
        **common,
        target_a_copies=target_a_copies,
        target_b_copies=target_b_copies + 1,
        disposable_nonstarters=disposable_nonstarters,
    )
    add_d = two_channel_connector_access(
        **common,
        target_a_copies=target_a_copies,
        target_b_copies=target_b_copies,
        disposable_nonstarters=disposable_nonstarters + 1,
    )

    return SlotMarginalResult(
        baseline=baseline,
        add_target_a=_marginal(baseline, add_a),
        add_target_b=_marginal(baseline, add_b),
        add_disposable=_marginal(baseline, add_d),
    )
