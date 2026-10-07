"""Fixed-size slot marginals for multi-output connector models.

This compares adding one direct out to any required target channel with adding
one currently disposable card, while holding deck size fixed. The underlying
same-window probabilities come from `multi_channel_connector_access()`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from multi_channel_connector import multi_channel_connector_access


@dataclass(frozen=True)
class MultiOutputSlotMarginals:
    """One-slot marginal values around a fixed baseline composition."""

    baseline_joint_access: float
    add_target_gains: tuple[float, ...]
    add_disposable_gain: float

    @property
    def weakest_direct_gain(self) -> float:
        return min(self.add_target_gains)

    @property
    def strongest_direct_gain(self) -> float:
        return max(self.add_target_gains)

    @property
    def disposable_to_weakest_direct_ratio(self) -> float:
        return self.add_disposable_gain / self.weakest_direct_gain

    @property
    def disposable_to_strongest_direct_ratio(self) -> float:
        return self.add_disposable_gain / self.strongest_direct_gain


def fixed_size_multi_output_marginals(
    deck_size: int,
    prize_count: int,
    *,
    starter_cards: int,
    target_counts: Sequence[int],
    disposable_nonstarters: int,
    discard_cost: int,
    connector_capacity: int,
    opening_hand_size: int = 7,
) -> MultiOutputSlotMarginals:
    """Return exact one-slot marginals for direct outs and discardability.

    The baseline must contain at least one protected non-starter filler card.
    Every comparison replaces exactly one such filler, so deck size is fixed.
    """

    targets = tuple(target_counts)
    protected_fillers = (
        deck_size
        - starter_cards
        - sum(targets)
        - 1
        - disposable_nonstarters
    )
    if protected_fillers < 1:
        raise ValueError("baseline needs a protected filler slot to replace")

    common = dict(
        deck_size=deck_size,
        prize_count=prize_count,
        starter_cards=starter_cards,
        disposable_nonstarters=disposable_nonstarters,
        discard_cost=discard_cost,
        connector_capacity=connector_capacity,
        opening_hand_size=opening_hand_size,
    )
    baseline = multi_channel_connector_access(
        **common,
        target_counts=targets,
    ).joint_access

    direct_gains = []
    for index in range(len(targets)):
        changed = list(targets)
        changed[index] += 1
        access = multi_channel_connector_access(
            **common,
            target_counts=tuple(changed),
        ).joint_access
        direct_gains.append(access - baseline)

    disposable_access = multi_channel_connector_access(
        deck_size,
        prize_count,
        starter_cards=starter_cards,
        target_counts=targets,
        disposable_nonstarters=disposable_nonstarters + 1,
        discard_cost=discard_cost,
        connector_capacity=connector_capacity,
        opening_hand_size=opening_hand_size,
    ).joint_access

    return MultiOutputSlotMarginals(
        baseline_joint_access=baseline,
        add_target_gains=tuple(direct_gains),
        add_disposable_gain=disposable_access - baseline,
    )


def first_symmetric_disposable_crossover(
    channel_count: int,
    target_copies_per_channel: int,
    *,
    deck_size: int = 60,
    prize_count: int = 6,
    starter_cards: int = 12,
    discard_cost: int = 3,
    opening_hand_size: int = 7,
) -> int | None:
    """Return the first D where +1 disposable beats +1 direct out.

    Every target channel has the same number of outs, and the connector can
    satisfy all missing channels simultaneously.
    """

    targets = (target_copies_per_channel,) * channel_count
    max_disposable = deck_size - starter_cards - sum(targets) - 2

    for disposable in range(max_disposable + 1):
        result = fixed_size_multi_output_marginals(
            deck_size,
            prize_count,
            starter_cards=starter_cards,
            target_counts=targets,
            disposable_nonstarters=disposable,
            discard_cost=discard_cost,
            connector_capacity=channel_count,
            opening_hand_size=opening_hand_size,
        )
        if result.add_disposable_gain > result.strongest_direct_gain:
            return disposable

    return None
