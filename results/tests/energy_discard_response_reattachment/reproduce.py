"""Independent physical Energy slot backtracker for the response/attachment test."""
from __future__ import annotations

from fractions import Fraction
from pathlib import Path

from tools.energy_discard_continuation_frontier import DRAGON_ENERGIES, build as base_build
from tools.energy_discard_continuation_disruption import response_state
from tools.energy_discard_response_reattachment import (
    HAND_STATES, RESPONSES, apply_attachment, build, expected_readiness, payment_matrix,
)


def independent_attack_ready(cards: list[dict], cost: list[str]) -> bool:
    slots = [set(card["types"]) for card in cards for _ in range(int(card["units"]))]

    def assign(index: int, used: frozenset[int]) -> bool:
        if index == len(cost):
            return True
        for slot_index, available_types in enumerate(slots):
            if slot_index in used:
                continue
            if cost[index] == "Colorless" or cost[index] in available_types:
                if assign(index + 1, used | {slot_index}):
                    return True
        return False

    return assign(0, frozenset())


def run() -> None:
    root = Path("resources")
    fixture = base_build(root)
    cost = fixture["future_attack"]["cost"]
    rows = payment_matrix(root)
    independent_checks = 0
    for payment, row in zip(fixture["payments"], rows):
        removed = set(payment["discard_indices"])
        remaining = [card for i, card in enumerate(DRAGON_ENERGIES) if i not in removed]
        for response in RESPONSES:
            reacted, available = response_state(remaining, response)
            assert available == row["outcomes"][response]["counter_available"]
            for hand in HAND_STATES:
                post = apply_attachment(reacted, response, hand)
                assert independent_attack_ready(post, cost) == row["outcomes"][response]["ready_by_hand"][hand]
                independent_checks += 1
    assert independent_checks == 48
    # A one-Grass future hand gives a strict protection advantage versus
    # either special-Energy response, but does not price the attachment.
    certain_grass = {hand: Fraction(int(hand == "basic_grass")) for hand in HAND_STATES}
    tests = 0
    for hammer_step in range(11):
        for temple_step in range(11 - hammer_step):
            response = {"enhanced_hammer": Fraction(hammer_step, 10),
                        "temple_of_sinnoh": Fraction(temple_step, 10),
                        "none": Fraction(10 - hammer_step - temple_step, 10)}
            outcomes = [expected_readiness(row, response, certain_grass) for row in rows]
            assert outcomes[0] == 1
            assert outcomes[1:] == [response["none"]] * 3
            tests += 1
    assert tests == 66
    result = build(root)
    assert result["outcome_count"] == 48
    print("physical-slot independent checks:", independent_checks)
    print("exact counter-prior lattice checks:", tests)
    print("readiness under toy priors:", result["readiness"])
    print("PASS: all 48 outcome cells and 66 probability-lattice examples")


if __name__ == "__main__":
    run()
