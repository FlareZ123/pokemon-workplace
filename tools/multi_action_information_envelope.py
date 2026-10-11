"""Exact finite-action value of observing a hidden strategic state.

This is a belief-state calculation. A search's payments and legal-action gates
must be modeled *before* constructing the post-search action table.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Iterable, Mapping


@dataclass(frozen=True)
class ActionEnvelope:
    fixed_payoffs: tuple[tuple[str, Fraction], ...]
    best_fixed_action: str
    best_fixed_value: Fraction
    observed_value: Fraction
    information_value: Fraction
    challenger_regrets: tuple[tuple[str, Fraction], ...]
    pairwise_lower_bound: Fraction
    sum_upper_bound: Fraction
    optimal_after_observation: tuple[str, ...]


def action_information_envelope(
    states: Iterable[tuple[Fraction, Mapping[str, Fraction]]],
) -> ActionEnvelope:
    """Return exact expected best fixed vs state-contingent action payoffs.

    Each row contains (prior mass, action-name -> payoff). Every row must
    offer the same positive number of candidate actions. Ties prefer the
    first action's insertion order, to keep a reproducible policy.

    The bound is relative to the optimal *fixed* action j:
      max_i E[(u_i-u_j)_+] <= information value
      information value <= sum_i E[(u_i-u_j)_+].
    For exactly two actions both bounds are equalities.
    """
    rows = tuple((Fraction(w), {str(k): Fraction(v) for k, v in p.items()})
                 for w, p in states)
    if not rows or not rows[0][1]:
        raise ValueError("at least one state and one action required")
    actions = tuple(rows[0][1])
    keys = set(actions)
    if (any(w < 0 or set(p) != keys for w, p in rows)
            or sum((w for w, _ in rows), Fraction()) != 1):
        raise ValueError("nonnegative normalized prior and identical action sets required")

    means = tuple((a, sum((w * p[a] for w, p in rows), Fraction()))
                  for a in actions)
    baseline = max(v for _, v in means)
    chosen = next(a for a, v in means if v == baseline)
    observed_choices = tuple(max(actions, key=lambda a: p[a]) for _, p in rows)
    observed = sum((w * p[a] for (w, p), a in zip(rows, observed_choices)), Fraction())
    regrets = tuple((a, sum((w * max(Fraction(), p[a] - p[chosen])
                             for w, p in rows), Fraction()))
                    for a in actions if a != chosen)
    lower = max((v for _, v in regrets), default=Fraction())
    upper = sum((v for _, v in regrets), Fraction())
    gain = observed - baseline
    assert lower <= gain <= upper
    return ActionEnvelope(means, chosen, baseline, observed, gain,
                          regrets, lower, upper, observed_choices)
