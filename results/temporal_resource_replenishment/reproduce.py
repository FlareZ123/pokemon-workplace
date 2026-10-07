"""Reproduce the replenishable-resource connector counterexample."""

from __future__ import annotations

from itertools import permutations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from temporal_resource_connectors import (
    TemporalActionProfile,
    TemporalConnectorType,
    evaluate_temporal_resource_connectors,
)


def main() -> None:
    box = TemporalConnectorType(
        "Secret Box-like",
        1,
        (TemporalActionProfile(output=(1, 0), cost=(3,), production=(2,)),),
    )
    gnh = TemporalConnectorType(
        "Guzma & Hala-like",
        1,
        (TemporalActionProfile(output=(0, 1), cost=(2,), production=(0,)),),
    )

    result = evaluate_temporal_resource_connectors(
        demand=(1, 1),
        starting_resources=(3,),
        connectors=(box, gnh),
    )
    assert result.feasible
    assert result.minimum_unmet_units == 0
    assert result.ending_resources == (0,)
    assert [name for name, _profile in result.witness_actions or ()] == [
        "Secret Box-like",
        "Guzma & Hala-like",
    ]

    low_production_box = TemporalConnectorType(
        "Low-production Box-like",
        1,
        (TemporalActionProfile(output=(1, 0), cost=(3,), production=(1,)),),
    )
    insufficient = evaluate_temporal_resource_connectors(
        demand=(1, 1),
        starting_resources=(3,),
        connectors=(low_production_box, gnh),
    )
    assert not insufficient.feasible
    assert insufficient.minimum_unmet_units == 1

    enough_initial_stock = evaluate_temporal_resource_connectors(
        demand=(1, 1),
        starting_resources=(4,),
        connectors=(low_production_box, gnh),
    )
    assert enough_initial_stock.feasible

    producer = TemporalConnectorType(
        "Producer-only",
        1,
        (TemporalActionProfile(output=(0,), cost=(0,), production=(1,)),),
    )
    consumer = TemporalConnectorType(
        "Consumer",
        1,
        (TemporalActionProfile(output=(1,), cost=(1,), production=(0,)),),
    )
    producer_only = evaluate_temporal_resource_connectors(
        demand=(1,),
        starting_resources=(0,),
        connectors=(producer, consumer),
    )
    assert producer_only.feasible
    assert [name for name, _profile in producer_only.witness_actions or ()] == [
        "Producer-only",
        "Consumer",
    ]

    # Independent two-action enumeration confirms that only Box -> G&H works
    # in the 3-stock, 2-production case.
    legal_orders = []
    actions = {
        "Secret Box-like": ((1, 0), 3, 2),
        "Guzma & Hala-like": ((0, 1), 2, 0),
    }
    for order in permutations(actions):
        stock = 3
        supplied = [0, 0]
        legal = True
        for name in order:
            output, cost, production = actions[name]
            if cost > stock:
                legal = False
                break
            stock = stock - cost + production
            supplied = [a + b for a, b in zip(supplied, output)]
        if legal and all(value >= 1 for value in supplied):
            legal_orders.append(order)

    assert legal_orders == [("Secret Box-like", "Guzma & Hala-like")]

    print("starting_stock=3")
    print("static_cost_sum=5")
    print("box_production=2")
    print("witness=Secret Box-like -> Guzma & Hala-like")
    print("ending_stock=0")
    print("All temporal resource replenishment checks passed.")


if __name__ == "__main__":
    main()
