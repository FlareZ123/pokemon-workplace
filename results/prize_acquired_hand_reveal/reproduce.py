"""Regression: private Prize identity survives later public hand-card sampling."""

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
from prize_acquired_hand_reveal import (
    decline_prize_into_latent_hand,
    publicly_reveal_random_hand_card,
)
from prize_pending_take import stage_prize_takes
from prize_top_swap_belief import TopPrizeJointBelief
from top_prize_physical_bridge import TopPrizePhysicalState

GROUPS = {"S-class": "S", "O-class": "O", "sv3pt5-113": "C"}
PROFILE = BeforeHandPrizeProfile(
    "sv3pt5-113", "Chansey", "ability:Lucky Bonus", "self_to_bench",
    "in_play", True, True, "coin_heads", False,
)
WORLDS = (
    ("S", "C", Fraction(2, 5)),
    ("F", "C", Fraction(1, 10)),
    ("S", "O", Fraction(1, 10)),
    ("F", "O", Fraction(2, 5)),
)


def setup():
    prior = TopPrizeJointBelief(
        ("S", "F", "C", "O"), (False,),
        tuple(((top, (card,)), float(p)) for top, card, p in WORLDS),
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
    physical = TopPrizePhysicalState(
        ledger, "top-s", ("prize-c",), (False,),
    )
    return ledger, stage_prize_takes(physical, positions=(0,)), beliefs


def oracle(reveal):
    use = {"C": Fraction(3, 5), "O": Fraction(0)}
    weighted = tuple(
        (top, card, p * (1 - use[card]) * Fraction(1 + int(card == reveal), 3))
        for top, card, p in WORLDS
    )
    normalizer = sum(weight for _top, _card, weight in weighted)
    return (
        sum(weight for _top, card, weight in weighted if card == "C") / normalizer,
        sum(weight for top, _card, weight in weighted if top == "S") / normalizer,
    )


def close(actual, expected):
    assert abs(actual - float(expected)) <= 1e-12, (actual, expected)


def main():
    first, pending, beliefs = setup()
    private_hand = decline_prize_into_latent_hand(
        pending, beliefs, PROFILE,
        actor_id="actor",
        group_by_card_class=GROUPS,
        use_probability_by_group={"C": 0.6, "O": 0.0},
        during_own_turn=True,
    )
    final_ledger = private_hand.transition.after.physical.ledger
    assert final_ledger.instance("prize-c").zone == "hand"
    assert_conserved(first, final_ledger)
    opponent = private_hand.beliefs.belief_for("opponent")
    close(opponent.target_probability("C"), Fraction(2, 7))
    close(opponent.top_probability("S"), Fraction(13, 35))
    close(
        private_hand.project_without_hand_identity()
        .belief_for("opponent").top_probability("S"),
        Fraction(13, 35),
    )

    for instance, group in (("hand-c", "C"), ("hand-o", "O")):
        after = publicly_reveal_random_hand_card(
            private_hand, observed_instance_id=instance,
            group_by_card_class=GROUPS,
            other_hand_counts={"C": 1, "O": 1},
        )
        expected_card, expected_top = oracle(group)
        observed = after.beliefs.belief_for("opponent")
        close(observed.target_probability("C"), expected_card)
        close(observed.top_probability("S"), expected_top)
        close(after.beliefs.belief_for("actor").top_probability("S"), Fraction(4, 5))
        assert after.transition.after.physical.ledger == final_ledger
        assert_conserved(first, final_ledger)

    for other in ({"C": 0, "O": 1}, {"C": 2, "O": 1}):
        try:
            publicly_reveal_random_hand_card(
                private_hand, observed_instance_id="hand-c",
                group_by_card_class=GROUPS, other_hand_counts=other,
            )
        except ValueError:
            pass
        else:
            raise AssertionError("mismatched hand inventory was accepted")
    print("Latent Prize-to-hand random-reveal checks passed")
    print("Reveal C: P(tagged C)=4/9; P(top S)=7/15")
    print("Reveal O: P(tagged C)=1/6; P(top S)=3/10")


if __name__ == "__main__":
    main()
