"""Combine exact conditional reset payoffs with nested natural-access events."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class AccessLimitedPolicy:
    conditional_success_by_limit: tuple[Fraction, ...]
    joint_success_by_limit: tuple[Fraction, ...]
    conditional_expected_uses: Fraction


def combine_access_and_stopping(
    conditional_access: tuple[Fraction, ...],
    full_access_success: tuple[Fraction, ...],
    witness_probability: Fraction,
) -> AccessLimitedPolicy:
    """Mix no-resource/limited-resource policy over observed Item availability.

    Resource tiers are nested: tier j is the event that all Items needed to
    execute j adaptive resets are accessible. Success values are those for
    fully funded policy with <=j resets, indexed from j=0. Within the
    conditioned initial K1 witness, original deck order must be independent
    of naturally observed Item counts. Under that assumption:

    P(success at ceiling k) = success[0] + sum_{j=1}^k
        P(resource_tier_j) * (success[j] - success[j-1]).

    The policy always uses a first Ticket whenever it has one and baseline
    access fails, then continues only when reinspection reveals failure and
    enough Items remain. Item costs are not assigned a utility penalty.
    """
    k = len(conditional_access)
    if len(full_access_success) != k + 1:
        raise ValueError("success curve must include the zero-reset baseline")
    if not 0 <= witness_probability <= 1:
        raise ValueError("witness probability must be between zero and one")
    if any(not 0 <= p <= 1 for p in conditional_access):
        raise ValueError("access probabilities must be between zero and one")
    if any(conditional_access[i] < conditional_access[i+1] for i in range(k-1)):
        raise ValueError("resource-tier access probabilities must be nested")
    if any(not 0 <= s <= 1 for s in full_access_success):
        raise ValueError("success probabilities must be between zero and one")
    if any(full_access_success[i] > full_access_success[i+1] for i in range(k)):
        raise ValueError("adaptive success curve must be nondecreasing")

    success = [full_access_success[0]]
    for i, access in enumerate(conditional_access, start=1):
        success.append(success[-1] + access * (full_access_success[i] - full_access_success[i-1]))

    expected = sum((access * (1 - full_access_success[i-1])
                    for i, access in enumerate(conditional_access, start=1)), Fraction(0))
    return AccessLimitedPolicy(tuple(success),
                               tuple(witness_probability * s for s in success), expected)
