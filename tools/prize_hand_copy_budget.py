"""Prune impossible hidden hand worlds using legal full-deck group counts."""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping
from math import isclose

from prize_unknown_hand_composition import (
    LatentHandCompositionBelief,
    ObserverLatentHandCompositionBeliefs,
)


def condition_joint_hand_on_copy_budget(
    before: ObserverLatentHandCompositionBeliefs,
    *,
    total_deck_copies: Mapping[str, int],
    publicly_known_elsewhere: Mapping[str, int] | None = None,
) -> ObserverLatentHandCompositionBeliefs:
    """Use necessary copy ceilings; outside counts exclude every modeled zone.

    Modeled zones are the deck top, remaining Prizes, tagged hand card, and
    other hand cards. The filter does not prove sufficiency of a whole world.
    """
    elsewhere = publicly_known_elsewhere or {}
    if any(not isinstance(n, int) or n < 0 for n in total_deck_copies.values()):
        raise ValueError("deck copy counts must be nonnegative integers")
    if any(not isinstance(n, int) or n < 0 for n in elsewhere.values()):
        raise ValueError("public copy counts must be nonnegative integers")
    if set(elsewhere) - set(total_deck_copies):
        raise ValueError("public group has no corresponding deck capacity")
    if any(elsewhere[g] > total_deck_copies[g] for g in elsewhere):
        raise ValueError("public copies exceed the initial deck inventory")

    conditioned = []
    for observer, belief in before.beliefs:
        if set(belief.groups) - set(total_deck_copies):
            raise ValueError("every modeled group requires an inventory count")
        surviving = []
        evidence = 0.0
        for (top, prizes, tag, other), mass in belief.masses:
            required = Counter(g for g in (top, tag, *prizes) if g is not None)
            required.update({g: n for g, n in zip(belief.groups, other) if n})
            feasible = all(
                n + elsewhere.get(g, 0) <= total_deck_copies[g]
                for g, n in required.items()
            )
            if feasible:
                surviving.append(((top, prizes, tag, other), mass))
                evidence += mass
        if isclose(evidence, 0.0, abs_tol=1e-15, rel_tol=0.0):
            raise ValueError(f"no copy-feasible world for {observer}")
        conditioned.append((
            observer,
            LatentHandCompositionBelief(
                belief.groups,
                belief.face_up,
                tuple((state, mass / evidence) for state, mass in surviving),
            ),
        ))
    return ObserverLatentHandCompositionBeliefs(tuple(conditioned))
