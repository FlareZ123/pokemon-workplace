"""Reproduce observer-indexed Prize belief updates."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from observer_prize_beliefs import ObserverPrizeBeliefs, update_for_prize_removal
from prize_belief_kernel import PrizeBelief
from prize_take_information_asymmetry import group_probability


def assert_close(actual: float, expected: float) -> None:
    assert abs(actual - expected) <= 1e-12, (actual, expected)


def main() -> None:
    prior = PrizeBelief.from_hypergeometric(
        {"A": 1, "B": 1},
        pool_size=5,
        prize_count=2,
    )
    state = ObserverPrizeBeliefs(
        "Alice",
        (
            ("Alice", prior),
            ("Bob", prior),
        ),
    )

    private_take = update_for_prize_removal(
        state,
        visible_groups={"Alice": "A"},
    )
    alice = private_take.belief_for("Alice")
    bob = private_take.belief_for("Bob")
    assert private_take.prize_count == 1
    assert_close(group_probability(alice, "A"), 0.0)
    assert_close(group_probability(alice, "B"), 1.0 / 4.0)
    assert_close(group_probability(bob, "A"), 1.0 / 5.0)
    assert_close(group_probability(bob, "B"), 1.0 / 5.0)
    assert bob.entropy_bits() > alice.entropy_bits()

    public_take = update_for_prize_removal(
        state,
        visible_groups={
            "Alice": "A",
            "Bob": "A",
        },
    )
    public_alice = public_take.belief_for("Alice")
    public_bob = public_take.belief_for("Bob")
    assert public_alice == public_bob
    assert_close(group_probability(public_bob, "A"), 0.0)
    assert_close(group_probability(public_bob, "B"), 1.0 / 4.0)

    filler_take = update_for_prize_removal(
        state,
        visible_groups={"Alice": None},
    )
    alice_filler = filler_take.belief_for("Alice")
    bob_filler = filler_take.belief_for("Bob")
    assert_close(group_probability(alice_filler, "A"), 1.0 / 3.0)
    assert_close(group_probability(alice_filler, "B"), 1.0 / 3.0)
    assert_close(group_probability(bob_filler, "A"), 1.0 / 5.0)
    assert_close(group_probability(bob_filler, "B"), 1.0 / 5.0)

    try:
        update_for_prize_removal(
            state,
            visible_groups={"Charlie": "A"},
        )
    except ValueError:
        pass
    else:
        raise AssertionError("unknown observer visibility was accepted")

    try:
        ObserverPrizeBeliefs(
            "Alice",
            (
                ("Alice", prior),
                (
                    "Bob",
                    PrizeBelief.from_hypergeometric(
                        {"A": 1, "B": 1},
                        pool_size=5,
                        prize_count=1,
                    ),
                ),
            ),
        )
    except ValueError:
        pass
    else:
        raise AssertionError("observer Prize counts were allowed to diverge")

    print("observer-indexed Prize belief regressions passed")


if __name__ == "__main__":
    main()
