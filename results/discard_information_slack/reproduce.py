"""Reproduce discard-information slack boundary checks."""

from discard_information_slack import (
    DiscardInformationBoundary,
    aichi_direct_gnh_rich_endpoint,
    secret_box_local_counterexample,
)


def main() -> None:
    gnh = aichi_direct_gnh_rich_endpoint()
    assert gnh.forced_critical_discards == 0
    assert not gnh.information_can_change_choice
    assert gnh.blind_success == 1.0
    assert gnh.informed_success == 1.0
    assert gnh.information_gap == 0.0

    box = secret_box_local_counterexample()
    assert box.forced_critical_discards == 1
    assert box.information_can_change_choice
    assert abs(box.blind_success - 0.8846153846153846) < 1e-15
    assert abs(box.informed_success - 0.9886877828054299) < 1e-15
    assert abs(box.information_gap - 0.10407239819004525) < 1e-15

    forced_all = DiscardInformationBoundary(
        unknown_pool=52,
        prize_count=6,
        discard_cost=4,
        always_safe_cards=2,
        critical_candidates=2,
    )
    assert forced_all.forced_critical_discards == 2
    assert not forced_all.information_can_change_choice
    assert abs(forced_all.information_gap) < 1e-15

    print(f"gnh_forced_critical={gnh.forced_critical_discards}")
    print(f"gnh_gap_pp={gnh.information_gap * 100:.9f}")
    print(f"box_forced_critical={box.forced_critical_discards}")
    print(f"box_gap_pp={box.information_gap * 100:.9f}")
    print(f"forced_all_gap_pp={forced_all.information_gap * 100:.9f}")


if __name__ == "__main__":
    main()
