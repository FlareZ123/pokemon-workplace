"""Extract the unique required-name Secret Box payment witness."""

from __future__ import annotations

import random

from aichi_secret_box_payment_families import state_payment_family
from aichi_secret_box_payment_required_names import common_names
from aichi_vileplume_secret_box import (
    BASE_DECK,
    SECRET_BOX_DECK,
    _raw_state,
    _state_succeeds,
)


def find_witness(
    trials: int = 100_000,
    *,
    seed: int = 20261007,
):
    rng = random.Random(seed)

    for trial in range(1, trials + 1):
        while True:
            order = rng.sample(range(60), 60)
            baseline_state = _raw_state(BASE_DECK, order)
            if baseline_state is not None:
                break

        secret_state = _raw_state(SECRET_BOX_DECK, order)
        if secret_state is None:
            raise AssertionError("ACE SPEC substitution changed setup acceptance")
        if not _state_succeeds(secret_state) or _state_succeeds(baseline_state):
            continue

        family = state_payment_family(secret_state)
        required = common_names(family)
        if not required:
            continue

        opening = tuple(SECRET_BOX_DECK[index] for index in order[:7])
        prizes = tuple(SECRET_BOX_DECK[index] for index in order[7:13])
        draw = SECRET_BOX_DECK[order[13]]
        hand, remaining, active, top_five = secret_state
        return {
            "trial": trial,
            "opening": opening,
            "prizes": prizes,
            "draw": draw,
            "active": active,
            "top_five": top_five,
            "hand": tuple(sorted(hand.elements())),
            "required_names": tuple(sorted(required)),
            "payment_family": tuple(sorted(family)),
            "remaining_pidgeotto": remaining["Pidgeotto"],
        }

    raise AssertionError("required-name witness not found")


def main() -> None:
    witness = find_witness()
    assert witness["required_names"] == ("Pidgeotto",)
    print(witness)


if __name__ == "__main__":
    main()
