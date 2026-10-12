"""Independent exact-rational oracle and physical Prize-discard integration."""

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
from prize_hand_copy_budget import condition_joint_hand_on_copy_budget
from prize_pending_take import stage_prize_takes
from prize_top_swap_belief import TopPrizeJointBelief
from prize_unknown_hand_composition import (
    LatentHandCompositionBelief, ObserverLatentHandCompositionBeliefs,
    publicly_discard_unknown_other_hand,
)
from top_prize_physical_bridge import TopPrizePhysicalState

GROUPS = ("S", "F", "C", "O")
WORLDS = (("S", "C", "O"), ("F", "C", "C"),
          ("S", "O", "C"), ("F", "O", "O"))
CAPS = {"S": 1, "F": 1, "C": 1, "O": 2}
CLASSES = {"S-class": "S", "C-class": "C", "O-class": "O"}


def state(top, tag, other):
    return (top, (), tag, tuple(int(g == other) for g in GROUPS))


def prior():
    opponent = LatentHandCompositionBelief(
        GROUPS, (), tuple((state(*world), .25) for world in WORLDS),
    )
    actor = LatentHandCompositionBelief(
        GROUPS, (), ((state(*WORLDS[0]), 1.0),),
    )
    return ObserverLatentHandCompositionBeliefs(
        (("actor", actor), ("opponent", opponent)),
    )


def acquired_fixture():
    material = TopPrizePhysicalState(
        IdentityLedger(ZoneCountState(), (
            CardInstance("other-o", "O-class", "Other", "hand"),
            CardInstance("prize-c", "C-class", "Chansey", "prize"),
            CardInstance("top-s", "S-class", "S", "deck_top"),
        )),
        "top-s", ("prize-c",), (False,),
    )
    source = TopPrizeJointBelief(GROUPS, (False,), (
        (("S", ("C",)), 0.5), (("F", ("C",)), 0.5),
    ))
    pending = stage_one_pending_prize_for_observers(
        ObserverTopPrizeBeliefs((("actor", source), ("opponent", source))),
        position=0, visible_groups={"actor": "C"},
    )
    profile = BeforeHandPrizeProfile(
        "C-class", "Chansey", "ability:Lucky Bonus",
        "self_to_bench", "in_play", True, True, "coin_heads", False,
    )
    result = decline_prize_into_latent_hand(
        stage_prize_takes(material, positions=(0,)),
        pending, profile, actor_id="actor",
        group_by_card_class=CLASSES,
        use_probability_by_group={"C": 0.6, "O": 0.0},
        during_own_turn=True,
    )
    return material.ledger, result


def oracle(prune):
    hits = []
    for top, tag, other in WORLDS:
        counts = Counter((top, tag, other))
        if prune and any(counts[g] > CAPS[g] for g in CAPS):
            continue
        for discard_tag in (True, False):
            if (tag if discard_tag else other) == "C":
                hits.append((top, tag, not discard_tag, F(1, 8)))
    likelihood = sum(w for *_rest, w in hits)
    return (
        sum(w for top, _tag, _survives, w in hits if top == "S") / likelihood,
        sum(w for _top, tag, _survives, w in hits if tag == "C") / likelihood,
        sum(w for _top, _tag, survives, w in hits if survives) / likelihood,
    )


def check(actual, expected):
    assert abs(actual - float(expected)) < 1e-12, (actual, expected)


def must_raise(callback):
    try:
        callback()
    except ValueError:
        return
    raise AssertionError("invalid copy inventory accepted")


def main():
    unfiltered = prior()
    filtered = condition_joint_hand_on_copy_budget(
        unfiltered, total_deck_copies=CAPS,
    )
    assert len(filtered.belief_for("opponent").masses) == 3
    assert oracle(False) == (F(1, 2), F(3, 4), F(1, 4))
    assert oracle(True) == (F(1), F(1, 2), F(1, 2))

    old_ledger, acquired = acquired_fixture()
    for belief, expected in (
        (unfiltered, oracle(False)), (filtered, oracle(True)),
    ):
        outcome = publicly_discard_unknown_other_hand(
            acquired, belief, actor_id="actor",
            discarded_instance_id="prize-c", group_by_card_class=CLASSES,
        )
        observer = outcome.beliefs.belief_for("opponent")
        check(observer.top_probability("S"), expected[0])
        check(observer.tagged_probability("C"), expected[1])
        check(observer.tagged_survival_probability(), expected[2])
        assert outcome.physical.ledger.instance("prize-c").zone == "discard"
        assert_conserved(old_ledger, outcome.physical.ledger)

    must_raise(lambda: condition_joint_hand_on_copy_budget(
        unfiltered, total_deck_copies={**CAPS, "S": -1},
    ))
    must_raise(lambda: condition_joint_hand_on_copy_budget(
        unfiltered, total_deck_copies=CAPS,
        publicly_known_elsewhere={"C": 2},
    ))
    must_raise(lambda: condition_joint_hand_on_copy_budget(
        unfiltered, total_deck_copies={**CAPS, "C": 0, "O": 0},
    ))
    must_raise(lambda: condition_joint_hand_on_copy_budget(
        unfiltered, total_deck_copies={"S": 1, "F": 1},
    ))
    print("Copy-capacity Bayesian and physical-card regression passed")
    print("Before: P(top S)=1/2, P(tag C)=3/4")
    print("After:  P(top S)=1, P(tag C)=1/2")


if __name__ == "__main__":
    main()
