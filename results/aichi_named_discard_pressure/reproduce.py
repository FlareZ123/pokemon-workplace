"""Regression for Aichi starting-Active named discard pressure."""

from aichi_named_discard_pressure import simulate_named_pressure


def main() -> None:
    result = simulate_named_pressure(100_000, seed=20261007)

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

    assert result.any_forced_singleton_default.get("item_pidgeot", 0) == 1
    assert sum(result.any_forced_singleton_default.values()) == 1
    assert sum(result.any_forced_singleton_bunnelby.values()) == 0

    assert result.forced_default_by_name["item_pidgeot"] == {
        "Budew": 1,
        "Mr. Mime": 1,
    }
    assert result.newly_avoidable_bunnelby_by_name["item_pidgeot"] == {
        "Budew": 1,
        "Mr. Mime": 1,
    }

    expected_bunnelby_protected = {
        "core": 8_500,
        "pidgeot": 7_301,
        "stoutland": 6_034,
        "dual": 5_353,
        "item": 3_136,
        "item_pidgeot": 2_705,
        "item_stoutland": 2_280,
    }
    for endpoint, expected in expected_bunnelby_protected.items():
        actual = result.newly_protected_bunnelby_by_name[endpoint].get(
            "Bunnelby", 0
        )
        assert actual == expected, (endpoint, actual, expected)

    print("Aichi named discard pressure regression passed.")


if __name__ == "__main__":
    main()
