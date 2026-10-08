"""Project ordered KO destination outcomes onto conserved terminal game states.

The ordering model enumerates destination vectors over materialized instance
IDs. Once disposed, the existing physical identity ledger dematerializes copies
and may merge several instance-distinct routes into the same final game state.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

from ko_order_outcome_space import ko_order_outcomes
from knockout_zone_routing import discard_pending_with_zone_routes
from simultaneous_knockout_conservation import PendingKnockOutBatch
from stack_knockout_conservation import StackBoardMaterialState


@dataclass(frozen=True)
class TerminalOutcome:
    state: StackBoardMaterialState
    order_count: int
    distinct_instance_routes: int
    witness_orders: tuple[tuple[str, ...], ...]


def project_terminal_outcomes(
    pending: PendingKnockOutBatch,
    programs: Mapping[str, Mapping[str, str]],
    *,
    promote_id: str | None = None,
    precedences: Iterable[tuple[str, str]] = (),
) -> tuple[TerminalOutcome, ...]:
    """Group destination orders by exactly equal conserved terminal states.

    Every individual route is executed against the same unchanged pending
    batch. Equivalence uses the full final StackBoardMaterialState (board,
    exchangeable counts and any surviving materialized instances), not a
    coarse count of zone labels alone. If an endpoint is not executable under
    the supplied promotion and route program, reject the entire input.
    """
    grouped: list[TerminalOutcome] = []
    for route_outcome in ko_order_outcomes(
        programs,
        precedences=precedences,
    ):
        state = discard_pending_with_zone_routes(
            pending,
            promote_id=promote_id,
            destinations=dict(route_outcome.destinations),
        )
        if state is None:
            raise ValueError("KO route cannot be executed on the pending batch")
        for index, prior in enumerate(grouped):
            if prior.state == state:
                grouped[index] = TerminalOutcome(
                    state=state,
                    order_count=prior.order_count + route_outcome.order_count,
                    distinct_instance_routes=prior.distinct_instance_routes + 1,
                    witness_orders=prior.witness_orders + (
                        route_outcome.witness_order,
                    ),
                )
                break
        else:
            grouped.append(
                TerminalOutcome(
                    state=state,
                    order_count=route_outcome.order_count,
                    distinct_instance_routes=1,
                    witness_orders=(route_outcome.witness_order,),
                )
            )
    return tuple(grouped)
