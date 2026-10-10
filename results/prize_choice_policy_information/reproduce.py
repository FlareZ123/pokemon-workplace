"""Exhaustive toy proof that hidden-position policies require private knowledge."""

from fractions import Fraction
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from prize_position_top_swap import PrizePositionTopBelief
from prize_choice_policy_information import (
    condition_on_admissible_position_choice,
    is_world_likelihood_admissible,
)


def close(actual, expected):
    assert abs(actual - float(expected)) <= 1e-12, (actual, expected)


def must_reject(thunk):
    try:
        thunk()
    except (ValueError, IndexError):
        return
    raise AssertionError("accepted invalid policy")


def main():
    world_a = (("A", "B"), "X")
    world_b = (("B", "A"), "X")
    observer = PrizePositionTopBelief(
        ("A", "B", "X"), (False, False),
        ((world_a, 1 / 2), (world_b, 1 / 2)),
    )

    world_policy = {world_a: 4 / 5, world_b: 1 / 5}
    uninformed = {world_a: "not-seen", world_b: "not-seen"}
    informed = {world_a: "A-at-0", world_b: "B-at-0"}

    # No private knowledge: these world-conditioned choice rates are illegal.
    assert not is_world_likelihood_admissible(
        observer, uninformed, world_policy
    )

    # Prior deliberate placements/inspections can distinguish the two worlds.
    assert is_world_likelihood_admissible(
        observer, informed, world_policy
    )
    informed_strategy = {
        "A-at-0": {0: 4 / 5, 1: 1 / 5},
        "B-at-0": {0: 1 / 5, 1: 4 / 5},
    }
    condition = condition_on_admissible_position_choice(
        observer,
        actor_information_by_world=informed,
        policy_by_information=informed_strategy,
        chosen_position=0,
    )
    swapped = condition.swap_face_down_with_top(0)
    close(swapped.probability_top("A"), Fraction(4, 5))

    # The independent exact-rational conditional outcome.
    numerator = Fraction(1, 2) * Fraction(4, 5)
    denominator = numerator + Fraction(1, 2) * Fraction(1, 5)
    assert numerator / denominator == Fraction(4, 5)

    # Unknown mapping => actor must play the same mixed strategy in both worlds.
    unknown_strategy = {"not-seen": {0: 3 / 4, 1: 1 / 4}}
    uninformative_posterior = condition_on_admissible_position_choice(
        observer,
        actor_information_by_world=uninformed,
        policy_by_information=unknown_strategy,
        chosen_position=0,
    ).swap_face_down_with_top(0)
    close(uninformative_posterior.probability_top("A"), Fraction(1, 2))

    # Perfectly targeting A signals its hidden location, if known to the actor.
    target_a_strategy = {
        "A-at-0": {0: 1, 1: 0},
        "B-at-0": {0: 0, 1: 1},
    }
    perfectly_revealed = condition_on_admissible_position_choice(
        observer,
        actor_information_by_world=informed,
        policy_by_information=target_a_strategy,
        chosen_position=0,
    )
    close(perfectly_revealed.swap_face_down_with_top(0).probability_top("A"), 1)

    must_reject(lambda: is_world_likelihood_admissible(
        observer, {world_a: "only"}, world_policy
    ))
    must_reject(lambda: condition_on_admissible_position_choice(
        observer,
        actor_information_by_world=informed,
        policy_by_information={"A-at-0": {0: 0.5, 1: 0.5}},
        chosen_position=0,
    ))
    must_reject(lambda: condition_on_admissible_position_choice(
        observer,
        actor_information_by_world=informed,
        policy_by_information={
            "A-at-0": {0: 0.5, 1: 0.4},
            "B-at-0": {0: 0.5, 1: 0.5},
        },
        chosen_position=0,
    ))
    must_reject(lambda: condition_on_admissible_position_choice(
        observer,
        actor_information_by_world=informed,
        policy_by_information=informed_strategy,
        chosen_position=2,
    ))
    must_reject(lambda: condition_on_admissible_position_choice(
        observer,
        actor_information_by_world=informed,
        policy_by_information={
            "A-at-0": {0: 0, 1: 1},
            "B-at-0": {0: 0, 1: 1},
        },
        chosen_position=0,
    ))

    print("Prize-choice information admissibility passed; impossible oracle strategy rejected")
    print("Informed choice posterior 4/5; uninformed choice posterior 1/2")


if __name__ == "__main__":
    main()
