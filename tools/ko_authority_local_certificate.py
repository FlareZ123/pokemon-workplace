"""Authority-neutral KO state certificate without global order expansion.

The caller's official source-profile claims are retained in the result while
the separate component certificate establishes whether their chooser
disagreement can change a fixed, destination-only conserved terminal state.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

from ko_component_state_invariance import (
    ComponentInvariance, certify_component_ko_invariance,
)
from ko_trigger_order_authority import OrderingContext
from simultaneous_knockout_conservation import PendingKnockOutBatch
from source_order_chooser import (
    ConcreteChooserAssessment, OrderingPlayers,
    assess_concrete_ordering_player,
)


@dataclass(frozen=True)
class AuthorityLocalCertificate:
    authority: ConcreteChooserAssessment
    physical: ComponentInvariance


def certify_authority_neutral_components(
    pending: PendingKnockOutBatch,
    programs: Mapping[str, Mapping[str, str]],
    *,
    context: OrderingContext,
    source_ids: Iterable[str],
    players: OrderingPlayers,
    promote_id: str | None = None,
    precedences: Iterable[tuple[str, str]] = (),
) -> AuthorityLocalCertificate:
    """Compute physical certainty independent of an unresolved chooser.

    This decision-only API intentionally does not estimate how many distinct
    states exist when order-sensitive. The earlier full projection remains
    available when exact global state enumeration is genuinely required.
    """
    authority = assess_concrete_ordering_player(
        context, source_ids, players
    )
    physical = certify_component_ko_invariance(
        pending, programs, promote_id=promote_id,
        precedences=precedences,
    )
    return AuthorityLocalCertificate(authority, physical)
