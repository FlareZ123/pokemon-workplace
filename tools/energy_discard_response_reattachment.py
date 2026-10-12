"""Regidrago Dragon Impact: opponent response, one future hand attachment.

The payment is chosen before the response and before learning which future
Energy is in hand. Output probabilities are conditional on supplied *toy*
independent categorical priors, never a claim about tournament draw rates.
"""
from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path
from typing import Any

from tools.energy_discard_continuation_frontier import DRAGON_ENERGIES, build as base_build
from tools.energy_discard_continuation_disruption import response_state
from tools.energy_discard_solver import attack_cost_ready

RESPONSES = ("none", "enhanced_hammer", "temple_of_sinnoh")
HAND_STATES = ("none", "basic_grass", "basic_fire", "double_dragon")
FRESH_ENERGY = {
    "basic_grass": {"name": "Basic Grass Energy", "units": 1, "types": ["Grass"], "basic": True},
    "basic_fire": {"name": "Basic Fire Energy", "units": 1, "types": ["Fire"], "basic": True},
    "double_dragon": {"name": "Double Dragon Energy", "units": 2,
                      "types": ["Grass", "Fire", "Water", "Lightning", "Psychic",
                                "Fighting", "Darkness", "Metal", "Fairy", "Colorless"],
                      "basic": False},
}


def apply_attachment(
    cards: list[dict[str, Any]], response: str, hand: str,
) -> list[dict[str, Any]]:
    """One optional manual Energy attachment onto a surviving Dragon."""
    if hand == "none":
        return list(cards)
    fresh = dict(FRESH_ENERGY[hand])
    if response == "temple_of_sinnoh" and hand == "double_dragon":
        fresh["units"] = 1
        fresh["types"] = ["Colorless"]
    return [*cards, fresh]


def payment_matrix(resources_root: Path) -> list[dict[str, Any]]:
    baseline = base_build(resources_root)
    cost = baseline["future_attack"]["cost"]
    assert cost == ["Grass", "Grass", "Fire"]
    rows = []
    for payment in baseline["payments"]:
        removed = set(payment["discard_indices"])
        remaining = [card for i, card in enumerate(DRAGON_ENERGIES) if i not in removed]
        outcomes = {}
        for response in RESPONSES:
            reacted, available = response_state(remaining, response)
            outcomes[response] = {
                "counter_available": available,
                "ready_by_hand": {
                    hand: attack_cost_ready(apply_attachment(reacted, response, hand), cost)
                    for hand in HAND_STATES
                },
            }
        rows.append({
            "payment": payment["discard_names"],
            "discarded_cards": payment["physical_cards_discarded"],
            "outcomes": outcomes,
        })
    return rows


def expected_readiness(
    row: dict[str, Any],
    response_probability: dict[str, Fraction],
    hand_probability: dict[str, Fraction],
) -> Fraction:
    """Precommitted payment's exact readiness under independent toy priors."""
    assert set(response_probability) == set(RESPONSES)
    assert set(hand_probability) == set(HAND_STATES)
    assert sum(response_probability.values()) == 1
    assert sum(hand_probability.values()) == 1
    assert all(0 <= p <= 1 for p in (*response_probability.values(), *hand_probability.values()))
    return sum(
        (response_probability[response] * hand_probability[hand]
         for response in RESPONSES for hand in HAND_STATES
         if row["outcomes"][response]["ready_by_hand"][hand]),
        Fraction(0),
    )


def build(resources_root: Path) -> dict[str, Any]:
    rows = payment_matrix(resources_root)
    assert len(rows) == 4
    dde_payment = next(row for row in rows if row["discarded_cards"] == 1)
    basic_payments = [row for row in rows if row["discarded_cards"] == 2]
    assert len(basic_payments) == 3
    # Order: no attachment, Grass, Fire, Double Dragon from hand.
    expected = {
        "dde": {"none": (False, True, False, True),
                "enhanced_hammer": (False, True, False, True),
                "temple_of_sinnoh": (False, True, False, False)},
        "basics": {"none": (True, True, True, True),
                   "enhanced_hammer": (False, False, False, True),
                   "temple_of_sinnoh": (False, False, False, False)},
    }
    for kind, family in (("dde", [dde_payment]), ("basics", basic_payments)):
        for row in family:
            for response in RESPONSES:
                actual = tuple(row["outcomes"][response]["ready_by_hand"].values())
                assert actual == expected[kind][response], (kind, response, actual)
                if response == "enhanced_hammer":
                    assert row["outcomes"][response]["counter_available"] == (kind == "basics")

    # Deliberately hypothetical independent priors. Fraction avoids rounding.
    hand_prior = {"none": Fraction(3, 10), "basic_grass": Fraction(1, 2),
                  "basic_fire": Fraction(1, 10), "double_dragon": Fraction(1, 10)}
    counter_high = {"none": Fraction(3, 10), "enhanced_hammer": Fraction(3, 5),
                    "temple_of_sinnoh": Fraction(1, 10)}
    counter_low = {"none": Fraction(4, 5), "enhanced_hammer": Fraction(1, 10),
                   "temple_of_sinnoh": Fraction(1, 10)}
    high_dde = expected_readiness(dde_payment, counter_high, hand_prior)
    high_basics = expected_readiness(basic_payments[0], counter_high, hand_prior)
    low_dde = expected_readiness(dde_payment, counter_low, hand_prior)
    low_basics = expected_readiness(basic_payments[0], counter_low, hand_prior)
    assert (high_dde, high_basics, low_dde, low_basics) == (
        Fraction(59, 100), Fraction(9, 25), Fraction(59, 100), Fraction(81, 100))
    assert all(expected_readiness(row, counter_high, hand_prior) == high_basics
               for row in basic_payments)
    # For Temple probability t, future Grass probability g, DDE d, the
    # equality threshold is h = ((1-t)*(1-d)-g)/(1-d), provided d<1.
    threshold = Fraction(31, 90)
    g, d, t = (hand_prior["basic_grass"], hand_prior["double_dragon"],
               counter_high["temple_of_sinnoh"])
    assert threshold == ((1 - t) * (1 - d) - g) / (1 - d)
    return {
        "source_cards": ["swsh12-136", "sv9-114", "xy6-97", "sv6-148", "swsh10-155"],
        "timing": "discard during copied attack; opponent single response; one next-turn hand attachment",
        "outcome_count": len(rows) * len(RESPONSES) * len(HAND_STATES),
        "rows": rows,
        "hypothetical_priors": {
            "hand": {k: str(v) for k, v in hand_prior.items()},
            "high_counter": {k: str(v) for k, v in counter_high.items()},
            "low_counter": {k: str(v) for k, v in counter_low.items()},
        },
        "readiness": {"high_counter_discard_dde": str(high_dde),
                      "high_counter_retain_dde": str(high_basics),
                      "low_counter_discard_dde": str(low_dde),
                      "low_counter_retain_dde": str(low_basics)},
        "hammer_probability_indifference_boundary_at_fixed_t_and_hand": str(threshold),
    }


if __name__ == "__main__":
    print(json.dumps(build(Path("resources")), indent=2))
