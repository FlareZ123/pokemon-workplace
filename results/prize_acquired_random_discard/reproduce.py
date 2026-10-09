"""Exact public random-hand discard, hidden-origin and conservation regression."""

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
from prize_acquired_random_discard import publicly_discard_random_hand_card
from prize_pending_take import stage_prize_takes
from prize_top_swap_belief import TopPrizeJointBelief
from top_prize_physical_bridge import TopPrizePhysicalState

GROUP_MAP = {"S-class": "S", "O-class": "O", "sv3pt5-113": "C"}
PROFILE = BeforeHandPrizeProfile(
    "sv3pt5-113", "Chansey", "ability:Lucky Bonus",
    "self_to_bench", "in_play", True, True, "coin_heads", False,
)
WORLDS = (
    ("S", "C", Fraction(2, 5)), ("F", "C", Fraction(1, 10)),
    ("S", "O", Fraction(1, 10)), ("F", "O", Fraction(2, 5)),
)


def initial_state():
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
    physical = TopPrizePhysicalState(ledger, "top-s", ("prize-c",), (False,))
    acquired = decline_prize_into_latent_hand(
        stage_prize_takes(physical, positions=(0,)),
        beliefs,
        PROFILE,
        actor_id="actor",
        group_by_card_class=GROUP_MAP,
        use_probability_by_group={"C": 0.6, "O": 0.0},
        during_own_turn=True,
    )
    return ledger, acquired


def exact_fraction_oracle(observed):
    likelihood = {"C": Fraction(2, 3) if observed == "C" else Fraction(1, 3),
                  "O": Fraction(1, 3) if observed == "C" else Fraction(2, 3)}
    use = {"C": Fraction(3, 5), "O": Fraction(0)}
    weighted = [
        (top, card, p * (1 - use[card]) * likelihood[card])
        for top, card, p in WORLDS
    ]
    total = sum(p for _top, _card, p in weighted)
    target = sum(p for _top, card, p in weighted if card == "C") / total
    top = sum(p for t, _card, p in weighted if t == "S") / total
    tag_survival = (
        target * (Fraction(1, 2) if observed == "C" else 1)
        + (1 - target) * (1 if observed == "C" else Fraction(1, 2))
    )
    return target, top, tag_survival


def close(actual, expected):
    assert abs(actual - float(expected)) < 1e-12, (actual, expected)


def main():
    for instance, observed, tag_was_discarded in (
        ("hand-c", "C", False),
        ("prize-c", "C", True),
        ("hand-o", "O", False),
    ):
        initial, acquired = initial_state()
        result = publicly_discard_random_hand_card(
            acquired,
            actor_id="actor",
            discarded_instance_id=instance,
            group_by_card_class=GROUP_MAP,
            other_hand_counts={"C": 1, "O": 1},
        )
        assert result.physical.ledger.instance(instance).zone == "discard"
        assert_conserved(initial, result.physical.ledger)
        expected_tag, expected_top, expected_survival = exact_fraction_oracle(observed)
        opponent = result.beliefs.belief_for("opponent")
        close(opponent.tagged_probability("C"), expected_tag)
        close(opponent.top_probability("S"), expected_top)
        close(opponent.tagged_survival_probability(), expected_survival)
        actor = result.beliefs.belief_for("actor")
        close(actor.tagged_probability("C"), 1)
        close(actor.top_probability("S"), Fraction(4, 5))
        close(actor.tagged_survival_probability(), int(not tag_was_discarded))

    initial, acquired = initial_state()
    try:
        publicly_discard_random_hand_card(
            acquired,
            actor_id="actor",
            discarded_instance_id="hand-c",
            group_by_card_class=GROUP_MAP,
            other_hand_counts={"C": 2, "O": 1},
        )
    except ValueError:
        pass
    else:
        raise AssertionError("impossible claimed hand inventory was accepted")

    print("Random discard of acquired Prize: exact regression passed")
    print("Public C: P(tag C)=4/9, P(top S)=7/15, P(tag survives)=7/9")
    print("Public O: P(tag C)=1/6, P(top S)=3/10, P(tag survives)=7/12")


if __name__ == "__main__":
    main()
