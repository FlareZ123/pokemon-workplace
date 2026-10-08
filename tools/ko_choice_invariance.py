"""Distinguish source-choice payoff, instance-route, and terminal-state invariance.

All certificates are conditional on the source profiles that actually resolve,
plus fixed pending KO state, promotion and destination-only cleanup semantics.
No source weighting, policy authority or win probability is inferred here.
"""

from __future__ import annotations

from dataclasses import dataclass

from ko_order_outcome_space import OrderOutcome
from ko_order_zone_signature import terminal_zone_signature
from ko_source_scoped_choice import SourceChoiceResult
from simultaneous_knockout_conservation import PendingKnockOutBatch
from source_order_chooser import ConcreteChooserStatus


@dataclass(frozen=True)
class KOChoiceInvariance:
    unresolved_source_ids: tuple[str, ...]
    utility_value_invariant: bool | None
    physical_instance_route_invariant: bool | None
    conserved_terminal_state_invariant: bool | None
    terminal_signatures: tuple[tuple[tuple[str, str, int], ...], ...]


def assess_ko_choice_invariance(
    pending: PendingKnockOutBatch,
    choices: SourceChoiceResult,
) -> KOChoiceInvariance:
    """Compare all tied-optimal outcomes from all individually resolved sources.

    The full terminal-state certificate follows from the independent fixed-
    batch histogram theorem. It considers fixed survival and promotion. If no
    source supplies a complete chooser, invariance is unknown, not true.
    """
    unresolved = tuple(
        choice.source_id
        for choice in choices.choices
        if choice.authority_status != ConcreteChooserStatus.RESOLVED
    )
    routes: tuple[OrderOutcome, ...] = choices.optimal_outcome_union
    if not routes:
        return KOChoiceInvariance(unresolved, None, None, None, ())

    signatures = tuple(sorted({
        terminal_zone_signature(
            pending, destinations=dict(outcome.destinations)
        )
        for outcome in routes
    }))
    return KOChoiceInvariance(
        unresolved_source_ids=unresolved,
        utility_value_invariant=choices.value_invariant,
        physical_instance_route_invariant=choices.instance_destination_invariant,
        conserved_terminal_state_invariant=len(signatures) == 1,
        terminal_signatures=signatures,
    )
