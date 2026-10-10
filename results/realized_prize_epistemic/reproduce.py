"""Reproduce realized physical-instance and epistemic-trace synchronization."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from observer_positioned_prize_truth import PhysicalPrizeTop
from prize_position_top_swap import PrizePositionTopBelief
from realized_prize_epistemic import RealizedPrizeEpistemic


def close(actual, expected):
    assert abs(actual - expected) <= 1e-12, (actual, expected)


def reject(thunk):
    try:
        thunk()
    except (ValueError, IndexError):
        return
    raise AssertionError("accepted impossible physical/epistemic state")


def main():
    a_first = (("A", "B"), "X")
    b_first = (("B", "A"), "X")
    prior = PrizePositionTopBelief(
        ("A", "B", "X"),
        (False, False),
        ((a_first, 1 / 2), (b_first, 1 / 2)),
    )
    physical = PhysicalPrizeTop(
        ("physical-A", "physical-B"),
        "physical-X",
        (False, False),
        (
            ("physical-A", "A"),
            ("physical-B", "B"),
            ("physical-X", "X"),
        ),
    )
    realized = RealizedPrizeEpistemic.from_prior(
        physical, prior, ("actor", "opponent")
    )
    close(realized.posterior_for("opponent").probability_at(0, "A"), 1 / 2)

    # The exact physical world has A in Prize0. The actor, and not the opponent,
    # learns that fact by observing the card under a stipulated legal prior effect.
    realized = realized.private_peek("actor", zone="prize", position=0)
    assert realized.actual_histories[0] == ("private:prize:0:'A'",)
    assert realized.actual_histories[1] == ("public:peek:prize:0",)
    close(realized.posterior_for("actor").probability_at(0, "A"), 1)
    close(realized.posterior_for("opponent").probability_at(0, "A"), 1 / 2)

    # Arc Phone's top card inspection must be recorded before its optional swap.
    realized = realized.private_peek("actor", zone="top")
    assert realized.actual_histories[0][-1] == "private:top:'X'"
    actor_a = ("private:prize:0:'A'", "private:top:'X'")
    actor_b = ("private:prize:0:'B'", "private:top:'X'")
    choice = {
        actor_a: {0: 4 / 5, 1: 1 / 5},
        actor_b: {0: 1 / 5, 1: 4 / 5},
    }
    realized = realized.selected_swap(
        actor_id="actor",
        selected_position=0,
        policy_by_actor_history=choice,
    )
    assert realized.truth.prizes == ("physical-X", "physical-B")
    assert realized.truth.deck_top == "physical-A"
    close(realized.posterior_for("actor").probability_top("A"), 1)
    close(realized.posterior_for("opponent").probability_top("A"), 4 / 5)
    realized.as_observer_positioned_prizes()

    # A hidden uniform shuffle is realized physically as one sampled
    # permutation but marginalized by the epistemic model.
    realized = realized.hidden_shuffle((1, 0))
    assert realized.truth.prizes == ("physical-B", "physical-X")
    close(realized.posterior_for("actor").probability_at(1, "X"), 1 / 2)
    close(realized.posterior_for("opponent").probability_at(1, "X"), 1 / 2)
    realized.as_observer_positioned_prizes()

    # The physical result of revealing slot1 is X, so all observers condition
    # on that public fact and the exposed position becomes ineligible.
    realized = realized.public_reveal(1)
    assert realized.truth.face_up == (False, True)
    close(realized.posterior_for("actor").probability_at(1, "X"), 1)
    close(realized.posterior_for("opponent").probability_at(1, "X"), 1)
    realized.as_observer_positioned_prizes()
    reject(lambda: realized.selected_swap(
        actor_id="actor", selected_position=1,
        policy_by_actor_history={},
    ))
    reject(lambda: realized.hidden_shuffle((1, 0)))

    # The realized physical configuration must already have positive support.
    incompatible = PhysicalPrizeTop(
        ("physical-X", "physical-B"),
        "physical-A",
        (False, False),
        physical.groups_by_instance,
    )
    reject(lambda: RealizedPrizeEpistemic.from_prior(
        incompatible, prior, ("actor", "opponent")
    ))

    print("Physical-instance Prize truth and event-derived observer posteriors agree")
    print("Private peek + selected swap gives actor P(top=A)=1; opponent P=4/5")
    print("Uniform hidden shuffle and public reveal preserve one physical world")


if __name__ == "__main__":
    main()
