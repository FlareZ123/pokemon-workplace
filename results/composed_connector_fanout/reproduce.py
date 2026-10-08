"""Reproduce composed connector fan-out for the Aichi Secret Box chain."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from temporal_resource_connectors import (
    TemporalActionProfile,
    TemporalConnectorType,
    evaluate_temporal_resource_connectors,
)


# Terminal demand: Bunnelby access, TM: Evolution, Jet Energy.
DEMAND = (1, 1, 1)

# Resource dimensions:
# (discardable hand material, Supporter window, Tag Call token,
#  Guzma & Hala token, Artazon token)
ITEM_CHAIN = (
    TemporalConnectorType(
        "Secret Box -> Item",
        1,
        (
            TemporalActionProfile(
                output=(0, 0, 0),
                cost=(3, 0, 0, 0, 0),
                production=(0, 0, 1, 0, 0),
            ),
        ),
    ),
    TemporalConnectorType(
        "Tag Call",
        1,
        (
            TemporalActionProfile(
                output=(0, 0, 0),
                cost=(0, 0, 1, 0, 0),
                # The second TAG TEAM card is represented as one unit of
                # newly available payment material.
                production=(1, 0, 0, 1, 0),
            ),
        ),
    ),
    TemporalConnectorType(
        "Guzma & Hala",
        1,
        (
            TemporalActionProfile(
                output=(0, 1, 1),
                cost=(2, 1, 0, 1, 0),
                production=(0, 0, 0, 0, 1),
            ),
        ),
    ),
    TemporalConnectorType(
        "Artazon",
        1,
        (
            TemporalActionProfile(
                output=(1, 0, 0),
                cost=(0, 0, 0, 0, 1),
                production=(0, 0, 0, 0, 0),
            ),
        ),
    ),
)

SUPPORTER_CHAIN = (
    TemporalConnectorType(
        "Secret Box -> Supporter",
        1,
        (
            TemporalActionProfile(
                output=(0, 0, 0),
                cost=(3, 0, 0, 0, 0),
                production=(0, 0, 0, 1, 0),
            ),
        ),
    ),
    ITEM_CHAIN[2],
    ITEM_CHAIN[3],
)

ITEM_CHAIN_NO_SECOND_TAG = (
    ITEM_CHAIN[0],
    TemporalConnectorType(
        "Tag Call",
        1,
        (
            TemporalActionProfile(
                output=(0, 0, 0),
                cost=(0, 0, 1, 0, 0),
                production=(0, 0, 0, 1, 0),
            ),
        ),
    ),
    ITEM_CHAIN[2],
    ITEM_CHAIN[3],
)


def evaluate(connectors, discardable: int, supporter_window: int = 1):
    return evaluate_temporal_resource_connectors(
        DEMAND,
        (discardable, supporter_window, 0, 0, 0),
        connectors,
    )


def main() -> None:
    item_four = evaluate(ITEM_CHAIN, 4)
    item_three = evaluate(ITEM_CHAIN, 3)
    item_no_second_four = evaluate(ITEM_CHAIN_NO_SECOND_TAG, 4)
    item_no_second_five = evaluate(ITEM_CHAIN_NO_SECOND_TAG, 5)
    supporter_four = evaluate(SUPPORTER_CHAIN, 4)
    supporter_five = evaluate(SUPPORTER_CHAIN, 5)
    item_no_supporter_window = evaluate(ITEM_CHAIN, 5, supporter_window=0)

    if not item_four.feasible:
        raise AssertionError("Item chain should be feasible from four payment cards")
    if item_three.feasible:
        raise AssertionError("Item chain should fail from only three payment cards")
    if item_no_second_four.feasible:
        raise AssertionError("Without Tag Call replenishment, four should fail")
    if not item_no_second_five.feasible:
        raise AssertionError("Without replenishment, five should succeed")
    if supporter_four.feasible:
        raise AssertionError("Direct Supporter chain should fail from four")
    if not supporter_five.feasible:
        raise AssertionError("Direct Supporter chain should succeed from five")
    if item_no_supporter_window.feasible:
        raise AssertionError("The chain must consume the Supporter window")

    names = tuple(name for name, _profile in item_four.witness_actions)
    expected_names = (
        "Secret Box -> Item",
        "Tag Call",
        "Guzma & Hala",
        "Artazon",
    )
    if names != expected_names:
        raise AssertionError(f"{names!r} != {expected_names!r}")
    if item_four.ending_resources != (0, 0, 0, 0, 0):
        raise AssertionError(item_four.ending_resources)

    print("item_chain_start_4=feasible")
    print(f"item_chain_witness={names}")
    print(f"item_chain_end_resources={item_four.ending_resources}")
    print("item_chain_start_3=infeasible")
    print("item_chain_without_second_tag_start_4=infeasible")
    print("item_chain_without_second_tag_start_5=feasible")
    print("supporter_chain_start_4=infeasible")
    print("supporter_chain_start_5=feasible")
    print("item_chain_supporter_window_0=infeasible")
    print("All composed connector fan-out checks passed.")


if __name__ == "__main__":
    main()
