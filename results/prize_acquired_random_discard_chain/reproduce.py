"""Two public random hand discards: exact labeled permutation oracle."""

from fractions import Fraction
from itertools import permutations
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
from prize_acquired_random_discard import publicly_discard_random_hand_card
from prize_acquired_random_discard_chain import continue_random_hand_discard
from prize_pending_take import stage_prize_takes
from prize_top_swap_belief import TopPrizeJointBelief
from top_prize_physical_bridge import TopPrizePhysicalState

WORLDS = (
    ("S", "C", Fraction(2, 5)), ("F", "C", Fraction(1, 10)),
    ("S", "O", Fraction(1, 10)), ("F", "O", Fraction(2, 5)),
)
GROUPS = {"S-class": "S", "O-class": "O", "sv3pt5-113": "C"}
PROFILE = BeforeHandPrizeProfile(
    "sv3pt5-113", "Chansey", "ability:Lucky Bonus",
    "self_to_bench", "in_play", True, True, "coin_heads", False,
)


def make_start():
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
            CardInstance("hand-o", "O-class", "Other", "hand"),
            CardInstance("prize-c", "sv3pt5-113", "Chansey", "prize"),
            CardInstance("top-s", "S-class", "S", "deck_top"),
        ),
    )
    physical = TopPrizePhysicalState(ledger, "top-s", ("prize-c",), (False,))
    hand = decline_prize_into_latent_hand(
        stage_prize_takes(physical, positions=(0,)),
        beliefs, PROFILE, actor_id="actor",
        group_by_card_class=GROUPS,
        use_probability_by_group={"C": 0.6, "O": 0.0},
        during_own_turn=True,
    )
    return ledger, hand


def oracle(public_groups):
    worlds = []
    for top, tagged, prior in WORLDS:
        hand = (tagged, "C", "O")
        decline = 1 - (Fraction(3, 5) if tagged == "C" else 0)
        for first, second in permutations(range(3), 2):
            if (hand[first], hand[second]) != public_groups:
                continue
            worlds.append((
                top, tagged, 0 not in (first, second),
                prior * decline * Fraction(1, 6),
            ))
    evidence = sum(p for _top, _tag, _survives, p in worlds)
    return (
        sum(p for _top, tag, _survives, p in worlds if tag == "C") / evidence,
        sum(p for top, _tag, _survives, p in worlds if top == "S") / evidence,
        sum(p for _top, _tag, survives, p in worlds if survives) / evidence,
    )


def close(actual, expected):
    assert abs(actual - float(expected)) < 1e-12, (actual, expected)


def main():
    trials = (
        (("hand-c", "prize-c"), ("C", "C"), False),
        (("prize-c", "hand-c"), ("C", "C"), False),
        (("hand-c", "hand-o"), ("C", "O"), True),
        (("prize-c", "hand-o"), ("C", "O"), False),
        (("hand-o", "hand-c"), ("O", "C"), True),
        (("hand-o", "prize-c"), ("O", "C"), False),
    )
    for (first_id, second_id), public, actual_survival in trials:
        initial, acquired = make_start()
        first = publicly_discard_random_hand_card(
            acquired, actor_id="actor",
            discarded_instance_id=first_id,
            group_by_card_class=GROUPS,
            other_hand_counts={"C": 1, "O": 1},
        )
        second = continue_random_hand_discard(
            first, actor_id="actor",
            discarded_instance_id=second_id,
            group_by_card_class=GROUPS,
        )
        expected_tag, expected_top, expected_survival = oracle(public)
        other = second.beliefs.belief_for("opponent")
        close(other.tagged_probability("C"), expected_tag)
        close(other.top_probability("S"), expected_top)
        close(other.tagged_survival_probability(), expected_survival)
        actor = second.beliefs.belief_for("actor")
        close(actor.tagged_probability("C"), 1)
        close(actor.top_probability("S"), Fraction(4, 5))
        close(actor.tagged_survival_probability(), int(actual_survival))
        assert second.physical.ledger.instance(first_id).zone == "discard"
        assert second.physical.ledger.instance(second_id).zone == "discard"
        assert_conserved(initial, second.physical.ledger)

    for public, target, top, survives in (
        (("C", "C"), Fraction(1), Fraction(4, 5), Fraction(0)),
        (("C", "O"), Fraction(2, 7), Fraction(13, 35), Fraction(1, 2)),
        (("O", "C"), Fraction(2, 7), Fraction(13, 35), Fraction(1, 2)),
        (("O", "O"), Fraction(0), Fraction(1, 5), Fraction(0)),
    ):
        assert oracle(public) == (target, top, survives)

    print("Two successive random discards exact permutation oracle passed")
    print("Different groups C,O or O,C restore P(tag=C)=2/7 and P(top S)=13/35")
    print("Same group C,C proves tag=C and tag removed")


if __name__ == "__main__":
    main()
