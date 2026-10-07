"""Reproduce Supporter-effect copy provenance and corpus counts."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from build_expanded_legality_baseline import classify_effective_legality
from supporter_effect_copy_channels import (
    CopiedSupporterAttackState,
    SupporterCopyCard,
    execute_impersonation,
    supporter_effect_copy_rows,
)
from turn_action_budget import TurnAction, TurnActionBudget


def main() -> None:
    rows = supporter_effect_copy_rows(ROOT / "resources")
    assert len(rows) == 11
    assert {row["name"] for row in rows} == {
        "Liepard",
        "Mimikyu",
        "Mr. Mime",
        "Ninetales",
        "Oranguru",
        "Sabrina's Suggestion",
        "Smeargle",
        "Sylveon",
    }

    attack_names = {
        row["name"] for row in rows if row["source_class"] == "Attack"
    }
    assert attack_names == {
        "Liepard",
        "Mimikyu",
        "Mr. Mime",
        "Ninetales",
        "Oranguru",
        "Smeargle",
        "Sylveon",
    }
    supporter_names = {
        row["name"] for row in rows if row["source_class"] == "Supporter"
    }
    assert supporter_names == {"Sabrina's Suggestion"}

    sm12 = json.loads(
        (ROOT / "resources" / "cards" / "en" / "sm12.json").read_text(
            encoding="utf-8"
        )
    )
    mimikyu = next(card for card in sm12 if card["id"] == "sm12-96")
    status, _ = classify_effective_legality(mimikyu)
    assert status == "Legal"
    impersonation = next(
        attack for attack in mimikyu["attacks"] if attack["name"] == "Impersonation"
    )
    assert impersonation["text"] == (
        "Discard a Supporter card from your hand. If you do, use the effect "
        "of that card as the effect of this attack."
    )

    swsh4 = json.loads(
        (ROOT / "resources" / "cards" / "en" / "swsh4.json").read_text(
            encoding="utf-8"
        )
    )
    shiftry = next(card for card in swsh4 if card["id"] == "swsh4-12")
    status, _ = classify_effective_legality(shiftry)
    assert status == "Legal"
    substitution = next(
        ability
        for ability in shiftry["abilities"]
        if ability["name"] == "Shifty Substitution"
    )
    assert substitution["text"] == (
        'As long as this Pokémon is in the Active Spot, each Supporter card '
        'in your opponent\'s hand has the effect "Draw 3 cards." '
        "(This happens instead of the card's usual effect.)"
    )

    bw7 = json.loads(
        (ROOT / "resources" / "cards" / "en" / "bw7.json").read_text(encoding="utf-8")
    )
    stoutland = next(card for card in bw7 if card["id"] == "bw7-122")
    status, _ = classify_effective_legality(stoutland)
    assert status == "Legal"
    sentinel = next(a for a in stoutland["abilities"] if a["name"] == "Sentinel")
    assert "Supporter cards from his or her hand" in sentinel["text"]

    bw8 = json.loads(
        (ROOT / "resources" / "cards" / "en" / "bw8.json").read_text(encoding="utf-8")
    )
    liepard = next(card for card in bw8 if card["id"] == "bw8-84")
    status, _ = classify_effective_legality(liepard)
    assert status == "Legal"
    silent_claw = next(a for a in liepard["attacks"] if a["name"] == "Silent Claw")
    assert "Use the effect of that card as the effect of this attack." in silent_claw["text"]

    copied = SupporterCopyCard(
        copy_id="supporter-1",
        name="Example Supporter",
        printed_effect="Search your deck for a Pokémon and put it into your hand.",
    )

    # Fresh turn: Impersonation delegates the physical Supporter's body to the
    # attack and closes the turn without spending the Supporter-play quota.
    fresh = CopiedSupporterAttackState(
        budget=TurnActionBudget(),
        hand=(copied,),
    )
    resolved = execute_impersonation(fresh, copied.copy_id)
    assert resolved is not None
    assert resolved.hand == ()
    assert resolved.discard == (copied,)
    assert resolved.executed_effect == copied.printed_effect
    assert resolved.effect_source_copy_id == copied.copy_id
    assert resolved.execution_class == "attack_effect"
    assert resolved.budget.supporter_plays_used == 0
    assert resolved.budget.turn_ended

    # The same attack channel remains mechanically available after an ordinary
    # Supporter has already consumed the one-Supporter quota.
    after_supporter = TurnActionBudget().consume(TurnAction.SUPPORTER)
    assert after_supporter is not None
    assert not after_supporter.can(TurnAction.SUPPORTER)
    state = CopiedSupporterAttackState(
        budget=after_supporter,
        hand=(copied,),
    )
    second = execute_impersonation(state, copied.copy_id)
    assert second is not None
    assert second.budget.supporter_plays_used == 1
    assert second.budget.turn_ended

    # The attack cannot be executed after the turn has already ended.
    assert execute_impersonation(second, copied.copy_id) is None

    # A stale/non-hand physical Supporter witness cannot be reused.
    assert execute_impersonation(resolved, copied.copy_id) is None

    print("supporter_effect_copy_channels regression: PASS")
    print("effect-copy print rows:", len(rows))
    print("attack-source names:", len(attack_names))


if __name__ == "__main__":
    main()
