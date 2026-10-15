"""K0-observable Fog first source with two different K1 target choices."""
from results.tests.shadow_rider_k0_first_source.reproduce import first_success
from results.tests.shadow_rider_paid_search_allocation.reproduce import feasible

op = (0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1, 1, 2)
hand = (0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 1, 1, 2)
marshadow_prized = (1, 2, 4, 0, 1, 0, 1, 8, 0, 1, 10, 3, 0, 15)
shadow_v_prized = (1, 2, 4, 0, 1, 0, 0, 8, 1, 1, 10, 3, 0, 15)


def after_fog(target: int, deck: tuple[int, ...]) -> bool:
    if not deck[target]:
        return False
    h, d = list(hand), list(deck)
    h[11] -= 1
    h[target] += 1
    d[target] -= 1
    return feasible(op, tuple(h), tuple(d))


def main() -> None:
    assert first_success(op, hand, marshadow_prized, "fog")
    assert first_success(op, hand, shadow_v_prized, "fog")
    assert after_fog(6, marshadow_prized)
    assert not after_fog(8, marshadow_prized)
    assert after_fog(8, shadow_v_prized)
    assert not after_fog(6, shadow_v_prized)
    print("PASS: fixed Fog first source; K1 deck inspection changes its target")


if __name__ == "__main__":
    main()
