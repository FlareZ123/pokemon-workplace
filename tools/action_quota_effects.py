"""State-dependent grants that modify generic per-turn action quotas.

A quota grant expresses wording that changes the total number of ordinary uses
allowed for one action channel. It is a ceiling replacement rather than an
additional-use token. Player-level play locks remain a separate permission
layer.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Iterable

from turn_action_budget import TurnAction, TurnActionBudget


_QUOTA_ACTIONS = frozenset(
    {
        TurnAction.SUPPORTER,
        TurnAction.STADIUM_PLAY,
        TurnAction.MANUAL_ENERGY_ATTACHMENT,
        TurnAction.RETREAT,
    }
)


@dataclass(frozen=True)
class ActionQuotaGrant:
    source: str
    action: TurnAction
    limit: int
    active: bool = True

    def __post_init__(self) -> None:
        if not self.source:
            raise ValueError("quota grant source must be non-empty")
        if self.action not in _QUOTA_ACTIONS:
            raise ValueError("quota grants apply only to quota-limited actions")
        if self.limit < 0:
            raise ValueError("quota grant limit must be non-negative")


def derive_action_quotas(
    budget: TurnActionBudget,
    grants: Iterable[ActionQuotaGrant] = (),
    *,
    base_supporter_limit: int = 1,
    base_stadium_limit: int = 1,
    base_manual_energy_attachment_limit: int = 1,
    base_retreat_limit: int = 1,
) -> TurnActionBudget:
    """Recompute current limits from basic-rule ceilings plus active grants.

    Usage counts and turn-ended state are preserved. Recomputing from base
    limits is important because a grant can disappear when its source leaves
    play or is suppressed.
    """

    bases = {
        TurnAction.SUPPORTER: base_supporter_limit,
        TurnAction.STADIUM_PLAY: base_stadium_limit,
        TurnAction.MANUAL_ENERGY_ATTACHMENT: base_manual_energy_attachment_limit,
        TurnAction.RETREAT: base_retreat_limit,
    }
    if any(limit < 0 for limit in bases.values()):
        raise ValueError("base action limits must be non-negative")

    limits = dict(bases)
    for grant in grants:
        if grant.active:
            limits[grant.action] = max(limits[grant.action], grant.limit)

    return replace(
        budget,
        supporter_play_limit=limits[TurnAction.SUPPORTER],
        stadium_play_limit=limits[TurnAction.STADIUM_PLAY],
        manual_energy_attachment_limit=limits[
            TurnAction.MANUAL_ENERGY_ATTACHMENT
        ],
        retreat_limit=limits[TurnAction.RETREAT],
    )


DUAL_BRAINS = ActionQuotaGrant(
    source="Magnezone bw8-46 / Dual Brains",
    action=TurnAction.SUPPORTER,
    limit=2,
)
