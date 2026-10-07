"""Exact endpoint-sensitive policy for two coexisting payload connectors.

The modeled singleton payload is a Supporter. One connector is itself a
Supporter and acquires the payload while consuming its ordinary same-turn action
window. The other connector is an Item with a discard gate and preserves that
window.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import comb


@dataclass(frozen=True)
class MixedConnectorPayloadMetrics:
    valid_start_probability: Fraction
    direct_hand_probability: Fraction
    acquisition_probability: Fraction
    optimal_same_turn_execution_probability: Fraction
    supporter_priority_same_turn_execution_probability: Fraction
    next_turn_execution_probability: Fraction
    decision_overlap_probability: Fraction


def _choose(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    return comb(n, k)


def analyze_mixed_payload_policy(
    *,
    deck_size: int = 60,
    hand_size: int = 7,
    prize_count: int = 6,
    starter_copies: int,
    supporter_connector_copies: int,
    item_connector_copies: int,
    dedicated_fodder: int,
    item_discard_cost: int,
) -> MixedConnectorPayloadMetrics:
    """Compare acquisition-indifferent and execution-aware connector policies.

    The target is a singleton Supporter. The Supporter connector has no modeled
    discard cost and consumes the ordinary payload Supporter window. The Item
    connector preserves that window but needs dedicated discard fodder.

    supporter_priority_same_turn_execution_probability represents a policy that
    chooses the Supporter connector whenever it is available, even in overlap
    states where the Item connector could have preserved execution.
    """

    if deck_size <= 0:
        raise ValueError("deck_size must be positive")
    if hand_size <= 0 or hand_size >= deck_size:
        raise ValueError("invalid hand_size")
    if prize_count < 0 or prize_count > deck_size - hand_size:
        raise ValueError("invalid prize_count")
    if min(
        starter_copies,
        supporter_connector_copies,
        item_connector_copies,
        dedicated_fodder,
        item_discard_cost,
    ) < 0:
        raise ValueError("counts must be non-negative")

    payload_copies = 1
    filler = (
        deck_size
        - starter_copies
        - payload_copies
        - supporter_connector_copies
        - item_connector_copies
        - dedicated_fodder
    )
    if filler < 0:
        raise ValueError("represented card classes exceed deck_size")

    total_hands = _choose(deck_size, hand_size)
    valid_weight = 0
    direct_weight = Fraction(0)
    acquisition_weight = Fraction(0)
    optimal_execution_weight = Fraction(0)
    supporter_priority_execution_weight = Fraction(0)
    overlap_weight = Fraction(0)

    for starters_in_hand in range(min(starter_copies, hand_size) + 1):
        for payload_in_hand in range(2):
            for supporter_connectors_in_hand in range(
                min(supporter_connector_copies, hand_size) + 1
            ):
                for item_connectors_in_hand in range(
                    min(item_connector_copies, hand_size) + 1
                ):
                    used = (
                        starters_in_hand
                        + payload_in_hand
                        + supporter_connectors_in_hand
                        + item_connectors_in_hand
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
                            * _choose(
                                supporter_connector_copies,
                                supporter_connectors_in_hand,
                            )
                            * _choose(
                                item_connector_copies,
                                item_connectors_in_hand,
                            )
                            * _choose(dedicated_fodder, fodder_in_hand)
                            * _choose(filler, filler_in_hand)
                        )
                        if ways == 0 or starters_in_hand == 0:
                            continue

                        valid_weight += ways
                        if payload_in_hand:
                            direct_weight += ways
                            acquisition_weight += ways
                            optimal_execution_weight += ways
                            supporter_priority_execution_weight += ways
                            continue

                        supporter_route = supporter_connectors_in_hand > 0
                        item_route = (
                            item_connectors_in_hand > 0
                            and fodder_in_hand >= item_discard_cost
                        )
                        if not supporter_route and not item_route:
                            continue

                        remaining_cards = deck_size - hand_size
                        payload_in_deck_probability = Fraction(
                            remaining_cards - prize_count,
                            remaining_cards,
                        )
                        route_weight = ways * payload_in_deck_probability

                        acquisition_weight += route_weight
                        if item_route:
                            optimal_execution_weight += route_weight
                        if item_route and not supporter_route:
                            supporter_priority_execution_weight += route_weight
                        if item_route and supporter_route:
                            overlap_weight += route_weight

    if valid_weight == 0:
        raise ValueError("no valid starter-containing opening hands")

    direct = direct_weight / valid_weight
    acquisition = acquisition_weight / valid_weight
    optimal_execution = optimal_execution_weight / valid_weight
    supporter_priority_execution = (
        supporter_priority_execution_weight / valid_weight
    )
    overlap = overlap_weight / valid_weight

    if optimal_execution - supporter_priority_execution != overlap:
        raise AssertionError("decision-overlap identity failed")

    return MixedConnectorPayloadMetrics(
        valid_start_probability=Fraction(valid_weight, total_hands),
        direct_hand_probability=direct,
        acquisition_probability=acquisition,
        optimal_same_turn_execution_probability=optimal_execution,
        supporter_priority_same_turn_execution_probability=(
            supporter_priority_execution
        ),
        next_turn_execution_probability=acquisition,
        decision_overlap_probability=overlap,
    )
