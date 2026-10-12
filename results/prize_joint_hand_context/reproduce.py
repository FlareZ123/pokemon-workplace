"""Exact physical and rational counterexample to tag-only hand composition."""

from collections import Counter
from fractions import Fraction as F
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from before_hand_prize_profiles import BeforeHandPrizeProfile
from identity_materialization import CardInstance, IdentityLedger, assert_conserved
from multicopy_zone_state import ZoneCountState
from observer_top_prize_beliefs import ObserverTopPrizeBeliefs
from pending_prize_identity_belief import stage_one_pending_prize_for_observers
from prize_acquired_hand_reveal import decline_prize_into_latent_hand
from prize_joint_hand_context import expand_joint_private_prize_hand_composition
from prize_pending_take import stage_prize_takes
from prize_top_swap_belief import TopPrizeJointBelief
from prize_unknown_hand_composition import (
    expand_private_prize_hand_composition,
    publicly_discard_unknown_other_hand,
)
from top_prize_physical_bridge import TopPrizePhysicalState

PRIOR = (
    ("S", "C", F(2, 5)),
    ("F", "C", F(1, 10)),
    ("S", "O", F(1, 10)),
    ("F", "O", F(2, 5)),
)
GROUPS = ("S", "F", "C", "O")
OTHER_C = (0, 0, 1, 0)
OTHER_O = (0, 0, 0, 1)
CLASS_GROUPS = {"S-class": "S", "sv3pt5-113": "C"}
PROFILE = BeforeHandPrizeProfile(
    "sv3pt5-113", "Chansey", "ability:Lucky Bonus",
    "self_to_bench", "in_play", True, True, "coin_heads", False,
)
# Opponent's hypotheses P(other C | top, tagged Prize). No hidden world is
# eliminated; the actual material world is (S, C, other C).
P_OTHER_C = {
    ("S", "C"): F(1),
    ("F", "C"): F(0),
    ("S", "O"): F(1, 2),
    ("F", "O"): F(1, 4),
}


def setup():
    prior = TopPrizeJointBelief(
        GROUPS, (False,),
        tuple(((top, (tag,)), float(p)) for top, tag, p in PRIOR),
    )
    pending = stage_one_pending_prize_for_observers(
        ObserverTopPrizeBeliefs((("actor", prior), ("opponent", prior))),
        position=0, visible_groups={"actor": "C"},
    )
    ledger = IdentityLedger(
        ZoneCountState(),
        (
            CardInstance("other-c", "sv3pt5-113", "Chansey", "hand"),
            CardInstance("prize-c", "sv3pt5-113", "Chansey", "prize"),
            CardInstance("top-s", "S-class", "S", "deck_top"),
        ),
    )
    physical = TopPrizePhysicalState(ledger, "top-s", ("prize-c",), (False,))
    acquired = decline_prize_into_latent_hand(
        stage_prize_takes(physical, positions=(0,)),
        pending, PROFILE, actor_id="actor",
        group_by_card_class=CLASS_GROUPS,
        use_probability_by_group={"C": 0.6, "O": 0.0},
        during_own_turn=True,
    )
    return ledger, acquired


def joint_hypotheses(acquired):
    models = {}
    for observer, belief in acquired.beliefs.beliefs:
        by_world = {}
        for (top, prizes, tag), mass in belief.masses:
            if mass <= 0:
                continue
            if observer == "actor":
                by_world[(top, prizes, tag)] = {OTHER_C: 1.0}
            else:
                q = P_OTHER_C[(top, tag)]
                by_world[(top, prizes, tag)] = {
                    counts: float(p)
                    for counts, p in ((OTHER_C, q), (OTHER_O, 1 - q))
                    if p
                }
        models[observer] = by_world
    return models


