"""Regression for Aichi Active-swap discard-family locality."""

from aichi_active_discard_swap_locality import simulate_swap_locality


def main() -> None:
    result = simulate_swap_locality(100_000, seed=20261007)

    assert result.policy_difference_states == 16_905
    assert result.comparable == {
        "core": 10_343,
        "pidgeot": 9_586,
        "stoutland": 7_947,
        "dual": 6_936,
        "item": 9_578,
        "item_pidgeot": 5_384,
        "item_stoutland": 4_484,
    }
    assert result.added_edges == {
        "core": 48_235,
        "pidgeot": 43_399,
        "stoutland": 35_895,
        "dual": 26_500,
        "item": 43_429,
        "item_pidgeot": 8_233,
        "item_stoutland": 7_045,
    }
    assert result.removed_edges == {
        "core": 40_627,
        "pidgeot": 34_564,
        "stoutland": 28_401,
        "dual": 25_145,
        "item": 14_009,
        "item_pidgeot": 11_979,
        "item_stoutland": 10_015,
    }
    assert sum(result.added_without_displaced_active.values()) == 0
    assert sum(result.removed_without_bunnelby.values()) == 0
    assert sum(result.violating_states.values()) == 0

    print("Aichi Active-swap locality regression passed.")


if __name__ == "__main__":
    main()
