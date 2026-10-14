"""Exact K0 physical-search decision when singleton Radiant may be Prized."""

from __future__ import annotations

from fractions import Fraction
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from discard_cost_witness import DiscardCandidate
from k0_physical_search_policy import (
    AcquisitionGoal,
    K0BeliefWorld,
    K0PhysicalSearchFamily,
    evaluate_k0_physical_search,
)
from multicopy_zone_state import ZoneCountState
from physical_staged_trainer_policy import PhysicalSearchOption
from search_zone_transition import SearchZoneTarget
from trainer_search_profile_compiler import (
    CompiledTrainerSearchProfile,
    SearchOutput,
)
from trainer_search_transaction import TrainerSearchExecutionState
from typed_search_retrieval import enumerate_typed_retrieval_actions
from typed_search_target_allocator import (
    BASIC_POKEMON,
    TYPE_PREFIX,
    TargetGroup,
)


def card(card_id: str) -> dict:
    set_id = card_id.split("-", 1)[0]
    cards = json.loads(
        (ROOT / "resources" / "cards" / "en" / f"{set_id}.json")
        .read_text(encoding="utf-8")
    )
    return next(card for card in cards if card["id"] == card_id)


def physical_world(*, radiant_prized: bool) -> TrainerSearchExecutionState:
    # A fully conserved 60-card population. Seven cards remain in hand
    # after a valid Basic starting Active has been promoted; one natural
    # draw is already among those seven. Six Prizes and 46 deck cards.
    # Generic neutral cards are a controlled physical-count abstraction.
    counts = {
        ("treasure", "hand"): 1,
        ("psychic_energy", "hand"): 1,
        ("starter_basic", "active"): 1,
        ("neutral", "hand"): 5,
        ("neutral", "prize"): 5 if radiant_prized else 6,
        ("neutral", "deck"): 46 if radiant_prized else 45,
        ("radiant", "prize" if radiant_prized else "deck"): 1,
    }
    state = TrainerSearchExecutionState(
        zones=ZoneCountState.from_mapping(counts)
    )
    assert sum(count for _, _, count in state.zones.counts) == 60
    assert sum(
        count for _, zone, count in state.zones.counts
        if zone == "deck"
    ) == 46
    assert sum(
        count for _, zone, count in state.zones.counts
        if zone == "prize"
    ) == 6
    assert sum(
        count for _, zone, count in state.zones.counts
        if zone == "hand"
    ) == 7
    return state


def expect_value_error(fn) -> bool:
    try:
        fn()
    except ValueError:
        return True
    return False


