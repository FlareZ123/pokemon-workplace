"""Exact bottleneck-regime scans for one-slot connector marginals.

This module maps which one-slot substitution has the largest local gain in the
two-channel connector-domination model:

- add one direct out to target A;
- add one direct out to target B;
- add one currently disposable non-starter.

It uses the analytically Prize-collapsed exact solver so dense grids remain
cheap while preserving the same model semantics.
"""

from __future__ import annotations

from dataclasses import dataclass

from connector_domination import (
    ConnectorDominationResult,
    two_channel_connector_access_collapsed,
)


@dataclass(frozen=True)
class RegimePoint:
    """One exact fixed-size local marginal comparison."""

    target_a_copies: int
    target_b_copies: int
    disposable_nonstarters: int
    discard_cost: int
    baseline_realistic_access: float
    add_target_a_gain: float
    add_target_b_gain: float
    add_disposable_gain: float
    winner: str

    @property
    def best_direct_gain(self) -> float:
        return max(self.add_target_a_gain, self.add_target_b_gain)

    @property
    def direct_over_disposable_gap(self) -> float:
        return self.best_direct_gain - self.add_disposable_gain


@dataclass(frozen=True)
class RegimeSummary:
    """Summary of an exact grid scan."""

    discard_cost: int
    points: tuple[RegimePoint, ...]
    target_a_wins: int
    target_b_wins: int
    target_ties: int
    disposable_wins: int
    mixed_ties: int
    minimum_direct_over_disposable_gap: float
    minimum_gap_point: RegimePoint
    maximum_disposable_gain: float
    maximum_disposable_point: RegimePoint


def _realistic(result: ConnectorDominationResult) -> float:
    return result.capacity_aware_gated_access


def _point(
    *,
    deck_size: int,
    prize_count: int,
    starter_cards: int,
    target_a_copies: int,
    target_b_copies: int,
    disposable_nonstarters: int,
    discard_cost: int,
    opening_hand_size: int,
    tolerance: float,
) -> RegimePoint:
    common = dict(
        deck_size=deck_size,
        prize_count=prize_count,
        starter_cards=starter_cards,
        discard_cost=discard_cost,
        opening_hand_size=opening_hand_size,
    )

    baseline = two_channel_connector_access_collapsed(
        **common,
        target_a_copies=target_a_copies,
        target_b_copies=target_b_copies,
        disposable_nonstarters=disposable_nonstarters,
    )
    add_a = two_channel_connector_access_collapsed(
        **common,
        target_a_copies=target_a_copies + 1,
        target_b_copies=target_b_copies,
        disposable_nonstarters=disposable_nonstarters,
    )
    add_b = two_channel_connector_access_collapsed(
        **common,
        target_a_copies=target_a_copies,
        target_b_copies=target_b_copies + 1,
        disposable_nonstarters=disposable_nonstarters,
    )
    add_d = two_channel_connector_access_collapsed(
        **common,
        target_a_copies=target_a_copies,
        target_b_copies=target_b_copies,
        disposable_nonstarters=disposable_nonstarters + 1,
    )

    gains = {
        "target_a": _realistic(add_a) - _realistic(baseline),
        "target_b": _realistic(add_b) - _realistic(baseline),
        "disposable": _realistic(add_d) - _realistic(baseline),
    }
    best = max(gains.values())
    winners = tuple(
        name for name, value in gains.items()
        if abs(value - best) <= tolerance
    )

    if winners == ("target_a",):
        winner = "target_a"
    elif winners == ("target_b",):
        winner = "target_b"
    elif winners == ("disposable",):
        winner = "disposable"
    elif set(winners) == {"target_a", "target_b"}:
        winner = "target_tie"
    else:
        winner = "mixed_tie"

    return RegimePoint(
        target_a_copies=target_a_copies,
        target_b_copies=target_b_copies,
        disposable_nonstarters=disposable_nonstarters,
        discard_cost=discard_cost,
        baseline_realistic_access=_realistic(baseline),
        add_target_a_gain=gains["target_a"],
        add_target_b_gain=gains["target_b"],
        add_disposable_gain=gains["disposable"],
        winner=winner,
    )


def scan_bottleneck_regimes(
    *,
    discard_cost: int,
    deck_size: int = 60,
    prize_count: int = 6,
    starter_cards: int = 12,
    target_copy_values: tuple[int, ...] = (1, 2, 3, 4),
    disposable_values: tuple[int, ...] = tuple(range(36)),
    opening_hand_size: int = 7,
    tolerance: float = 1e-12,
) -> RegimeSummary:
    """Exhaust an exact local-marginal grid.

    Every point holds deck size fixed. Increasing one modeled category by one
    therefore converts one protected non-starter filler slot into that
    category.

    Infeasible points are rejected by the underlying exact solver rather than
    silently skipped.
    """

    if discard_cost < 0:
        raise ValueError("discard_cost must be non-negative")
    if not target_copy_values:
        raise ValueError("target_copy_values must not be empty")
    if not disposable_values:
        raise ValueError("disposable_values must not be empty")

    points = tuple(
        _point(
            deck_size=deck_size,
            prize_count=prize_count,
            starter_cards=starter_cards,
            target_a_copies=target_a,
            target_b_copies=target_b,
            disposable_nonstarters=disposable,
            discard_cost=discard_cost,
            opening_hand_size=opening_hand_size,
            tolerance=tolerance,
        )
        for target_a in target_copy_values
        for target_b in target_copy_values
        for disposable in disposable_values
    )

    minimum_gap_point = min(
        points,
        key=lambda point: point.direct_over_disposable_gap,
    )
    maximum_disposable_point = max(
        points,
        key=lambda point: point.add_disposable_gain,
    )

    return RegimeSummary(
        discard_cost=discard_cost,
        points=points,
        target_a_wins=sum(point.winner == "target_a" for point in points),
        target_b_wins=sum(point.winner == "target_b" for point in points),
        target_ties=sum(point.winner == "target_tie" for point in points),
        disposable_wins=sum(point.winner == "disposable" for point in points),
        mixed_ties=sum(point.winner == "mixed_tie" for point in points),
        minimum_direct_over_disposable_gap=(
            minimum_gap_point.direct_over_disposable_gap
        ),
        minimum_gap_point=minimum_gap_point,
        maximum_disposable_gain=maximum_disposable_point.add_disposable_gain,
        maximum_disposable_point=maximum_disposable_point,
    )
