"""Reproduce examples where exact Prize knowledge can become uncertain again."""

from __future__ import annotations

import json
from math import comb, isclose, log2
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from prize_knowledge_transitions import (  # noqa: E402
    exact_knowledge_preserved,
    redealt_prize_support,
    uniform_support_entropy_bits,
    unknown_position_swap_support,
)


def _card_by_id(card_id: str):
    set_id = card_id.split("-", 1)[0]
    path = ROOT / "resources" / "cards" / "en" / f"{set_id}.json"
    cards = json.loads(path.read_text(encoding="utf-8"))
    return next(card for card in cards if card["id"] == card_id)


def _texts(card) -> list[str]:
    rows = list(card.get("rules") or [])
    rows.extend(ability.get("text") or "" for ability in card.get("abilities") or [])
    rows.extend(attack.get("text") or "" for attack in card.get("attacks") or [])
    return rows


def main() -> None:
    arc_phone = _card_by_id("swsh11-152")
    assert any(
        "switch that card with 1 of your face-down Prize cards" in text
        for text in _texts(arc_phone)
    )

    rotom_dex = _card_by_id("sm1-131")
    assert any(
        "shuffle them into your deck" in text
        and "put them face down as your Prize cards" in text
        for text in _texts(rotom_dex)
    )

    stinger = _card_by_id("sm6-56")
    assert any(
        "Both players shuffle their Prize cards into their decks" in text
        for text in _texts(stinger)
    )

    pantomime = _card_by_id("det1-11")
    assert any(
        "switch 1 of your face-down Prize cards with the top card of your deck" in text
        for text in _texts(pantomime)
    )

    six_way = unknown_position_swap_support(6)
    assert six_way == 6
    assert isclose(
        uniform_support_entropy_bits(six_way),
        log2(6),
        rel_tol=0.0,
        abs_tol=1e-12,
    )

    first_turn_pool = 52
    redeal_support = redealt_prize_support(first_turn_pool, 6)
    assert redeal_support == comb(52, 6) == 20358520

    assert exact_knowledge_preserved(
        outgoing_identity_known=True,
        incoming_identity_known=True,
    )
    assert not exact_knowledge_preserved(
        outgoing_identity_known=False,
        incoming_identity_known=True,
    )
    assert not exact_knowledge_preserved(
        outgoing_identity_known=True,
        incoming_identity_known=False,
    )
    assert exact_knowledge_preserved(
        outgoing_identity_known=False,
        incoming_identity_known=False,
        resulting_set_reinspected=True,
    )

    print("Arc Phone-style six-Prize known-composition swap")
    print(f"  possible resulting physical Prize sets: {six_way}")
    print(f"  uniform entropy if identities are distinct: {log2(6):.9f} bits")
    print()

    print("Representative full redeal from a 52-card combined pool")
    print(f"  possible physical six-card Prize sets: {redeal_support}")
    print(f"  uniform entropy if identities are distinct: {log2(redeal_support):.9f} bits")
    print()

    print("All Prize-knowledge transition checks passed.")


if __name__ == "__main__":
    main()
