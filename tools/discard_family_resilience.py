"""Structural robustness metrics for families of feasible discard witnesses."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from math import comb
from typing import Iterable


@dataclass(frozen=True)
class DiscardFamilyMetrics:
    witness_count: int
    candidate_count: int
    forced_cards: frozenset[str]
    minimum_protection_cut: int


def _normalize(
    witnesses: Iterable[Iterable[str]],
) -> tuple[frozenset[str], ...]:
    unique = {
        frozenset(witness)
        for witness in witnesses
    }
    if not unique or any(not witness for witness in unique):
        raise ValueError("witness family must contain non-empty witnesses")
    return tuple(sorted(unique, key=lambda w: (len(w), tuple(sorted(w)))))


def minimum_protection_cut(
    witnesses: Iterable[Iterable[str]],
) -> int:
    """Smallest number of protected cards that intersects every witness."""
    family = _normalize(witnesses)
    candidates = sorted(set().union(*family))
    for size in range(1, len(candidates) + 1):
        for protected in combinations(candidates, size):
            protected_set = frozenset(protected)
            if all(witness & protected_set for witness in family):
                return size
    raise AssertionError("finite non-empty witness family must have a protection cut")


def uniform_protection_survival(
    witnesses: Iterable[Iterable[str]],
    protected_count: int,
    *,
    candidate_universe: Iterable[str] | None = None,
) -> float:
    """Probability some witness remains when p candidate names are protected.

    Protection sets are uniformly sampled from an explicit candidate universe,
    defaulting to the names that appear in at least one witness. A witness
    survives when none of its cards is protected.
    """
    family = _normalize(witnesses)
    witness_cards = set().union(*family)
    candidates = sorted(
        witness_cards if candidate_universe is None else set(candidate_universe)
    )
    if not witness_cards <= set(candidates):
        raise ValueError("candidate_universe must contain every witness card")
    if protected_count < 0 or protected_count > len(candidates):
        raise ValueError("protected_count must fit the candidate universe")
    total = comb(len(candidates), protected_count)
    surviving = 0
    for protected in combinations(candidates, protected_count):
        protected_set = frozenset(protected)
        if any(not (witness & protected_set) for witness in family):
            surviving += 1
    return surviving / total


def discard_family_metrics(
    witnesses: Iterable[Iterable[str]],
) -> DiscardFamilyMetrics:
    family = _normalize(witnesses)
    candidates = frozenset().union(*family)
    forced = frozenset.intersection(*family)
    return DiscardFamilyMetrics(
        witness_count=len(family),
        candidate_count=len(candidates),
        forced_cards=forced,
        minimum_protection_cut=minimum_protection_cut(family),
    )
