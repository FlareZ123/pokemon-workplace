"""Reproduce action signaling from observation-generated information partitions."""

from fractions import Fraction
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from prize_position_top_swap import PrizePositionTopBelief
from prize_epistemic_trace import PrizeEpistemicTrace


def close(actual, expected):
    assert abs(actual - float(expected)) <= 1e-12, (actual, expected)


def must_reject(thunk):
    try:
        thunk()
    except (ValueError, IndexError):
        return
    raise AssertionError("invalid epistemic trace action was allowed")


def main():
    a_first = (("A", "B"), "X")
    b_first = (("B", "A"), "X")
    prior = PrizePositionTopBelief(
        ("A", "B", "X"),
        (False, False),
        ((a_first, 1 / 2), (b_first, 1 / 2)),
    )
    start = PrizeEpistemicTrace.from_joint_prior(prior, ("actor", "opponent"))

    assert start.histories_for("actor") == {()}
    assert start.histories_for("opponent") == {()}

    # In a world where a previous source-authorized inspection has revealed
    # Prize0, the actor's histories distinguish the two physical assignments.
    peeked = start.private_peek("actor", zone="prize", position=0)
    private_a = ("private:prize:0:'A'",)
    private_b = ("private:prize:0:'B'",)
    public_peek = ("public:peek:prize:0",)
    assert peeked.histories_for("actor") == {private_a, private_b}
    assert peeked.histories_for("opponent") == {public_peek}
    close(
        peeked.conditional_probability(
            "actor", private_a, lambda w: w[0][0] == "A"
        ),
        1,
    )

    choice_policy = {
        private_a: {0: 4 / 5, 1: 1 / 5},
        private_b: {0: 1 / 5, 1: 4 / 5},
    }
    chosen = peeked.select_and_swap(
        actor_id="actor",
        selected_position=0,
        policy_by_actor_history=choice_policy,
    )
    public_after = ("public:peek:prize:0", "public:swap:0")
    actor_a_after = private_a + ("public:swap:0",)
    actor_b_after = private_b + ("public:swap:0",)
    assert chosen.histories_for("opponent") == {public_after}
    close(chosen.conditional_probability(
        "opponent", public_after, lambda w: w[1] == "A"
    ), Fraction(4, 5))
    close(chosen.conditional_probability(
        "actor", actor_a_after, lambda w: w[1] == "A"
    ), 1)
    close(chosen.conditional_probability(
        "actor", actor_b_after, lambda w: w[1] == "B"
    ), 1)

    # Independent two-world Bayes rational oracle.
    event_a = Fraction(1, 2) * Fraction(4, 5)
    event_b = Fraction(1, 2) * Fraction(1, 5)
    assert event_a / (event_a + event_b) == Fraction(4, 5)

    # Without a prior private inspection, no source-derived information set
    # distinguishes the physical mappings; a legal mixed choice is neutral.
    neutral = start.select_and_swap(
        actor_id="actor",
        selected_position=0,
        policy_by_actor_history={(): {0: 3 / 4, 1: 1 / 4}},
    )
    close(
        neutral.conditional_probability(
            "opponent", ("public:swap:0",), lambda w: w[1] == "A"
        ),
        Fraction(1, 2),
    )
    must_reject(lambda: start.select_and_swap(
        actor_id="actor", selected_position=0,
        policy_by_actor_history=choice_policy,
    ))

    # The hidden uniform shuffle changes material positions but remembers
    # prior private observations. It destroys slot precision after the swap.
    shuffled = chosen.hidden_shuffle()
    shuffled_actor_a = actor_a_after + ("public:shuffle-face-down",)
    close(shuffled.conditional_probability(
        "actor", shuffled_actor_a, lambda w: w[0][0] == "X"
    ), Fraction(1, 2))
    close(shuffled.conditional_probability(
        "actor", shuffled_actor_a, lambda w: w[1] == "A"
    ), 1)

    # Public revelation updates each observer using a single actual result.
    revealed = shuffled.public_reveal(1, "X")
    public_revealed_history = public_after + (
        "public:shuffle-face-down", "public:reveal:1:'X'"
    )
    close(revealed.conditional_probability(
        "opponent", public_revealed_history, lambda w: w[0][1] == "X"
    ), 1)
    assert revealed.face_up == (False, True)
    must_reject(lambda: revealed.select_and_swap(
        actor_id="actor", selected_position=1,
        policy_by_actor_history={(): {0: 1}},
    ))
    must_reject(lambda: shuffled.public_reveal(1, "impossible"))
    must_reject(lambda: peeked.select_and_swap(
        actor_id="actor", selected_position=0,
        policy_by_actor_history={
            private_a: {0: 0.7, 1: 0.4},
            private_b: {0: 0.5, 1: 0.5},
        },
    ))

    print("Observation-derived actor partitions and opponent Bayes passed")
    print("Hidden-position private peek: posterior 4/5 vs neutral 1/2")
    print("Shuffle and public reveal update both observers without inventing observations")


if __name__ == "__main__":
    main()
