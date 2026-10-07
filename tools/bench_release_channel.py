from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ReleaseChannel:
    name: str
    action_class: str
    requires_bench_slot: bool = False
    ends_turn: bool = False
    requires_item_permission: bool = False
    requires_supporter_window: bool = False
    requires_stadium_play: bool = False
    additional_cost_payable: bool = True


def evaluate_release(
    channel: ReleaseChannel,
    *,
    bench_occupancy: int,
    bench_capacity: int,
    items_allowed: bool = True,
    supporter_used: bool = False,
    stadium_played: bool = False,
) -> dict[str, Any]:
    reasons: list[str] = []

    if channel.requires_bench_slot and bench_occupancy >= bench_capacity:
        reasons.append("no open Bench slot")
    if channel.requires_item_permission and not items_allowed:
        reasons.append("Items are not playable")
    if channel.requires_supporter_window and supporter_used:
        reasons.append("Supporter window already used")
    if channel.requires_stadium_play and stadium_played:
        reasons.append("Stadium play already used")
    if not channel.additional_cost_payable:
        reasons.append("additional cost is not payable")

    mechanically_usable = not reasons
    enables_same_turn_continuation = mechanically_usable and not channel.ends_turn
    return {
        "name": channel.name,
        "action_class": channel.action_class,
        "mechanically_usable": mechanically_usable,
        "enables_same_turn_continuation": enables_same_turn_continuation,
        "blocking_reasons": reasons,
    }


def eternal_zone_full_contraction_examples() -> list[dict[str, Any]]:
    state = {
        "bench_occupancy": 5,
        "bench_capacity": 5,
        "items_allowed": True,
        "supporter_used": False,
        "stadium_played": True,
    }
    channels = (
        ReleaseChannel(
            "Field Blower",
            "Item",
            requires_item_permission=True,
        ),
        ReleaseChannel(
            "Lost Vacuum",
            "Item",
            requires_item_permission=True,
            additional_cost_payable=True,
        ),
        ReleaseChannel(
            "Worker",
            "Supporter",
            requires_supporter_window=True,
        ),
        ReleaseChannel(
            "Pumpkaboo / Chien-Pao",
            "Bench-entry Ability",
            requires_bench_slot=True,
        ),
        ReleaseChannel(
            "play another Stadium",
            "Stadium",
            requires_stadium_play=True,
        ),
        ReleaseChannel(
            "attack-based Stadium removal",
            "Attack",
            ends_turn=True,
        ),
    )
    return [evaluate_release(channel, **state) for channel in channels]


if __name__ == "__main__":
    for row in eternal_zone_full_contraction_examples():
        print(row)