def main() -> None:
    treasure_print = card("sm6-113")
    radiant_print = card("swsh12pt5-105")
    assert treasure_print["name"] == "Mysterious Treasure"
    assert "Discard a card from your hand" in " ".join(
        treasure_print["rules"]
    )
    assert "Psychic or Dragon Pokémon" in " ".join(
        treasure_print["rules"]
    )
    assert radiant_print["name"] == "Radiant Eternatus"
    assert "Dragon" in radiant_print["types"]
    assert "Basic" in radiant_print["subtypes"]

    # Restricted strategic option of the source's broader Psychic/Dragon
    # search. Zero retrieval is legal because the search is restricted
    # and its physical one-card payment changes the game state.
    profile = CompiledTrainerSearchProfile(
        card_id=treasure_print["id"],
        name="Mysterious Treasure / Dragon-only branch",
        action_class="Item",
        base_outputs=(SearchOutput("Dragon Pokémon", 1),),
        required_discard_other_cards=1,
    )
    targets = (
        SearchZoneTarget(
            "radiant",
            TargetGroup(
                "Radiant Eternatus", 1,
                frozenset({BASIC_POKEMON, TYPE_PREFIX + "dragon"}),
            ),
        ),
    )
    available = enumerate_typed_retrieval_actions(
        profile.base_outputs,
        (targets[0].group,),
    )
    assert {a.target_cost for a in available} == {(0,), (1,)}
    candidates = (DiscardCandidate("psychic_energy"),)
    variants = tuple(
        PhysicalSearchOption(
            "retrieve Radiant" if a.target_cost == (1,) else "zero target",
            profile,
            "treasure",
            targets,
            a,
            discard_candidates=candidates,
        )
        for a in available
    )
    action = K0PhysicalSearchFamily("Play Treasure", variants)

    # Conditional on the same known eight-card exposure (including the
    # opened Basic) and an unseen Radiant, six random Prizes among the
    # other 52 cards give P(Radiant remains in 46-card deck)=46/52.
    worlds = (
        K0BeliefWorld(
            physical_world(radiant_prized=False),
            Fraction(46, 52),
        ),
        K0BeliefWorld(
            physical_world(radiant_prized=True),
            Fraction(6, 52),
        ),
    )
    assert worlds[0].state.zones.count("radiant", "deck") == 1
    assert worlds[1].state.zones.count("radiant", "prize") == 1

    high_value = evaluate_k0_physical_search(
        worlds,
        families=(action,),
        acquisition_goals=(AcquisitionGoal("radiant"),),
        reward_per_unit=Fraction(3),
        penalty_per_discard=Fraction(1),
    )
    assert high_value.selected_family == "Play Treasure"
    assert high_value.selected_payment is not None
    assert high_value.selected_payment.cost == 1
    assert high_value.world_completed_units == (1, 0)
    assert high_value.world_retrieval_variants == (
        "retrieve Radiant", "zero target"
    )
    assert high_value.expected_utility == Fraction(43, 26)
    assert high_value.oracle_expected_utility == Fraction(23, 13)
    assert high_value.value_of_hidden_information == Fraction(3, 26)

    # A narrower reward/cost policy reverses the optimal K0 action.
    # Only a clairvoyant policy can reserve its payment exclusively
    # for worlds where Radiant is known to be searchable.
    near_threshold = evaluate_k0_physical_search(
        worlds,
        families=(action,),
        acquisition_goals=(AcquisitionGoal("radiant"),),
        reward_per_unit=Fraction(21, 20),
        penalty_per_discard=Fraction(1),
    )
    assert near_threshold.selected_family is None
    assert near_threshold.expected_utility == 0
    assert near_threshold.oracle_expected_utility == Fraction(23, 520)
    assert (
        near_threshold.value_of_hidden_information
        == Fraction(23, 520)
    )

    # If hidden Prize truth is accidentally exposed in the hand or
    # public board, states must not be bundled into a single K0 belief.
    different_visible = TrainerSearchExecutionState(
        zones=worlds[1].state.zones.move(
            "neutral", "hand", "discard"
        )
    )
    assert expect_value_error(
        lambda: evaluate_k0_physical_search(
            (worlds[0], K0BeliefWorld(
                different_visible, Fraction(6, 52)
            )),
            families=(action,),
            acquisition_goals=(AcquisitionGoal("radiant"),),
        )
    )
    assert expect_value_error(
        lambda: evaluate_k0_physical_search(
            (
                K0BeliefWorld(worlds[0].state, Fraction(1, 2)),
                K0BeliefWorld(worlds[1].state, Fraction(1, 4)),
            ),
            families=(action,),
            acquisition_goals=(AcquisitionGoal("radiant"),),
        )
    )

    print(json.dumps({
        "source_prints": (treasure_print["id"], radiant_print["id"]),
        "p_radiant_searchable": str(Fraction(46, 52)),
        "p_radiant_prized": str(Fraction(6, 52)),
        "high_reward_K0_action": high_value.selected_family,
        "high_reward_expected_utility": str(
            high_value.expected_utility
        ),
        "high_reward_clairvoyance_gap": str(
            high_value.value_of_hidden_information
        ),
        "near_threshold_K0_action": near_threshold.selected_family,
        "near_threshold_clairvoyance_gap": str(
            near_threshold.value_of_hidden_information
        ),
        "source": "physical card-text subset, hypothetical utility units",
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
