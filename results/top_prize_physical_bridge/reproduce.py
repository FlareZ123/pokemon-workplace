"""Reproduce the physical/observer Prize-top swap bridge."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from identity_materialization import CardInstance, IdentityLedger, assert_conserved
from multicopy_zone_state import ZoneCountState
from observer_top_prize_beliefs import (
    ObserverTopPrizeBeliefs,
    independent_top_prize_belief,
)
from prize_position_belief import PrizePositionBelief
from prize_slot_visibility import PrizeSlotVisibilityBelief
from top_prize_physical_bridge import (
    TopPrizePhysicalState,
    actual_joint_groups,
    belief_truth_probability,
    resolve_observer_physical_optional_swap,
)


def assert_close(actual: float, expected: float) -> None:
    assert abs(actual - expected) <= 1e-12, (actual, expected)


def make_beliefs() -> ObserverTopPrizeBeliefs:
    positions = PrizePositionBelief.from_exact_composition(
        {"A": 1, "B": 1, "X": 0, "Y": 0},
        prize_count=2,
    )
    prizes = PrizeSlotVisibilityBelief.all_face_down(positions)
    prior = independent_top_prize_belief(
        prizes,
        {"X": 1.0 / 2.0, "Y": 1.0 / 2.0},
    )
    return ObserverTopPrizeBeliefs(
        (("actor", prior), ("opponent", prior))
    )


def make_physical() -> TopPrizePhysicalState:
    ledger = IdentityLedger(
        ZoneCountState.from_mapping({("Y", "deck"): 1}),
        (
            CardInstance("a", "A", "A", "prize"),
            CardInstance("b", "B", "B", "prize"),
            CardInstance("x", "X", "X", "deck_top"),
        ),
    )
    return TopPrizePhysicalState(
        ledger,
        "x",
        ("a", "b"),
        (False, False),
    )


def main() -> None:
    groups = {"A": "A", "B": "B", "X": "X", "Y": "Y"}
    physical = make_physical()
    beliefs = make_beliefs()

    transition = resolve_observer_physical_optional_swap(
        physical,
        beliefs,
        actor_id="actor",
        swap_probability_by_top={"X": 1.0, "Y": 1.0 / 4.0},
        observed_swap=True,
        position=0,
        group_by_card_class=groups,
    )

    after = transition.physical_after
    assert after.top_instance_id == "a"
    assert after.prize_instance_ids == ("x", "b")
    assert after.ledger.instance("a").zone == "deck_top"
    assert after.ledger.instance("x").zone == "prize"
    assert_conserved(physical.ledger, after.ledger)

    top_group, prize_groups = actual_joint_groups(after, groups)
    assert top_group == "A"
    assert prize_groups == ("X", "B")

    actor = transition.beliefs_after.belief_for("actor")
    opponent = transition.beliefs_after.belief_for("opponent")

    assert_close(
        belief_truth_probability(
            actor,
            top_group=top_group,
            prize_groups=prize_groups,
        ),
        1.0 / 2.0,
    )
    assert_close(
        belief_truth_probability(
            opponent,
            top_group=top_group,
            prize_groups=prize_groups,
        ),
        2.0 / 5.0,
    )

    # The exact physical truth is unique even though observers retain different
    # uncertainty over that same hidden topology.
    assert_close(actor.prize_probability_at(0, "X"), 1.0)
    assert_close(opponent.prize_probability_at(0, "X"), 4.0 / 5.0)

    # A combined state with a posterior that excludes the real top card is
    # rejected before mutation.
    impossible_positions = PrizePositionBelief.from_exact_composition(
        {"A": 1, "B": 1, "X": 0, "Y": 0},
        prize_count=2,
    )
    impossible_prizes = PrizeSlotVisibilityBelief.all_face_down(
        impossible_positions
    )
    impossible_prior = independent_top_prize_belief(
        impossible_prizes,
        {"Y": 1.0},
    )
    impossible = ObserverTopPrizeBeliefs(
        (("actor", impossible_prior), ("opponent", impossible_prior))
    )
    try:
        resolve_observer_physical_optional_swap(
            physical,
            impossible,
            actor_id="actor",
            swap_probability_by_top={"Y": 1.0},
            observed_swap=True,
            position=0,
            group_by_card_class=groups,
        )
    except ValueError:
        pass
    else:
        raise AssertionError("accepted observer beliefs excluding physical truth")

    print("Physical/observer top-Prize bridge regressions passed")


if __name__ == "__main__":
    main()
