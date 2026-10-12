"""Exact information value of first-action commitment under hidden states.

This is an abstract decision operator; action legality/success must be
supplied by a validated Pokémon TCG transition model.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Iterable


@dataclass(frozen=True)
class ActionWorld:
    probability: Fraction
    winning_first_actions: frozenset[str]


@dataclass(frozen=True)
class FirstActionInformationValue:
    clairvoyant: Fraction
    nonanticipative: Fraction
    information_gap: Fraction
    best_first_actions: tuple[str, ...]
    universal_winning_action: str | None


def evaluate_first_action_information(
    worlds: Iterable[ActionWorld],
    *,
    legal_first_actions: Iterable[str],
) -> FirstActionInformationValue:
    """Expected binary success when first action precedes hidden-zone search.

    Later actions may be optimized separately within each hidden world.
    All named first actions are assumed legally playable under the common
    observed state. Each winning_first_actions set contains only actions
    whose optimal *subsequent* continuation succeeds in that world.
    """
    rows = tuple(worlds)
    actions = tuple(dict.fromkeys(legal_first_actions))
    if not rows or not actions:
        raise ValueError("a nonempty world support and action set are required")
    if any(not isinstance(row.probability, Fraction)
           or row.probability < 0 for row in rows):
        raise ValueError("weights must be nonnegative exact Fractions")
    total = sum((row.probability for row in rows), Fraction())
    if total <= 0:
        raise ValueError("world support must have positive mass")
    legal = set(actions)
    if any(not row.winning_first_actions <= legal for row in rows):
        raise ValueError("hidden-world success refers to an illegal first action")

    clairvoyant = sum(
        (row.probability for row in rows if row.winning_first_actions),
        Fraction(),
    ) / total
    by_action = {
        action: sum(
            (row.probability for row in rows
             if action in row.winning_first_actions),
            Fraction(),
        ) / total
        for action in actions
    }
    nonanticipative = max(by_action.values())
    best = tuple(
        action for action in actions if by_action[action] == nonanticipative
    )
    winning = [
        row.winning_first_actions
        for row in rows
        if row.probability > 0 and row.winning_first_actions
    ]
    universal = next(
        (action for action in actions
         if all(action in witnesses for witnesses in winning)),
        None,
    ) if winning else actions[0]

    assert nonanticipative <= clairvoyant
    assert (universal is not None) == (clairvoyant == nonanticipative)
    return FirstActionInformationValue(
        clairvoyant,
        nonanticipative,
        clairvoyant - nonanticipative,
        best,
        universal,
    )
