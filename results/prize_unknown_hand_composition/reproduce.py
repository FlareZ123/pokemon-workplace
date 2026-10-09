"""Exact mixture oracle for random hand discard with unknown other-hand card."""

from fractions import Fraction
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
from prize_acquired_random_discard_chain import continue_random_hand_discard
from prize_pending_take import stage_prize_takes
from prize_top_swap_belief import TopPrizeJointBelief
from prize_unknown_hand_composition import (
    expand_private_prize_hand_composition,
    publicly_discard_unknown_other_hand,
)
from top_prize_physical_bridge import TopPrizePhysicalState

WORLDS = (
    ("S", "C", Fraction(2, 5)), ("F", "C", Fraction(1, 10)),
    ("S", "O", Fraction(1, 10)), ("F", "O", Fraction(2, 5)),
)
CLASS_GROUPS = {"S-class": "S", "sv3pt5-113": "C"}
PROFILE = BeforeHandPrizeProfile(
    "sv3pt5-113", "Chansey", "ability:Lucky Bonus",
    "self_to_bench", "in_play", True, True, "coin_heads", False,
)
OTHER_C = (0, 0, 1, 0)
OTHER_O = (0, 0, 0, 1)


def setup():
    prior = TopPrizeJointBelief(
        ("S", "F", "C", "O"), (False,),
        tuple(((top, (tag,)), float(p)) for top, tag, p in WORLDS),
    )
    beliefs = stage_one_pending_prize_for_observers(
        ObserverTopPrizeBeliefs((("actor", prior), ("opponent", prior))),
        position=0, visible_groups={"actor": "C"},
    )
    ledger = IdentityLedger(
        ZoneCountState(),
        (
            CardInstance("hand-c", "sv3pt5-113", "Chansey", "hand"),
            CardInstance("prize-c", "sv3pt5-113", "Chansey", "prize"),
            CardInstance("top-s", "S-class", "S", "deck_top"),
        ),
    )
    physical = TopPrizePhysicalState(ledger, "top-s", ("prize-c",), (False,))
    acquired = decline_prize_into_latent_hand(
        stage_prize_takes(physical, positions=(0,)),
        beliefs, PROFILE, actor_id="actor",
        group_by_card_class=CLASS_GROUPS,
        use_probability_by_group={"C": 0.6, "O": 0.0},
        during_own_turn=True,
    )
    assumptions = expand_private_prize_hand_composition(
        acquired,
        conditional_other_counts={
            "actor": {"C": {OTHER_C: 1.0}},
            "opponent": {
                "C": {OTHER_C: 0.25, OTHER_O: 0.75},
                "O": {OTHER_C: 0.75, OTHER_O: 0.25},
            },
        },
    )
    return ledger, acquired, assumptions


def exact_oracle():
    """Enumerate hidden tag, unknown other, and two labeled discard origins."""
    cond = {
        "C": {"C": Fraction(1, 4), "O": Fraction(3, 4)},
        "O": {"C": Fraction(3, 4), "O": Fraction(1, 4)},
    }
    weights = []
    for top, tag, prior in WORLDS:
        decline = 1 - (Fraction(3, 5) if tag == "C" else Fraction(0))
        for other, other_probability in cond[tag].items():
            for discarded_tag in (True, False):
                removed_group = tag if discarded_tag else other
                if removed_group != "C":
                    continue
                weight = prior * decline * other_probability * Fraction(1, 2)
                weights.append((top, tag, not discarded_tag, weight))
    evidence = sum(row[3] for row in weights)
    return (
        sum(p for _top, tag, _survived, p in weights if tag == "C") / evidence,
        sum(p for top, _tag, _survived, p in weights if top == "S") / evidence,
        sum(p for _top, _tag, survived, p in weights if survived) / evidence,
    )


def close(actual, expected):
    assert abs(actual - float(expected)) < 1e-12, (actual, expected)


def main():
    assert exact_oracle() == (
        Fraction(2, 5), Fraction(11, 25), Fraction(17, 25),
    )

    for chosen, survives in (("hand-c", True), ("prize-c", False)):
        original, acquired, expanded = setup()
        first = publicly_discard_unknown_other_hand(
            acquired, expanded,
            actor_id="actor",
            discarded_instance_id=chosen,
            group_by_card_class=CLASS_GROUPS,
        )
        other = first.beliefs.belief_for("opponent")
        target, top, survival = exact_oracle()
        close(other.tagged_probability("C"), target)
        close(other.top_probability("S"), top)
        close(other.tagged_survival_probability(), survival)
        actor = first.beliefs.belief_for("actor")
        close(actor.tagged_probability("C"), 1)
        close(actor.top_probability("S"), Fraction(4, 5))
        close(actor.tagged_survival_probability(), int(survives))
        assert first.physical.ledger.instance(chosen).zone == "discard"
        assert_conserved(original, first.physical.ledger)

        if survives:
            second = continue_random_hand_discard(
                first, actor_id="actor",
                discarded_instance_id="prize-c",
                group_by_card_class=CLASS_GROUPS,
            )
            posterior = second.beliefs.belief_for("opponent")
            close(posterior.tagged_probability("C"), 1)
            close(posterior.top_probability("S"), Fraction(4, 5))
            close(posterior.tagged_survival_probability(), 0)
            assert_conserved(original, second.physical.ledger)

    # A faulty independence projection over the other card's group changes
    # the inferred tagged-Chansey probability from 2/5 to 18/35.
    naive_other_c = Fraction(2, 7) * Fraction(1, 4) + Fraction(5, 7) * Fraction(3, 4)
    tag_prior = Fraction(2, 7)
    naive_c = (
        tag_prior * (1 + naive_other_c)
        / (tag_prior * (1 + naive_other_c)
           + (1 - tag_prior) * naive_other_c)
    )
    assert naive_c == Fraction(18, 35)
    assert naive_c != Fraction(2, 5)

    print("Unknown other-hand composition Bayesian regression passed")
    print("True P(tag C)=2/5 versus independent-composition P(tag C)=18/35")


if __name__ == "__main__":
    main()
