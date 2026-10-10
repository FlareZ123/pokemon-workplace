"""Check whether Tool+Stadium success exactly tracks held Jet Energy.

This is a paired-state fact for the Aichi Secret Box first-turn core,
not a universal card-effect implication.
"""

from collections import Counter
from pathlib import Path
import random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))

from aichi_secret_box_output_dependencies import _state_succeeds_with_mask
from aichi_vileplume_secret_box import (
    BASE_DECK, SECRET_BOX_DECK, BOX_ALL_OUTPUTS,
    BOX_TOOL_OUTPUT, BOX_STADIUM_OUTPUT,
    _raw_state, _state_succeeds,
)


def main(trials: int = 100_000) -> None:
    rng = random.Random(20261007)
    counts = Counter()
    pair = BOX_TOOL_OUTPUT | BOX_STADIUM_OUTPUT
    for _ in range(trials):
        while True:
            order = rng.sample(range(60), 60)
            base = _raw_state(BASE_DECK, order)
            if base is not None:
                break
        secret = _raw_state(SECRET_BOX_DECK, order)
        assert secret is not None
        if _state_succeeds(base):
            continue
        if not _state_succeeds_with_mask(secret, BOX_ALL_OUTPUTS):
            continue
        hand, deck, active, top = secret
        jet_initial = hand["Jet Energy"] > 0
        pair_success = _state_succeeds_with_mask(secret, pair)
        counts[(jet_initial, pair_success)] += 1

    assert counts[(True, False)] == 0, counts
    assert counts[(False, True)] == 0, counts
    if trials == 100_000:
        assert sum(counts.values()) == 4_175
        assert counts[(True, True)] == 978
    elif trials == 500_000:
        assert sum(counts.values()) == 20_785
        assert counts[(True, True)] == 4_849

    print("accepted_opener_trials", trials)
    print("jet_held_and_pair_success", counts[(True, True)])
    print("jet_held_but_pair_failure", counts[(True, False)])
    print("jet_missing_but_pair_success", counts[(False, True)])
    print("jet_missing_and_pair_failure", counts[(False, False)])
    print("Paired Jet/Tool+Stadium equivalence regression passed.")


if __name__ == "__main__":
    main()
