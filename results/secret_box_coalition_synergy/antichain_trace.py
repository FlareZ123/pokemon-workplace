"""Enumerate inclusion-minimal successful Secret Box output masks per state.

This differs from minimum-cardinality size: one state may have both a
singleton successful route and a distinct inclusion-minimal two-output route.
"""

from collections import Counter
from pathlib import Path
import random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))

from aichi_secret_box_output_dependencies import _state_succeeds_with_mask
from aichi_vileplume_secret_box import (
    BASE_DECK, SECRET_BOX_DECK, BOX_ALL_OUTPUTS,
    _raw_state, _state_succeeds,
)


def inclusion_minimal_masks(successes: tuple[bool, ...]) -> tuple[int, ...]:
    """Return the antichain of inclusion-minimal winning output masks."""
    if len(successes) != 16:
        raise ValueError("expected all sixteen four-category outcomes")
    for mask, works in enumerate(successes):
        if works and any(
            successes[subset]
            for subset in range(16)
            if subset != mask and subset & mask == subset
        ):
            continue
        if works and mask:
            yield mask


def main(trials: int = 100_000) -> None:
    rng = random.Random(20261007)
    profiles = Counter()
    pair_counts = Counter()
    marginal = [0] * 16
    singleton_signatures = Counter()
    incremental = 0
    max_antichain = 0

    for _ in range(trials):
        while True:
            order = rng.sample(range(60), 60)
            baseline = _raw_state(BASE_DECK, order)
            if baseline is not None:
                break
        secret = _raw_state(SECRET_BOX_DECK, order)
        assert secret is not None
        if _state_succeeds(baseline):
            continue
        if not _state_succeeds_with_mask(secret, BOX_ALL_OUTPUTS):
            continue
        incremental += 1
        outcomes = tuple(
            _state_succeeds_with_mask(secret, mask)
            for mask in range(16)
        )
        assert outcomes[-1] and not outcomes[0]

        minima = tuple(inclusion_minimal_masks(outcomes))
        singleton = sum(bit for bit in (1, 2, 4, 8) if outcomes[bit])
        assert singleton  # The seeded Aichi incremental set has a singleton.
        assert all(mask.bit_count() <= 2 for mask in minima)
        assert {mask for mask in minima if mask.bit_count() == 1} == {
            bit for bit in (1, 2, 4, 8) if outcomes[bit]
        }

        profiles[(singleton, minima)] += 1
        singleton_signatures[singleton] += 1
        max_antichain = max(max_antichain, len(minima))
        for mask in minima:
            if mask.bit_count() == 2:
                pair_counts[mask] += 1
        for mask, works in enumerate(outcomes):
            marginal[mask] += works

    reference = {
        100_000: (4_175, 8, 375, 9),
        500_000: (20_785, 42, 1_917, 42),
    }
    if trials in reference:
        exp_total, exp_pair6, exp_pair10, exp_pair12 = reference[trials]
        assert incremental == exp_total, incremental
        assert (pair_counts[6], pair_counts[10], pair_counts[12]) == (
            exp_pair6, exp_pair10, exp_pair12
        )
    assert sum(profiles.values()) == incremental
    assert sum(singleton_signatures.values()) == incremental

    print("accepted_trials", trials, "incremental", incremental)
    print("minimal_pair_counts", sorted(pair_counts.items()))
    print("maximum_distinct_minimal_routes_per_state", max_antichain)
    print("profile_count", len(profiles))
    for (singleton, minima), count in sorted(profiles.items()):
        print("profile", singleton, minima, count)
    print("singleton_signatures", sorted(singleton_signatures.items()))
    print("all_mask_success_counts", marginal)
    print("Inclusion-minimal antichain audit passed.")


if __name__ == "__main__":
    main()
