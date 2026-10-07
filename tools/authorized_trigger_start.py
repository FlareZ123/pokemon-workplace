"""Gate ready-effect selection with source-scoped ordering authority."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from ko_trigger_order_authority import OrderingContext
from source_order_chooser import (
    ConcreteChooserAssessment,
    ConcreteChooserStatus,
    OrderingPlayers,
    assess_concrete_ordering_player,
)
from trigger_deferral_kernel import (
    TriggerDeferralState,
    start_ready_effect,
)


class AuthorizedStartStatus(str, Enum):
    STARTED = "started"
    INVALID_START = "invalid_start"
    NO_AUTHORITY_CLAIMS = "no_authority_claims"
    MISSING_PLAYER_CONTEXT = "missing_player_context"
    AUTHORITY_CONFLICT = "authority_conflict"
    UNAUTHORIZED_CHOOSER = "unauthorized_chooser"


@dataclass(frozen=True)
class AuthorizedStartResult:
    status: AuthorizedStartStatus
    state: TriggerDeferralState
    chooser: str | None
    authority_required: bool
    assessment: ConcreteChooserAssessment | None = None


def start_authorized_ready_effect(
    state: TriggerDeferralState,
    *,
    effect_id: str,
    steps: tuple[str, ...],
    context: OrderingContext,
    source_ids: Iterable[str],
    players: OrderingPlayers,
    submitted_by: str | None = None,
) -> AuthorizedStartResult:
    """Start one ready effect without inventing ordering authority.

    A sole ready effect creates no ordering branch, so it can start without
    resolving who would control a choice among alternatives. With multiple ready
    effects, the selected source claims must resolve to one concrete chooser and
    the submitted choice must come from that player.
    """

    if state.active is not None or effect_id not in state.ready_effects:
        return AuthorizedStartResult(
            AuthorizedStartStatus.INVALID_START,
            state,
            None,
            False,
        )

    if len(state.ready_effects) == 1:
        started = start_ready_effect(state, effect_id=effect_id, steps=steps)
        assert started is not None
        return AuthorizedStartResult(
            AuthorizedStartStatus.STARTED,
            started,
            None,
            False,
        )

    assessment = assess_concrete_ordering_player(
        context,
        source_ids,
        players,
    )
    status_map = {
        ConcreteChooserStatus.NO_AUTHORITY_CLAIMS:
            AuthorizedStartStatus.NO_AUTHORITY_CLAIMS,
        ConcreteChooserStatus.MISSING_PLAYER_CONTEXT:
            AuthorizedStartStatus.MISSING_PLAYER_CONTEXT,
        ConcreteChooserStatus.AUTHORITY_CONFLICT:
            AuthorizedStartStatus.AUTHORITY_CONFLICT,
    }
    if assessment.status != ConcreteChooserStatus.RESOLVED:
        return AuthorizedStartResult(
            status_map[assessment.status],
            state,
            None,
            True,
            assessment,
        )

    assert assessment.chooser is not None
    if submitted_by != assessment.chooser:
        return AuthorizedStartResult(
            AuthorizedStartStatus.UNAUTHORIZED_CHOOSER,
            state,
            assessment.chooser,
            True,
            assessment,
        )

    started = start_ready_effect(state, effect_id=effect_id, steps=steps)
    assert started is not None
    return AuthorizedStartResult(
        AuthorizedStartStatus.STARTED,
        started,
        assessment.chooser,
        True,
        assessment,
    )
