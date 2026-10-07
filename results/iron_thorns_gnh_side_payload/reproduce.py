"""Validate the Aichi Iron Thorns Guzma & Hala Tool side-payload model."""
from __future__ import annotations

import itertools
import math
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from iron_thorns_gnh_side_payload import Counts, exact


def brute_small() -> tuple[Fraction, Fraction, tuple[Fraction, ...]]:
    cards = tuple(
        ["I0", "I1", "TAG", "GH", "M", "DCE", "TOOL0", "TOOL1"]
        + [f"F{i}" for i in range(4)]
    )
    total = discard = with_tool = 0
    dist = [0, 0, 0]

    for opening in itertools.combinations(cards, 3):
        if not any(card.startswith("I") for card in opening):
            continue
        after_opening = tuple(card for card in cards if card not in opening)
        for prizes in itertools.combinations(after_opening, 2):
            after_prizes = tuple(card for card in after_opening if card not in prizes)
            for draw in after_prizes:
                total += 1
                hand = list(opening) + [draw]
                hand.remove(next(card for card in hand if card.startswith("I")))
                deck = list(after_prizes)
                deck.remove(draw)

                m_hand = "M" in hand
                dce_hand = "DCE" in hand
                resources = (m_hand or "M" in deck) and (dce_hand or "DCE" in deck)
                gh_access = "GH" in hand or ("TAG" in hand and "GH" in deck)
                if m_hand and dce_hand:
                    continue
                if not resources or not gh_access or dce_hand:
                    continue

                discard += 1
                tools = sum(card.startswith("TOOL") for card in deck)
                dist[tools] += 1
                if tools:
                    with_tool += 1

    return (
        Fraction(discard, total),
        Fraction(with_tool, total),
        tuple(Fraction(value, discard) for value in dist),
    )


def pct(value: Fraction) -> str:
    return f"{100 * float(value):.9f}%"


def main() -> None:
    toy = exact(
        Counts(
            iron=2,
            tag=1,
            gh=1,
            mountain=1,
            dce=1,
            tools=2,
            deck_size=12,
            opening=3,
            prizes=2,
        )
    )
    brute_discard, brute_tool, brute_dist = brute_small()
    assert toy.mediated_discard == brute_discard
    assert toy.mediated_discard_with_tool == brute_tool
    assert toy.tool_distribution_given_discard == brute_dist

    lists = {
        "Kazuma": Counts(dce=1, tools=3),
        "Ryoya": Counts(dce=3, tools=3),
        "Kohei": Counts(dce=1, tools=4),
    }
    expected_discard = {
        "Kazuma": 0.2894023064010956,
        "Ryoya": 0.25894650078307357,
        "Kohei": 0.2894023064010956,
    }

    print("iron_thorns_gnh_side_payload: all assertions passed")
    for name, counts in lists.items():
        result = exact(counts)
        assert math.isclose(
            float(result.mediated_discard),
            expected_discard[name],
            rel_tol=1e-14,
            abs_tol=1e-14,
        )
        print(
            name,
            f"discard_route={pct(result.mediated_discard)}",
            f"tool_available_given_route={pct(result.tool_available_given_discard)}",
            f"expected_tools_in_deck={float(result.expected_tools_in_deck_given_discard):.9f}",
        )


if __name__ == "__main__":
    main()
