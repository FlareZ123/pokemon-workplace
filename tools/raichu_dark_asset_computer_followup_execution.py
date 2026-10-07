"""Physical target-Prized Dark Asset -> Computer Search continuation.

Representative branch:
Quick Ball -> Crobat V -> Dark Asset draws Computer Search -> full-deck
inspection establishes Alolan Raichu is Prized -> Computer Search selects Gladion.

The Computer Search step delegates to the repository's observer-relative private
search transaction, so K1, private target identity, shuffle topology, and
physical conservation stay synchronized.
"""

from __future__ import annotations

from dataclasses import dataclass

from bench_state_kernel import BenchState
from computer_search_private_transaction import (
    ComputerSearchPrivateTransaction,
    execute_computer_search_private_transaction,
)
from deck_search_shuffle_topology import SearchableDeckPhysicalState
from discard_cost_witness import DiscardCandidate, DiscardSelection
from identity_materialization import IdentityLedger, materialize
from prize_position_belief import PrizePositionBelief
from prize_slot_visibility import PrizeSlotVisibilityBelief
from raichu_search_to_crobat_execution import (
    SearchToCrobatExecution,
    execute_search_to_crobat,
)
from trainer_search_transaction import TrainerSearchExecutionState


RAICHU_GROUP = "raichu"
GLADION_GROUP = "gladion"
GROUPS = (RAICHU_GROUP, GLADION_GROUP)


@dataclass(frozen=True)
class QuickDarkAssetComputerExecution:
    first: SearchToCrobatExecution
    after_dark_asset_draw: TrainerSearchExecutionState
    computer: ComputerSearchPrivateTransaction


def single_prize_zone_adaptive_prior() -> PrizeSlotVisibilityBelief:
    """Uniform one-Prize prior over Raichu, Gladion, or one filler card."""

    return PrizeSlotVisibilityBelief.all_face_down(
        PrizePositionBelief(
            GROUPS,
            1,
            (
                ((None,), 1.0 / 3.0),
                ((GLADION_GROUP,), 1.0 / 3.0),
                ((RAICHU_GROUP,), 1.0 / 3.0),
            ),
        )
    )


ZONE_ADAPTIVE_POLICY = {
    (1, 0): {GLADION_GROUP: 1.0},
    (0, 1): {RAICHU_GROUP: 1.0},
    (0, 0): {RAICHU_GROUP: 1.0},
}


def execute_quick_dark_asset_computer_gladion(
    state: TrainerSearchExecutionState,
    bench: BenchState,
    *,
    quick_discard_candidates: tuple[DiscardCandidate, ...],
    quick_discard_selection: DiscardSelection,
    computer_discard_candidates: tuple[DiscardCandidate, ...],
    computer_discard_selection: DiscardSelection,
    actor_id: str = "actor",
    observer_id: str = "observer",
    crobat_card_class: str = "crobat_v",
    computer_card_class: str = "computer_search",
    raichu_card_class: str = "alolan_raichu",
    gladion_card_class: str = "gladion",
    filler_card_class: str = "filler",
) -> QuickDarkAssetComputerExecution:
    """Execute one exact target-Prized adaptive Computer Search witness."""

    first = execute_search_to_crobat(
        state,
        bench,
        action_card_class="quick_ball",
        crobat_card_class=crobat_card_class,
        discard_candidates=quick_discard_candidates,
        discard_selection=quick_discard_selection,
    )
    if not first.crobat_benched:
        raise ValueError("Crobat V could not enter the Bench")
    if first.dark_asset_draw_count < 1:
        raise ValueError("Dark Asset has no draw capacity")
    if first.zones_after_bench.count(computer_card_class, "deck") < 1:
        raise ValueError("Computer Search is not available as the exact Dark Asset draw")

    after_draw_zones = first.zones_after_bench.move(
        computer_card_class,
        "deck",
        "hand",
    )
    after_dark_asset_draw = TrainerSearchExecutionState(
        zones=after_draw_zones,
        budget=first.transaction.after.budget,
        channels=first.transaction.after.channels,
    )

    if after_draw_zones.count(raichu_card_class, "prize") != 1:
        raise ValueError("representative branch requires exactly one Prized Alolan Raichu")
    if after_draw_zones.count(gladion_card_class, "deck") != 1:
        raise ValueError("representative branch requires one deck-resident Gladion")
    if after_draw_zones.count(filler_card_class, "deck") != 1:
        raise ValueError("representative branch requires one deck-resident filler")

    represented_deck_prize = sum(
        count
        for _card_class, zone, count in after_draw_zones.counts
        if zone in {"deck", "prize"}
    )
    if represented_deck_prize != 3:
        raise ValueError(
            "representative information witness requires exactly three deck-plus-Prize cards"
        )

    ledger = IdentityLedger(after_draw_zones)
    ledger = materialize(
        ledger,
        card_class=raichu_card_class,
        card_name="Alolan Raichu",
        source_zone="prize",
        instance_id="prize-raichu",
    )
    physical = SearchableDeckPhysicalState(
        ledger,
        ("prize-raichu",),
        (False,),
    )
    execution = TrainerSearchExecutionState(
        zones=ledger.exchangeable,
        budget=after_dark_asset_draw.budget,
        channels=after_dark_asset_draw.channels,
    )

    prior = single_prize_zone_adaptive_prior()
    computer = execute_computer_search_private_transaction(
        physical,
        execution,
        ((actor_id, prior), (observer_id, prior)),
        actor_id=actor_id,
        action_card_class=computer_card_class,
        discard_candidates=computer_discard_candidates,
        discard_selection=computer_discard_selection,
        target_probability_by_composition=ZONE_ADAPTIVE_POLICY,
        group_by_card_class={
            raichu_card_class: RAICHU_GROUP,
            gladion_card_class: GLADION_GROUP,
        },
        target_card_class=gladion_card_class,
        target_card_name="Gladion",
        target_instance_id="private-gladion",
        sampled_top_card_class=filler_card_class,
        sampled_top_card_name="Filler",
        sampled_top_instance_id="top-filler",
    )

    actor = computer.beliefs_after.belief_for(actor_id)
    if actor.prize_probability_at(0, RAICHU_GROUP) != 1.0:
        raise AssertionError("actor K1 belief did not collapse onto Prized Alolan Raichu")

    return QuickDarkAssetComputerExecution(
        first=first,
        after_dark_asset_draw=after_dark_asset_draw,
        computer=computer,
    )
