"""Reproduce state-dependent quota-grant behavior."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from action_quota_effects import (
    ActionQuotaGrant,
    DUAL_BRAINS,
    derive_action_quotas,
)
from build_expanded_legality_baseline import classify_effective_legality
from turn_action_budget import TurnAction, TurnActionBudget


def main() -> None:
    cards = json.loads(
        (ROOT / "resources" / "cards" / "en" / "bw8.json").read_text(
            encoding="utf-8"
        )
    )
    magnezone = next(card for card in cards if card["id"] == "bw8-46")
    status, _ = classify_effective_legality(magnezone)
    assert status == "Legal"
    ability = next(
        ability
        for ability in magnezone["abilities"]
        if ability["name"] == "Dual Brains"
    )
    assert ability["text"] == "During your turn, you may play 2 Supporter cards."

    base = TurnActionBudget()
    ordinary = derive_action_quotas(base)
    assert ordinary.supporter_play_limit == 1

    enabled = derive_action_quotas(base, (DUAL_BRAINS,))
    assert enabled.supporter_play_limit == 2

    after_one = enabled.consume(TurnAction.SUPPORTER)
    assert after_one is not None
    assert after_one.supporter_plays_used == 1
    assert after_one.can(TurnAction.SUPPORTER)

    # If the Ability is suppressed after the first play, recomputing from the
    # basic rule removes its grant and closes the second Supporter window.
    suppressed_grant = ActionQuotaGrant(
        source=DUAL_BRAINS.source,
        action=DUAL_BRAINS.action,
        limit=DUAL_BRAINS.limit,
        active=False,
    )
    suppressed = derive_action_quotas(after_one, (suppressed_grant,))
    assert suppressed.supporter_play_limit == 1
    assert suppressed.supporter_plays_used == 1
    assert not suppressed.can(TurnAction.SUPPORTER)

    restored = derive_action_quotas(suppressed, (DUAL_BRAINS,))
    assert restored.supporter_play_limit == 2
    assert restored.can(TurnAction.SUPPORTER)

    after_two = restored.consume(TurnAction.SUPPORTER)
    assert after_two is not None
    assert after_two.supporter_plays_used == 2
    assert not after_two.can(TurnAction.SUPPORTER)

    # Historical usage remains valid if the grant later disappears. The current
    # limit can be lower than already-consumed usage, but no further use opens.
    post_two_suppression = derive_action_quotas(
        after_two,
        (suppressed_grant,),
    )
    assert post_two_suppression.supporter_play_limit == 1
    assert post_two_suppression.supporter_plays_used == 2
    assert not post_two_suppression.can(TurnAction.SUPPORTER)

    # Total-limit wording is idempotent. Two active copies still establish a
    # ceiling of two rather than adding two extra uses each.
    duplicated = derive_action_quotas(base, (DUAL_BRAINS, DUAL_BRAINS))
    assert duplicated.supporter_play_limit == 2

    print("action_quota_effects regression: PASS")


if __name__ == "__main__":
    main()
