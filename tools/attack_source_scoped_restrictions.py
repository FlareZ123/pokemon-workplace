"""Resolve attack application gates into concrete source-scoped restrictions."""

from __future__ import annotations

from source_scoped_action_restrictions import (
    SourceScopedActionRestriction,
    resolve_exclusive_restriction,
)
from source_scoped_restriction_activation import RestrictionActivationProfile


def materialize_attack_restriction(
    profile: RestrictionActivationProfile,
    *,
    coin_heads: bool | None = None,
    selected_dimensions: frozenset[str] | None = None,
    prerequisite_succeeded: bool | None = None,
) -> SourceScopedActionRestriction | None:
    """Resolve one attack gate to a concrete pending restriction or no effect."""

    if profile.activation_family != "attack_applied":
        raise ValueError("profile is not attack-applied")

    gate = profile.application_gate
    restriction = profile.restriction

    if gate == "unconditional":
        if (
            coin_heads is not None
            or selected_dimensions is not None
            or prerequisite_succeeded is not None
        ):
            raise ValueError("unconditional restriction received gate outcome")
        return restriction

    if gate == "coin_heads":
        if coin_heads is None:
            raise ValueError("coin result is required")
        if selected_dimensions is not None or prerequisite_succeeded is not None:
            raise ValueError("unexpected outcome supplied for heads-only gate")
        return restriction if coin_heads else None

    if gate == "stadium_discard_if_you_do":
        if prerequisite_succeeded is None:
            raise ValueError("prerequisite result is required")
        if coin_heads is not None or selected_dimensions is not None:
            raise ValueError("unexpected outcome supplied for prerequisite gate")
        return restriction if prerequisite_succeeded else None

    if gate == "player_choice":
        if selected_dimensions is None:
            raise ValueError("selected dimensions are required")
        if coin_heads is not None or prerequisite_succeeded is not None:
            raise ValueError("unexpected outcome supplied for choice gate")
        return resolve_exclusive_restriction(
            restriction,
            selected_dimensions,
        )

    if gate == "coin_branch":
        if coin_heads is None:
            raise ValueError("coin result is required")
        if selected_dimensions is not None or prerequisite_succeeded is not None:
            raise ValueError("unexpected outcome supplied for coin branch")
        options = restriction.exclusive_dimension_options
        if len(options) != 2:
            raise ValueError("coin branch requires exactly two printed options")
        return resolve_exclusive_restriction(
            restriction,
            options[0] if coin_heads else options[1],
        )

    raise ValueError(f"unsupported attack application gate: {gate!r}")
