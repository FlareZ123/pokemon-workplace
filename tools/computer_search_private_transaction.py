"""Atomic Computer Search execution with private target information.

This adapter is intentionally card-specific. It composes the existing physical
discard witness, Item-play channel, private unrestricted-search belief bridge,
and identity ledger without weakening the constrained typed Trainer-search path.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from deck_search_shuffle_topology import SearchableDeckPhysicalState
from discard_cost_witness import (
    DiscardCandidate,
    DiscardSelection,
    apply_discard_selection,
)
from identity_materialization import IdentityLedger, assert_conserved
from observer_top_prize_beliefs import ObserverTopPrizeBeliefs
from private_search_target_belief import PrivateTargetPolicy
from private_search_target_physical import (
    PhysicalPrivateSearchShuffleTransition,
    resolve_physical_private_search_shuffle,
)
from prize_position_belief import PrizeGroup
from prize_slot_visibility import PrizeSlotVisibilityBelief
from top_prize_physical_bridge import TopPrizePhysicalState
from trainer_search_transaction import (
    RESOLVING_TRAINER_ZONE,
    TrainerSearchExecutionState,
)


COMPUTER_SEARCH_DISCARD_COST = 2


@dataclass(frozen=True)
class ComputerSearchPrivateTransaction:
    before: TrainerSearchExecutionState
    after: TrainerSearchExecutionState
    physical_before: SearchableDeckPhysicalState
    physical_after_cost: SearchableDeckPhysicalState
    private_search: PhysicalPrivateSearchShuffleTransition
    physical_after: TopPrizePhysicalState
    beliefs_after: ObserverTopPrizeBeliefs
    discard_selection: DiscardSelection
    target_instance_id: str


def execute_computer_search_private_transaction(
    physical: SearchableDeckPhysicalState,
    execution_state: TrainerSearchExecutionState,
    prizes_by_observer: Sequence[tuple[str, PrizeSlotVisibilityBelief]],
    *,
    actor_id: str,
    action_card_class: str,
    discard_candidates: Sequence[DiscardCandidate],
    discard_selection: DiscardSelection,
    target_probability_by_composition: PrivateTargetPolicy,
    group_by_card_class: Mapping[str, PrizeGroup],
    target_card_class: str,
    target_card_name: str,
    target_instance_id: str,
    sampled_top_card_class: str,
    sampled_top_card_name: str,
    sampled_top_instance_id: str,
) -> ComputerSearchPrivateTransaction:
    """Execute one bundled Computer Search-style private exact-one search."""

    if not action_card_class:
        raise ValueError("action_card_class must be non-empty")
    if execution_state.zones != physical.ledger.exchangeable:
        raise ValueError(
            "execution zones must equal the physical exchangeable ledger"
        )
    if not execution_state.channels.item_play:
        raise ValueError("Item play is locked")
    if execution_state.zones.count(action_card_class, "hand") < 1:
        raise ValueError("Computer Search is not in hand")
    if any(
        zone == RESOLVING_TRAINER_ZONE
        for _card_class, zone, _count in execution_state.zones.counts
    ):
        raise ValueError("state already contains a resolving Trainer")
    if discard_selection.cost != COMPUTER_SEARCH_DISCARD_COST:
        raise ValueError(
            f"Computer Search requires exactly {COMPUTER_SEARCH_DISCARD_COST} "
            "discarded cards"
        )

    working = execution_state.zones.move(
        action_card_class,
        "hand",
        RESOLVING_TRAINER_ZONE,
    )
    working = apply_discard_selection(
        working,
        tuple(discard_candidates),
        discard_selection,
    ).after

    after_cost = SearchableDeckPhysicalState(
        IdentityLedger(working, physical.ledger.instances),
        physical.prize_instance_ids,
        physical.face_up,
    )
    assert_conserved(physical.ledger, after_cost.ledger)

    private_search = resolve_physical_private_search_shuffle(
        after_cost,
        prizes_by_observer,
        actor_id=actor_id,
        target_probability_by_composition=target_probability_by_composition,
        group_by_card_class=group_by_card_class,
        target_card_class=target_card_class,
        target_card_name=target_card_name,
        target_instance_id=target_instance_id,
        sampled_top_card_class=sampled_top_card_class,
        sampled_top_card_name=sampled_top_card_name,
        sampled_top_instance_id=sampled_top_instance_id,
    )

    final_exchangeable = private_search.physical_after.ledger.exchangeable.move(
        action_card_class,
        RESOLVING_TRAINER_ZONE,
        "discard",
    )
    final_ledger = IdentityLedger(
        final_exchangeable,
        private_search.physical_after.ledger.instances,
    )
    final_physical = TopPrizePhysicalState(
        final_ledger,
        private_search.physical_after.top_instance_id,
        private_search.physical_after.prize_instance_ids,
        private_search.physical_after.face_up,
    )
    assert_conserved(physical.ledger, final_physical.ledger)

    after = TrainerSearchExecutionState(
        zones=final_exchangeable,
        budget=execution_state.budget,
        channels=execution_state.channels,
    )
    return ComputerSearchPrivateTransaction(
        before=execution_state,
        after=after,
        physical_before=physical,
        physical_after_cost=after_cost,
        private_search=private_search,
        physical_after=final_physical,
        beliefs_after=private_search.beliefs_after,
        discard_selection=discard_selection,
        target_instance_id=target_instance_id,
    )
