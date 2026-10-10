"""Count physical Retreat payment subsets by class using exact dynamic programming.

Unlike explicit payment-orbit generation, this DP aggregates equivalent
count/energy/minimum-unit states. It supports arbitrary positive unit values.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from math import comb

from retreat_payment_symmetry import InterchangeableEnergy
from retreat_payment_branch_complexity import RetreatPaymentCounts


@dataclass(frozen=True)
class PaymentDPReport:
    counts: RetreatPaymentCounts
    state_count: int
    transitions: int


def count_retreat_payments_dp(
    groups: tuple[InterchangeableEnergy, ...],
    retreat_cost: int,
) -> PaymentDPReport:
    """Count labeled-card legal and inclusion-minimal payments exactly."""
    if retreat_cost < 0:
        raise ValueError("Retreat Cost must be nonnegative")
    if len({group.key for group in groups}) != len(groups):
        raise ValueError("Group keys must be unique")
    if retreat_cost == 0:
        return PaymentDPReport(RetreatPaymentCounts(1, 1), 1, 0)

    # State tuple: selected physical cards, provided units, smallest selected
    # card's unit contribution. Zero denotes no physical card selected.
    states: dict[tuple[int, int, int], int] = {(0, 0, 0): 1}
    total_transitions = 0
    max_states = len(states)
    for group in groups:
        following: dict[tuple[int, int, int], int] = defaultdict(int)
        for (n_selected, provided, min_unit), ways in states.items():
            for picked in range(min(group.copies, retreat_cost - n_selected) + 1):
                minimum = min_unit
                if picked:
                    minimum = min(min_unit, group.provided_units) if min_unit else group.provided_units
                key = (
                    n_selected + picked,
                    provided + picked * group.provided_units,
                    minimum,
                )
                following[key] += ways * comb(group.copies, picked)
                total_transitions += 1
        states = dict(following)
        max_states = max(max_states, len(states))

    full = minimal = 0
    for (selected, supplied, smallest), multiplicity in states.items():
        if 1 <= selected <= retreat_cost and supplied >= retreat_cost:
            full += multiplicity
            if supplied - smallest < retreat_cost:
                minimal += multiplicity

    return PaymentDPReport(
        counts=RetreatPaymentCounts(full, minimal),
        state_count=max_states,
        transitions=total_transitions,
    )
