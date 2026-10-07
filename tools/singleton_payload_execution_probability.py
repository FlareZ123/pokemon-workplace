"""Exact opening/Prize probability for one singleton Trainer payload.

The model conditions on an opening hand containing at least one ordinary starter.
A singleton payload either begins in hand or can be searched from the remaining
deck by a connector already in hand. Connector payment is represented by a pool
of dedicated discardable cards.

The acquisition endpoint and same-turn execution endpoint are reported
separately. The latter depends on whether the connector leaves the payload's
required action window available after resolving.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import comb


@dataclass(frozen=True)
class SingletonPayloadMetrics:
    valid_start_probability: Fraction
    direct_hand_probability: Fraction
    acquisition_probability: Fraction
    same_turn_execution_probability: Fraction
    connector_acquisition_increment: Fraction
    connector_execution_increment: Fraction


def _choose(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    return comb(n, k)


def analyze_singleton_payload(
    *,
    deck_size: int = 60,
    hand_size: int = 7,
    prize_count: int = 6,
    starter_copies: int,
    connector_copies: int,
    dedicated_fodder: int,
    connector_discard_cost: int,
    connector_preserves_payload_window: bool,
    direct_payload_window_open: bool = True,
) -> SingletonPayloadMetrics:
    """Return exact valid-start-conditioned acquisition and execution rates.

    The singleton payload, starters, connector copies, dedicated fodder, and
    filler are disjoint card classes. Only dedicated fodder may pay the modeled
    connector discard cost.

    If the singleton payload is absent from the opening hand, it is still in the
    post-hand deck/Prize pool. Search succeeds only when the payload avoids the
    Prize cards.
    """

    if deck_size <= 0:
        raise ValueError("deck_size must be positive")
    if hand_size <= 0 or hand_size >= deck_size:
        raise ValueError("hand_size must be between 1 and deck_size - 1")
    if prize_count < 0 or prize_count > deck_size - hand_size:
        raise ValueError("invalid prize_count")
    if min(
        starter_copies,
        connector_copies,
        dedicated_fodder,
        connector_discard_cost,
    ) < 0:
        raise ValueError("counts must be non-negative")

    payload_copies = 1
    filler = (
        deck_size
        - starter_copies
        - payload_copies
        - connector_copies
        - dedicated_fodder
    )
    if filler < 0:
        raise ValueError("represented card classes exceed deck_size")

    total_hands = _choose(deck_size, hand_size)
    valid_weight = 0
    direct_weight = Fraction(0)
    acquisition_weight = Fraction(0)
    execution_weight = Fraction(0)

    for starters_in_hand in range(min(starter_copies, hand_size) + 1):
        for payload_in_hand in range(2):
            for connectors_in_hand in range(
                min(connector_copies, hand_size) + 1
            ):
                used = (
                    starters_in_hand
                    + payload_in_hand
                    + connectors_in_hand
                )
                if used > hand_size:
                    continue
                for fodder_in_hand in range(
                    min(dedicated_fodder, hand_size - used) + 1
                ):
                    filler_in_hand = hand_size - used - fodder_in_hand
                    if filler_in_hand < 0 or filler_in_hand > filler:
                        continue

                    ways = (
                        _choose(starter_copies, starters_in_hand)
                        * _choose(payload_copies, payload_in_hand)
                        * _choose(connector_copies, connectors_in_hand)
                        * _choose(dedicated_fodder, fodder_in_hand)
                        * _choose(filler, filler_in_hand)
                    )
                    if ways == 0 or starters_in_hand == 0:
                        continue

                    valid_weight += ways
                    if payload_in_hand:
                        direct_weight += ways
                        acquisition_weight += ways
                        if direct_payload_window_open:
                            execution_weight += ways
                        continue

                    connector_usable = (
                        connectors_in_hand > 0
                        and fodder_in_hand >= connector_discard_cost
                    )
                    if not connector_usable:
                        continue

                    remaining_cards = deck_size - hand_size
                    payload_in_deck_probability = Fraction(
                        remaining_cards - prize_count,
                        remaining_cards,
                    )
                    route_weight = ways * payload_in_deck_probability
                    acquisition_weight += route_weight
                    if (
                        direct_payload_window_open
                        and connector_preserves_payload_window
                    ):
                        execution_weight += route_weight

    if valid_weight == 0:
        raise ValueError("no valid starter-containing opening hands")

    valid_start_probability = Fraction(valid_weight, total_hands)
    direct_probability = direct_weight / valid_weight
    acquisition_probability = acquisition_weight / valid_weight
    execution_probability = execution_weight / valid_weight

    return SingletonPayloadMetrics(
        valid_start_probability=valid_start_probability,
        direct_hand_probability=direct_probability,
        acquisition_probability=acquisition_probability,
        same_turn_execution_probability=execution_probability,
        connector_acquisition_increment=(
            acquisition_probability - direct_probability
        ),
        connector_execution_increment=(
            execution_probability
            - (
                direct_probability
                if direct_payload_window_open
                else Fraction(0)
            )
        ),
    )
