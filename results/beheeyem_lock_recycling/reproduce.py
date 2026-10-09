"""Ideal-access physical pipeline for repeated Beheeyem Mysterious Noise."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import comb
import json


@dataclass(frozen=True)
class TurnWitness:
    turn: int
    attacker_basic: int
    recycled_basic_rebenched: tuple[int, ...]
    evolved_from_prior_turn: bool
    anchor_free_retreat_used: bool
    beheeyem_shuffled_back: bool
    triple_acceleration_shuffled_back: bool


def ideal_recycling_sequence(basic_copies: int, last_turn: int) -> tuple[TurnWitness, ...]:
    """Oracle access, one normal evolution and one attachment per attack turn.

    Elgyem 0 begins Active on turn one. Any other Elgyem copies begin
    Benched on turn one, with an already prepared Float Stone lock anchor
    available to become Active after turn-two Mysterious Noise.
    """
    born_on_board = {basic: 1 for basic in range(basic_copies)}
    elgyem_in_deck: set[int] = set()
    anchor_active = False
    attack_records: list[TurnWitness] = []

    for turn in range(2, last_turn + 1):
        recycled = tuple(sorted(elgyem_in_deck))
        for basic in recycled:
            born_on_board[basic] = turn
            elgyem_in_deck.remove(basic)
        ready = [basic for basic, born in born_on_board.items() if born < turn]
        if not ready:
            break
        attacker = min(ready)
        if turn == 2:
            assert attacker == 0 and not anchor_active
        else:
            assert anchor_active  # Anchor's Float Stone provides zero retreat cost.
        # The single Beheeyem and single Triple Acceleration Energy are
        # retrieved from the deck each turn after their previous self-shuffle.
        born_on_board.pop(attacker)
        elgyem_in_deck.add(attacker)
        anchor_active = True  # Shuffle removes the attacker; promote the anchor.
        attack_records.append(
            TurnWitness(
                turn=turn,
                attacker_basic=attacker,
                recycled_basic_rebenched=recycled,
                evolved_from_prior_turn=True,
                anchor_free_retreat_used=turn > 2,
                beheeyem_shuffled_back=True,
                triple_acceleration_shuffled_back=True,
            )
        )
    return tuple(attack_records)


def all_copies_prized_probability(copies: int) -> Fraction:
    """Probability six random Prizes contain all copies of one component."""
    return Fraction(comb(60 - copies, 6 - copies), comb(60, 6))


def either_component_fully_prized(a: int, b: int) -> Fraction:
    """Joint prize collapse for disjoint Beheeyem and TAE categories."""
    overlap = Fraction(comb(60 - a - b, 6 - a - b), comb(60, 6))
    return all_copies_prized_probability(a) + all_copies_prized_probability(b) - overlap


def main() -> None:
    lone = ideal_recycling_sequence(1, last_turn=8)
    pair = ideal_recycling_sequence(2, last_turn=8)
    assert len(lone) == 1  # Elgyem shuffles itself away on turn two.
    assert [x.turn for x in pair] == list(range(2, 9))
    assert [x.attacker_basic for x in pair] == [0, 1, 0, 1, 0, 1, 0]
    assert all(x.evolved_from_prior_turn for x in pair)
    assert all(x.beheeyem_shuffled_back and x.triple_acceleration_shuffled_back for x in pair)
    assert sum(x.anchor_free_retreat_used for x in pair) == 6
    assert all(len(x.recycled_basic_rebenched) == 1 for x in pair[1:])

    results = {
        "one_elgyem_consecutive_attacks": len(lone),
        "two_elgyem_attacking_turns": [x.turn for x in pair],
        "two_elgyem_attacker_sequence": [x.attacker_basic for x in pair],
        "anchor_zero_cost_retreats_after_first_attack": 6,
        "single_beheeyem_and_single_tae_prize_collapse_percent": round(
            float(either_component_fully_prized(1, 1)) * 100, 6
        ),
        "two_each_prize_collapse_percent": round(
            float(either_component_fully_prized(2, 2)) * 100, 6
        ),
    }
    assert results["single_beheeyem_and_single_tae_prize_collapse_percent"] == 19.152542
    assert results["two_each_prize_collapse_percent"] == 1.691839
    print(json.dumps(results, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
