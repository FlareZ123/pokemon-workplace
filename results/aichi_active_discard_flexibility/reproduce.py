"""Reproduce key Aichi Active discard-flexibility findings."""

from aichi_active_discard_flexibility import simulate_flex


def main() -> None:
    result = simulate_flex(100_000, seed=20261007)
    assert result.policy_difference_states == 16_905

    for endpoint in result.both_gnh:
        assert result.default_natural_only.get(endpoint, 0) == 0
        assert result.bunnelby_natural_only.get(endpoint, 0) == 0

    item = "item"
    item_pidgeot = "item_pidgeot"
    item_stoutland = "item_stoutland"

    assert (
        result.pair_totals_bunnelby[item]
        > result.pair_totals_default[item]
    )
    assert (
        result.pair_totals_bunnelby[item_pidgeot]
        < result.pair_totals_default[item_pidgeot]
    )
    assert (
        result.pair_totals_bunnelby[item_stoutland]
        < result.pair_totals_default[item_stoutland]
    )

    print("policy_difference_states", result.policy_difference_states)
    for endpoint in (item, item_pidgeot, item_stoutland):
        both = result.both_gnh[endpoint]
        print(
            endpoint,
            result.pair_totals_default[endpoint] / both,
            result.pair_totals_bunnelby[endpoint] / both,
        )


if __name__ == "__main__":
    main()
