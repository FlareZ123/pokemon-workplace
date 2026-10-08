"""Certify destination-only KO terminal states despite unresolved order authority.

This is a state projection, not a license for an unauthorized player to choose
an effect order. All candidate orders are included unless external, sourced
precedence constraints have been supplied; invariance over a superset suffices
to show the same physical destination for every admissible order within it.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Mapping

from ko_order_signature_projection import project_with_zone_signatures
from ko_trigger_order_authority import OrderingContext
from simultaneous_knockout_conservation import PendingKnockOutBatch
from source_order_chooser import (
    ConcreteChooserAssessment, OrderingPlayers,
    assess_concrete_ordering_player,
)
from stack_knockout_conservation import StackBoardMaterialState


class PhysicalCertainty(str, Enum):
    INVARIANT = "invariant"
    ORDER_SENSITIVE = "order_sensitive"


@dataclass(frozen=True)
class AuthorityNeutralProjection:
    certainty: PhysicalCertainty
    authority: ConcreteChooserAssessment
    terminal_state: StackBoardMaterialState | None
    witness_order: tuple[str, ...] | None
    possible_instance_routes: int
    possible_terminal_states: int
    candidate_total_orders: int


def project_authority_neutral_ko(
    pending: PendingKnockOutBatch,
    programs: Mapping[str, Mapping[str, str]],
    *,
    context: OrderingContext,
    source_ids: Iterable[str],
    players: OrderingPlayers,
    promote_id: str | None = None,
    precedences: Iterable[tuple[str, str]] = (),
) -> AuthorityNeutralProjection:
    """Project the terminal state only when every order yields that state.

    Authority provenance is returned unchanged. A conflicting, unknown or
    missing chooser does not block a proven destination-only state invariant,
    because the state is unchanged under every candidate order.

    A non-invariant projection never selects or physically executes one
    branch on the user's behalf. If the chooser is known but has not selected
    an order, the same rule applies.
    """
    authority = assess_concrete_ordering_player(
        context, source_ids, players,
    )
    projection = project_with_zone_signatures(
        pending, programs, promote_id=promote_id,
        precedences=precedences,
    )
    total_orders = sum(
        outcome.order_count for outcome in projection.outcomes
    )
    if projection.physical_disposals == 1:
        only = projection.outcomes[0]
        return AuthorityNeutralProjection(
            certainty=PhysicalCertainty.INVARIANT,
            authority=authority,
            terminal_state=only.state,
            witness_order=only.witness_orders[0],
            possible_instance_routes=projection.instance_route_outcomes,
            possible_terminal_states=1,
            candidate_total_orders=total_orders,
        )
    return AuthorityNeutralProjection(
        certainty=PhysicalCertainty.ORDER_SENSITIVE,
        authority=authority,
        terminal_state=None,
        witness_order=None,
        possible_instance_routes=projection.instance_route_outcomes,
        possible_terminal_states=projection.physical_disposals,
        candidate_total_orders=total_orders,
    )
