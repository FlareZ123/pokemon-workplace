"""Validate and demonstrate capacity-aware connector semantics."""

from __future__ import annotations

from itertools import product
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from connector_capacity import (  # noqa: E402
    ConnectorType,
    evaluate_connector_capacity,
)


def brute_force(
    demand: tuple[int, ...],
    connectors: tuple[ConnectorType, ...],
) -> tuple[bool, int]:
    """Independently enumerate unused/profile choices for every physical copy."""

    physical: list[tuple[str, tuple[tuple[int, ...], ...]]] = []
    for connector in connectors:
        for _ in range(connector.copies):
            physical.append((connector.name, connector.profiles))

    best_unmet = sum(demand)
    exact = False
    option_ranges = [
        (None,) + profiles
        for _, profiles in physical
    ]

    for choices in product(*option_ranges):
        remaining = list(demand)
        for profile in choices:
            if profile is None:
                continue
            for index, supplied in enumerate(profile):
                remaining[index] = max(
                    0,
                    remaining[index] - supplied,
                )

        unmet = sum(remaining)
        best_unmet = min(best_unmet, unmet)
        exact = exact or unmet == 0

    return exact, best_unmet


def validate() -> None:
    cases = (
        (
            (1, 1, 1),
            (
                ConnectorType(
                    "any-card",
                    1,
                    (
                        (1, 0, 0),
                        (0, 1, 0),
                        (0, 0, 1),
                    ),
                ),
            ),
        ),
        (
            (1, 1, 1),
            (
                ConnectorType(
                    "any-card",
                    3,
                    (
                        (1, 0, 0),
                        (0, 1, 0),
                        (0, 0, 1),
                    ),
                ),
            ),
        ),
        (
            (1, 1, 1),
            (
                ConnectorType(
                    "three-axis",
                    1,
                    ((1, 1, 1),),
                ),
            ),
        ),
        (
            (1, 1, 1, 1),
            (
                ConnectorType(
                    "three-axis",
                    1,
                    ((1, 1, 1, 0),),
                ),
                ConnectorType(
                    "any-card",
                    1,
                    (
                        (1, 0, 0, 0),
                        (0, 1, 0, 0),
                        (0, 0, 1, 0),
                        (0, 0, 0, 1),
                    ),
                ),
            ),
        ),
        (
            (2, 1, 1),
            (
                ConnectorType(
                    "split",
                    2,
                    (
                        (1, 1, 0),
                        (1, 0, 1),
                    ),
                ),
            ),
        ),
    )

    for demand, connectors in cases:
        result = evaluate_connector_capacity(
            demand,
            connectors,
        )
        brute_exact, brute_unmet = brute_force(
            demand,
            connectors,
        )
        if result.exact_joint_feasible != brute_exact:
            raise AssertionError(
                (demand, result, brute_exact)
            )
        if result.minimum_unmet_units != brute_unmet:
            raise AssertionError(
                (demand, result, brute_unmet)
            )


def main() -> None:
    validate()

    any_card_profiles = (
        (1, 0, 0),
        (0, 1, 0),
        (0, 0, 1),
    )

    one_any = evaluate_connector_capacity(
        (1, 1, 1),
        (
            ConnectorType(
                "Computer Search-like",
                1,
                any_card_profiles,
            ),
        ),
    )
    print("One one-shot any-card connector, three missing channels")
    print(one_any)

    three_axis = evaluate_connector_capacity(
        (1, 1, 1),
        (
            ConnectorType(
                "Guzma & Hala-like full mode",
                1,
                ((1, 1, 1),),
            ),
        ),
    )
    print("\nOne true three-axis connector")
    print(three_axis)

    mixed = evaluate_connector_capacity(
        (1, 1, 1, 1),
        (
            ConnectorType(
                "three-axis",
                1,
                ((1, 1, 1, 0),),
            ),
            ConnectorType(
                "any-card",
                1,
                (
                    (1, 0, 0, 0),
                    (0, 1, 0, 0),
                    (0, 0, 1, 0),
                    (0, 0, 0, 1),
                ),
            ),
        ),
    )
    print("\nThree-axis connector plus one any-card connector")
    print(mixed)


if __name__ == "__main__":
    main()
