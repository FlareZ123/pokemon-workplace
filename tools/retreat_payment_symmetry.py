"""Symmetry orbits for Retreat payments among interchangeable Energy copies.

An orbit represents an action class under permutations of indistinguishable
physical Energy attachments. Caller must certify per-group interchangeability,
including print text, exact effects, destinations, and observer knowledge.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from math import comb, prod


@dataclass(frozen=True)
class InterchangeableEnergy:
    key: str
    copies: int
    provided_units: int

    def __post_init__(self) -> None:
        if not self.key or self.copies < 0 or self.provided_units < 1:
            raise ValueError("Energy class, count or positive unit count invalid")


@dataclass(frozen=True)
class PaymentOrbit:
    paid_per_group: tuple[int, ...]
    physical_multiplicity: int
    inclusion_minimal: bool


def retreat_payment_orbits(
    groups: tuple[InterchangeableEnergy, ...],
    retreat_cost: int,
) -> tuple[PaymentOrbit, ...]:
    """One orbit per class-count payment vector with exact multiplicity."""
    if retreat_cost < 0:
        raise ValueError("Retreat Cost must be nonnegative")
    keys = [group.key for group in groups]
    if len(keys) != len(set(keys)):
        raise ValueError("Group keys must be unique")
    if retreat_cost == 0:
        return (PaymentOrbit((0,) * len(groups), 1, True),)

    result = []
    for chosen in product(*(range(group.copies + 1) for group in groups)):
        card_count = sum(chosen)
        units = sum(n * group.provided_units for n, group in zip(chosen, groups))
        if not (1 <= card_count <= retreat_cost and units >= retreat_cost):
            continue
        min_unit = min(
            group.provided_units for n, group in zip(chosen, groups) if n
        )
        result.append(PaymentOrbit(
            paid_per_group=chosen,
            physical_multiplicity=prod(
                comb(group.copies, n) for n, group in zip(chosen, groups)
            ),
            inclusion_minimal=units - min_unit < retreat_cost,
        ))
    return tuple(result)
