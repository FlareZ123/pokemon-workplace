"""Reproduce exact Bayesian policy signal and conserving Chansey E-31 branches."""

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
from prize_optional_trigger_signal import (
    condition_on_pending_trigger_decision,
    resolve_direct_optional_prize_trigger_with_observers,
)
from prize_pending_take import stage_prize_takes
from prize_top_swap_belief import TopPrizeJointBelief
from top_prize_physical_bridge import TopPrizePhysicalState


WORLDS = (
    ("S", "C", Fraction(2, 5)),
    ("F", "C", Fraction(1, 10)),
    ("S", "O", Fraction(1, 10)),
    ("F", "O", Fraction(2, 5)),
)
GROUPS = ("S", "F", "C", "O")
CLASS_GROUPS = {"S-class": "S", "sv3pt5-113": "C"}
POLICY = {"C": 0.6, "O": 0.0}
PROFILE = BeforeHandPrizeProfile(
    card_id="sv3pt5-113",
    card_name="Chansey",
    source="ability:Lucky Bonus",
    activation_family="self_to_bench",
    self_destination="in_play",
    during_own_turn_explicit=True,
    card_text_requires_open_bench=True,
    extra_prize_mode="coin_heads",
    searches_pokemon_to_bench=False,
)


def oracle(use: bool) -> tuple[Fraction, Fraction]:
    """Independent rational enumeration of all four hidden worlds."""
    policy = {"C": Fraction(3, 5), "O": Fraction(0)}
    weighted = [
        (top, pending, prior * (policy[pending] if use else 1 - policy[pending]))
        for top, pending, prior in WORLDS
    ]
    evidence = sum(weight for _top, _pending, weight in weighted)
    return (
        sum(weight for top, _pending, weight in weighted if top == "S") / evidence,
        sum(weight for _top, pending, weight in weighted if pending == "C") / evidence,
    )


def make_state():
    prior = TopPrizeJointBelief(
        GROUPS,
        (False,),
        tuple(
            ((top, (pending,)), float(probability))
            for top, pending, probability in WORLDS
        ),
    )
    observers = ObserverTopPrizeBeliefs((("actor", prior), ("opponent", prior)))
    pending_beliefs = stage_one_pending_prize_for_observers(
        observers,
        position=0,
        visible_groups={"actor": "C"},
    )
    initial = IdentityLedger(
        ZoneCountState(),
        (
            CardInstance("prize-chansey", "sv3pt5-113", "Chansey", "prize"),
            CardInstance("top-s", "S-class", "S", "deck_top"),
        ),
    )
    physical = TopPrizePhysicalState(
        initial, "top-s", ("prize-chansey",), (False,),
    )
    return initial, stage_prize_takes(physical, positions=(0,)), pending_beliefs


def close(actual: float, expected: Fraction | float) -> None:
    assert abs(actual - float(expected)) < 1e-12, (actual, expected)


def main() -> None:
    for use in (True, False):
        initial, pending, beliefs = make_state()
        assert beliefs.belief_for("actor").pending_probability("C") == 1.0
        close(beliefs.belief_for("opponent").pending_probability("C"), 0.5)
        prediction = condition_on_pending_trigger_decision(
            beliefs,
            actor_id="actor",
            actor_observed_group="C",
            observed_use=use,
            use_probability_by_group=POLICY,
        )
        expected_top, expected_chansey = oracle(use)
        close(prediction.belief_for("opponent").top_probability("S"), expected_top)
        close(
            prediction.belief_for("opponent").pending_probability("C"),
            expected_chansey,
        )
        resolved = resolve_direct_optional_prize_trigger_with_observers(
            pending,
            beliefs,
            PROFILE,
            actor_id="actor",
            group_by_card_class=CLASS_GROUPS,
            observed_use=use,
            use_probability_by_group=POLICY,
            during_own_turn=True,
            bench_open=True,
            board_object_id="bench-chansey" if use else None,
            coin_heads=False if use else None,
        )
        assert_conserved(initial, resolved.physical.after.physical.ledger)
        assert not resolved.physical.after.pending
        expected_zone = "in_play" if use else "hand"
        instance = resolved.physical.after.physical.ledger.instance("prize-chansey")
        assert instance.zone == expected_zone
        assert instance.board_object_id == (
            "bench-chansey" if use else None
        )
        close(
            resolved.beliefs_after.belief_for("opponent").top_probability("S"),
            expected_top,
        )
        close(
            resolved.beliefs_after.belief_for("actor").top_probability("S"),
            Fraction(4, 5),
        )

    _, pending, beliefs = make_state()
    try:
        resolve_direct_optional_prize_trigger_with_observers(
            pending, beliefs, PROFILE,
            actor_id="actor", group_by_card_class=CLASS_GROUPS,
            observed_use=True, use_probability_by_group=POLICY,
            during_own_turn=True, bench_open=False,
            board_object_id="bench-chansey", coin_heads=False,
        )
    except ValueError as error:
        assert "Bench" in str(error)
    else:
        raise AssertionError("full-Bench activation must be rejected")

    for bad_policy in (
        {"C": 0.0, "O": 0.0},
        {"C": 1.5, "O": 0.0},
        {"C": 0.6},
    ):
        try:
            condition_on_pending_trigger_decision(
                beliefs,
                actor_id="actor",
                actor_observed_group="C",
                observed_use=True,
                use_probability_by_group=bad_policy,
            )
        except ValueError:
            pass
        else:
            raise AssertionError(f"invalid policy was accepted: {bad_policy}")

    print("E-31 optional-trigger public-decision signal checks passed")
    print("Exact activation: P(top=S)=4/5; P(pending=C)=1")
    print("Exact decline: P(top=S)=13/35; P(pending=C)=2/7")


if __name__ == "__main__":
    main()
