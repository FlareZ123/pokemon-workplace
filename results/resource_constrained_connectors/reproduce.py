"""Validate shared-resource connector allocation against brute force."""

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
from resource_constrained_connectors import (  # noqa: E402
    ResourceActionProfile,
    ResourceConnectorType,
    evaluate_resource_constrained_connectors,
)


def brute_force(
    demand: tuple[int, ...],
    resources: tuple[int, ...],
    connectors: tuple[ResourceConnectorType, ...],
) -> tuple[bool, int]:
    """Enumerate every unused/profile choice for every physical copy."""

    physical: list[
        tuple[str, tuple[ResourceActionProfile, ...]]
    ] = []
    for connector in connectors:
        for _ in range(connector.copies):
            physical.append(
                (connector.name, connector.profiles)
            )

    option_ranges = [
        (None,) + profiles
        for _, profiles in physical
    ]
    exact = False
    minimum_unmet = sum(demand)

    for choices in product(*option_ranges):
        remaining_demand = list(demand)
        remaining_resources = list(resources)
        legal = True

        for profile in choices:
            if profile is None:
                continue

            if any(
                cost > available
                for cost, available in zip(
                    profile.cost,
                    remaining_resources,
                )
            ):
                legal = False
                break

            for index, cost in enumerate(profile.cost):
                remaining_resources[index] -= cost
            for index, supplied in enumerate(profile.output):
                remaining_demand[index] = max(
                    0,
                    remaining_demand[index] - supplied,
                )

        if not legal:
            continue

        unmet = sum(remaining_demand)
        minimum_unmet = min(minimum_unmet, unmet)
        exact = exact or unmet == 0

    return exact, minimum_unmet


def validate() -> None:
    cases = (
        (
            (1, 1),
            (3,),
            (
                ResourceConnectorType(
                    "broad search",
                    2,
                    (
                        ResourceActionProfile(
                            (1, 0),
                            (2,),
                        ),
                        ResourceActionProfile(
                            (0, 1),
                            (2,),
                        ),
                    ),
                ),
            ),
        ),
        (
            (1, 1),
            (4,),
            (
                ResourceConnectorType(
                    "broad search",
                    2,
                    (
                        ResourceActionProfile(
                            (1, 0),
                            (2,),
                        ),
                        ResourceActionProfile(
                            (0, 1),
                            (2,),
                        ),
                    ),
                ),
            ),
        ),
        (
            (1, 1),
            (1,),
            (
                ResourceConnectorType(
                    "supporter A",
                    1,
                    (
                        ResourceActionProfile(
                            (1, 0),
                            (1,),
                        ),
                    ),
                ),
                ResourceConnectorType(
                    "supporter B",
                    1,
                    (
                        ResourceActionProfile(
                            (0, 1),
                            (1,),
                        ),
                    ),
                ),
            ),
        ),
        (
            (1, 1),
            (1,),
            (
                ResourceConnectorType(
                    "multi-axis supporter",
                    1,
                    (
                        ResourceActionProfile(
                            (1, 1),
                            (1,),
                        ),
                    ),
                ),
            ),
        ),
        (
            (2, 1, 1),
            (5, 2),
            (
                ResourceConnectorType(
                    "mixed",
                    3,
                    (
                        ResourceActionProfile(
                            (1, 1, 0),
                            (2, 1),
                        ),
                        ResourceActionProfile(
                            (1, 0, 1),
                            (1, 1),
                        ),
                    ),
                ),
            ),
        ),
    )

    for demand, resources, connectors in cases:
        exact = evaluate_resource_constrained_connectors(
            demand,
            resources,
            connectors,
        )
        brute_exact, brute_unmet = brute_force(
            demand,
            resources,
            connectors,
        )
        if exact.exact_joint_feasible != brute_exact:
            raise AssertionError(
                (demand, resources, exact, brute_exact)
            )
        if exact.minimum_unmet_units != brute_unmet:
            raise AssertionError(
                (demand, resources, exact, brute_unmet)
            )

    no_resource_connectors = (
        ResourceConnectorType(
            "any-card",
            2,
            (
                ResourceActionProfile(
                    (1, 0, 0),
                    (),
                ),
                ResourceActionProfile(
                    (0, 1, 0),
                    (),
                ),
                ResourceActionProfile(
                    (0, 0, 1),
                    (),
                ),
            ),
        ),
    )
    resource_result = evaluate_resource_constrained_connectors(
        (1, 1, 1),
        (),
        no_resource_connectors,
    )
    previous_result = evaluate_connector_capacity(
        (1, 1, 1),
        (
            ConnectorType(
                "any-card",
                2,
                (
                    (1, 0, 0),
                    (0, 1, 0),
                    (0, 0, 1),
                ),
            ),
        ),
    )
    if (
        resource_result.exact_joint_feasible
        != previous_result.exact_joint_feasible
    ):
        raise AssertionError(
            (resource_result, previous_result)
        )
    if (
        resource_result.minimum_unmet_units
        != previous_result.minimum_unmet_units
    ):
        raise AssertionError(
            (resource_result, previous_result)
        )


def main() -> None:
    validate()

    discard_limited = evaluate_resource_constrained_connectors(
        (1, 1),
        (3,),
        (
            ResourceConnectorType(
                "two-discard any-card",
                2,
                (
                    ResourceActionProfile(
                        (1, 0),
                        (2,),
                    ),
                    ResourceActionProfile(
                        (0, 1),
                        (2,),
                    ),
                ),
            ),
        ),
    )
    print("Two individually payable searches sharing only 3 discardable cards")
    print(discard_limited)

    supporter_limited = evaluate_resource_constrained_connectors(
        (1, 1),
        (1,),
        (
            ResourceConnectorType(
                "Supporter route A",
                1,
                (
                    ResourceActionProfile(
                        (1, 0),
                        (1,),
                    ),
                ),
            ),
            ResourceConnectorType(
                "Supporter route B",
                1,
                (
                    ResourceActionProfile(
                        (0, 1),
                        (1,),
                    ),
                ),
            ),
        ),
    )
    print("\nTwo routes sharing one Supporter window")
    print(supporter_limited)

    multi_axis = evaluate_resource_constrained_connectors(
        (1, 1),
        (1,),
        (
            ResourceConnectorType(
                "multi-axis Supporter",
                1,
                (
                    ResourceActionProfile(
                        (1, 1),
                        (1,),
                    ),
                ),
            ),
        ),
    )
    print("\nOne multi-axis action inside one Supporter window")
    print(multi_axis)


if __name__ == "__main__":
    main()