def exact_oracle(prob_other_c):
    """Independently enumerate all labeled tag, other and discard-origin events."""
    accepted = []
    for top, tag, initial in PRIOR:
        decline = F(2, 5) if tag == "C" else F(1)
        q = prob_other_c[(top, tag)]
        for other, probability in (("C", q), ("O", 1 - q)):
            for tag_discarded in (True, False):
                observed = tag if tag_discarded else other
                if observed == "C":
                    accepted.append((
                        top, tag, not tag_discarded,
                        initial * decline * probability * F(1, 2),
                    ))
    evidence = sum(mass for *_rest, mass in accepted)
    return (
        evidence,
        sum(mass for _top, tag, _survives, mass in accepted if tag == "C") / evidence,
        sum(mass for top, _tag, _survives, mass in accepted if top == "S") / evidence,
        sum(mass for _top, _tag, survives, mass in accepted if survives) / evidence,
    )


def check(actual, expected):
    assert abs(actual - float(expected)) < 1e-12, (actual, expected)


def main():
    expected = exact_oracle(P_OTHER_C)
    assert expected == (F(51, 200), F(12, 17), F(37, 51), F(31, 51))

    marginal_other_c = {"C": F(4, 5), "O": F(3, 10)}
    collapsed = {
        (top, tag): marginal_other_c[tag]
        for top, tag, _mass in PRIOR
    }
    collapsed_oracle = exact_oracle(collapsed)
    assert collapsed_oracle == (F(51, 200), F(12, 17), F(53, 85), F(31, 51))
    assert expected[2] - collapsed_oracle[2] == F(26, 255)

    for chosen, tag_survives in (("other-c", True), ("prize-c", False)):
        original, acquired = setup()
        models = joint_hypotheses(acquired)
        expanded = expand_joint_private_prize_hand_composition(
            acquired, conditional_other_counts_by_world=models,
        )
        observed = publicly_discard_unknown_other_hand(
            acquired, expanded, actor_id="actor",
            discarded_instance_id=chosen, group_by_card_class=CLASS_GROUPS,
        )
        opponent = observed.beliefs.belief_for("opponent")
        check(opponent.tagged_probability("C"), expected[1])
        check(opponent.top_probability("S"), expected[2])
        check(opponent.tagged_survival_probability(), expected[3])
        actor = observed.beliefs.belief_for("actor")
        check(actor.tagged_probability("C"), 1)
        check(actor.top_probability("S"), F(4, 5))
        check(actor.tagged_survival_probability(), int(tag_survives))
        assert observed.physical.ledger.instance(chosen).zone == "discard"
        assert_conserved(original, observed.physical.ledger)

        # An old tag-conditioned model reproduces all tag-only marginals
        # yet loses a full 26/255 of top-S probability.
        tag_only = expand_private_prize_hand_composition(
            acquired, conditional_other_counts={
                "actor": {"C": {OTHER_C: 1.0}},
                "opponent": {
                    tag: {OTHER_C: float(q), OTHER_O: float(1 - q)}
                    for tag, q in marginal_other_c.items()
                },
            },
        )
        simpler = publicly_discard_unknown_other_hand(
            acquired, tag_only, actor_id="actor",
            discarded_instance_id=chosen, group_by_card_class=CLASS_GROUPS,
        )
        check(simpler.beliefs.belief_for("opponent").top_probability("S"),
              collapsed_oracle[2])

        for bad_worlds in (
            {**models["opponent"], ("INVALID", (), "C"): {OTHER_C: 1.0}},
            {**models["opponent"], ("S", ("C",), "C"): {OTHER_C: 0.5}},
        ):
            # The second malformed fixture may overlap a supported key.
            try:
                expand_joint_private_prize_hand_composition(
                    acquired,
                    conditional_other_counts_by_world={
                        **models, "opponent": bad_worlds
                    },
                )
            except ValueError:
                pass
            else:
                raise AssertionError("invalid joint hand hypothesis accepted")

    print("Joint Prize/top/tag hand-context regression passed")
    print("P(top S | public discard C): full = 37/51; tag-only = 53/85")
    print("Difference: 26/255 (10.196 percentage points)")


if __name__ == "__main__":
    main()
