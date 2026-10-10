"""Exhaustively enumerate all 19,635 generic-filler Item-tail cases.

The six specified Prize cards and five specified opening cards are fixed
physical instances. Two opening filler cards and the first turn draw come
from the remaining generic source class. Any later deck order is immaterial
because neither Jirachi nor Fan Rotom is active and the solver only tests
remaining deck counts for the immediate setup endpoint.
"""

from itertools import combinations
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from stratified_item_payment_tail import (
    BANNED_GENERIC, FORCED_OPENING, PRIZES, pick_indices,
)
from aichi_secret_box_output_dependencies import _state_succeeds_with_mask
from aichi_vileplume_secret_box import (
    BASE_DECK, SECRET_BOX_DECK, _raw_state, _state_succeeds,
)


def main() -> None:
    available = set(range(60))
    prized = pick_indices(PRIZES, available)
    fixed = pick_indices(FORCED_OPENING, available)
    generic = tuple(
        i for i in sorted(available)
        if BASE_DECK[i] not in BANNED_GENERIC
    )
    assert len(generic) == 35
    checked = 0

    for two in combinations(generic, 2):
        for draw in generic:
            if draw in two:
                continue
            rest = sorted(available.difference((*two, draw)))
            assert len(rest) == 46
            # Test two opposite opener-order patterns; active selection can
            # differ, but generic-only active choices are functionally inert.
            for opener in (fixed + list(two), list(two) + fixed):
                order = opener + prized + [draw] + rest
                assert len(order) == len(set(order)) == 60
                base = _raw_state(BASE_DECK, order)
                secret = _raw_state(SECRET_BOX_DECK, order)
                assert base is not None and secret is not None
                if (
                    _state_succeeds(base)
                    or not _state_succeeds_with_mask(secret, 15)
                    or _state_succeeds_with_mask(secret, 14)
                    or not _state_succeeds_with_mask(secret, 1)
                ):
                    raise AssertionError(
                        f"failed filler family: two={two}, draw={draw}"
                    )
            checked += 1

    assert checked == 19_635, checked
    print("Exhaustive distinct two-filler + draw combinations:", checked)
    print("Tested opposite starting-order patterns:", checked * 2)
    print("Every checked state: baseline fail, full success,")
    print("item-only success, no-Item mask failure.")
    print("Exhaustive Item-payment-family regression passed.")


if __name__ == "__main__":
    main()
