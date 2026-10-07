"""Reproduce conserved hidden Prize-taking belief transitions."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from identity_materialization import IdentityLedger
from multicopy_zone_state import ZoneCountState
from prize_belief_kernel import PrizeBelief
from prize_take_transition import (
    PrizeTruthBeliefState,
    begin_face_down_prize_take,
    complete_prize_take_to_hand,
    take_face_down_prize_branches,
    take_face_down_prize_observation,
)


def probability_of_state(belief: PrizeBelief, counts: tuple[int, ...]) -> float:
    return dict(belief.masses).get(counts, 0.0)


def check_one_take_prior_and_truth() -> None:
    belief = PrizeBelief.from_hypergeometric(
        {"A": 1, "B": 1},
        pool_size=4,
        prize_count=2,
    )
    branches = take_face_down_prize_branches(belief)
    by_group = {branch.observed_group: branch for branch in branches}
    assert abs(by_group["A"].probability - 0.25) < 1e-12
    assert abs(by_group["B"].probability - 0.25) < 1e-12
    assert abs(by_group[None].probability - 0.50) < 1e-12
    assert abs(sum(branch.probability for branch in branches) - 1.0) < 1e-12

    p_a, after_a = take_face_down_prize_observation(belief, "A")
    assert abs(p_a - 0.25) < 1e-12
    assert after_a.prize_count == 1
    assert abs(probability_of_state(after_a, (0, 0)) - 2 / 3) < 1e-12
    assert abs(probability_of_state(after_a, (0, 1)) - 1 / 3) < 1e-12

    ledger = IdentityLedger(
        ZoneCountState.from_mapping(
            {
                ("a-class", "prize"): 1,
                ("filler-1", "prize"): 1,
                ("b-class", "deck"): 1,
                ("filler-2", "deck"): 1,
            }
        )
    )
    state = PrizeTruthBeliefState(
        ledger,
        belief,
        (
            ("a-class", "A"),
            ("b-class", "B"),
            ("filler-1", None),
            ("filler-2", None),
        ),
    )
    started = begin_face_down_prize_take(
        state,
        card_class="a-class",
        card_name="A card",
        observed_group="A",
        instance_id="a-prize-instance",
    )
    assert abs(started.event.observation_probability - 0.25) < 1e-12
    assert started.state.belief == after_a
    assert started.state.ledger.exchangeable.count("a-class", "prize") == 0
    assert started.state.ledger.instance("a-prize-instance").zone == "prize_pending"

    finished = complete_prize_take_to_hand(
        started.state,
        "a-prize-instance",
    )
    assert finished.ledger.exchangeable.count("a-class", "hand") == 1
    assert all(
        row.instance_id != "a-prize-instance"
        for row in finished.ledger.instances
    )
    assert finished.belief == after_a


def check_truth_belief_consistency_guards() -> None:
    belief = PrizeBelief.from_exact({"A": 1}, prize_count=1)
    ledger = IdentityLedger(
        ZoneCountState.from_mapping({("a-class", "prize"): 1})
    )
    state = PrizeTruthBeliefState(
        ledger,
        belief,
        (("a-class", "A"),),
    )
    try:
        begin_face_down_prize_take(
            state,
            card_class="a-class",
            card_name="A card",
            observed_group=None,
            instance_id="wrong-group",
        )
    except ValueError as error:
        assert "does not match" in str(error)
    else:
        raise AssertionError("physical Prize class accepted the wrong belief group")

    impossible_belief = PrizeBelief.from_exact({"A": 0}, prize_count=1)
    try:
        PrizeTruthBeliefState(
            ledger,
            impossible_belief,
            (("a-class", "A"),),
        )
    except ValueError as error:
        assert "zero probability" in str(error)
    else:
        raise AssertionError("Prize composition outside belief support was accepted")


def check_nested_before_hand_prize_take() -> None:
    belief = PrizeBelief.from_exact(
        {"Lucky": 1, "Payload": 1},
        prize_count=2,
    )
    ledger = IdentityLedger(
        ZoneCountState.from_mapping(
            {
                ("lucky-class", "prize"): 1,
                ("payload-class", "prize"): 1,
            }
        )
    )
    state = PrizeTruthBeliefState(
        ledger,
        belief,
        (
            ("lucky-class", "Lucky"),
            ("payload-class", "Payload"),
        ),
    )

    first = begin_face_down_prize_take(
        state,
        card_class="lucky-class",
        card_name="Lucky Bonus card",
        observed_group="Lucky",
        instance_id="lucky-instance",
    )
    assert first.state.belief.prize_count == 1
    assert first.state.ledger.instance("lucky-instance").zone == "prize_pending"
    assert probability_of_state(first.state.belief, (0, 1)) == 1.0

    second = begin_face_down_prize_take(
        first.state,
        card_class="payload-class",
        card_name="Payload card",
        observed_group="Payload",
        instance_id="payload-instance",
    )
    assert second.state.belief.prize_count == 0
    assert second.state.ledger.instance("lucky-instance").zone == "prize_pending"
    assert second.state.ledger.instance("payload-instance").zone == "prize_pending"

    after_payload = complete_prize_take_to_hand(
        second.state,
        "payload-instance",
    )
    assert after_payload.ledger.instance("lucky-instance").zone == "prize_pending"
    finished = complete_prize_take_to_hand(
        after_payload,
        "lucky-instance",
    )
    assert finished.belief.prize_count == 0
    assert finished.ledger.instances == ()
    assert finished.ledger.exchangeable.count("lucky-class", "hand") == 1
    assert finished.ledger.exchangeable.count("payload-class", "hand") == 1


def main() -> None:
    check_one_take_prior_and_truth()
    check_truth_belief_consistency_guards()
    check_nested_before_hand_prize_take()
    print("Prize-take truth/belief regressions passed")


if __name__ == "__main__":
    main()
