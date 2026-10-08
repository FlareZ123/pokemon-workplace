"""Fast KO order outcome projection via canonical exchangeable-zone signatures."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

from ko_order_outcome_space import ko_order_outcomes
from ko_order_terminal_projection import TerminalOutcome
from ko_order_zone_signature import terminal_zone_signature
from knockout_zone_routing import discard_pending_with_zone_routes
from simultaneous_knockout_conservation import PendingKnockOutBatch


@dataclass(frozen=True)
class SignatureProjection:
    outcomes: tuple[TerminalOutcome, ...]
    instance_route_outcomes: int
    physical_disposals: int


def project_with_zone_signatures(
    pending: PendingKnockOutBatch,
    programs: Mapping[str, Mapping[str, str]],
    *,
    promote_id: str | None = None,
    precedences: Iterable[tuple[str, str]] = (),
) -> SignatureProjection:
    """Run one conserved disposal per canonical final zone histogram.

    Sound only for the destination-only KO cleanup kernel, from one fixed
    pending batch with one fixed survivor promotion. No authority or trigger
    eligibility decisions are made here.
    """
    groups: dict[
        tuple[tuple[str, str, int], ...],
        tuple[int, int, tuple[tuple[str, ...], ...], dict[str, str]],
    ] = {}
    route_outcomes = ko_order_outcomes(programs, precedences=precedences)
    for route in route_outcomes:
        destinations = dict(route.destinations)
        signature = terminal_zone_signature(
            pending, destinations=destinations
        )
        old = groups.get(signature)
        if old is None:
            groups[signature] = (
                route.order_count,
                1,
                (route.witness_order,),
                destinations,
            )
        else:
            groups[signature] = (
                old[0] + route.order_count,
                old[1] + 1,
                old[2] + (route.witness_order,),
                old[3],
            )

    outcomes = []
    for order_count, route_count, witnesses, destinations in groups.values():
        state = discard_pending_with_zone_routes(
            pending,
            promote_id=promote_id,
            destinations=destinations,
        )
        if state is None:
            raise ValueError("KO route cannot be executed on the pending batch")
        outcomes.append(
            TerminalOutcome(
                state=state,
                order_count=order_count,
                distinct_instance_routes=route_count,
                witness_orders=witnesses,
            )
        )
    return SignatureProjection(
        outcomes=tuple(outcomes),
        instance_route_outcomes=len(route_outcomes),
        physical_disposals=len(outcomes),
    )
