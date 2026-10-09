"""Retain a privately taken Prize in hand for later public random-hand evidence."""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass

from before_hand_prize_executor import (
    BeforeHandResolution,
    resolve_direct_before_hand_trigger,
)
from before_hand_prize_profiles import BeforeHandPrizeProfile
from identity_materialization import assert_conserved
from observer_top_prize_beliefs import ObserverTopPrizeBeliefs
from pending_prize_identity_belief import ObserverPendingPrizeBeliefs
from private_search_latent_target_belief import (
    LatentPrivateTargetJointBelief,
    ObserverLatentPrivateTargetBeliefs,
)
from prize_optional_trigger_signal import condition_on_pending_trigger_decision
from prize_pending_take import PrizePendingTakeState
from prize_position_belief import PrizeGroup
from top_prize_physical_bridge import actual_joint_groups


@dataclass(frozen=True)
class AcquiredPrizeHandState:
    transition: BeforeHandResolution
    tagged_instance_id: str
    beliefs: ObserverLatentPrivateTargetBeliefs

    def project_without_hand_identity(self) -> ObserverTopPrizeBeliefs:
        return self.beliefs.project_hidden_target()


def decline_prize_into_latent_hand(
    pending: PrizePendingTakeState,
    beliefs: ObserverPendingPrizeBeliefs,
    profile: BeforeHandPrizeProfile,
    *,
    actor_id: str,
    group_by_card_class: Mapping[str, PrizeGroup],
    use_probability_by_group: Mapping[PrizeGroup, float],
    during_own_turn: bool,
) -> AcquiredPrizeHandState:
    """Retain the pending group's correlation after it enters private hand."""

    if len(pending.pending) != 1 or not pending.pending[0].was_face_down:
        raise ValueError("requires exactly one face-down pending Prize")
    instance_id = pending.pending[0].instance_id
    true_group = group_by_card_class.get(
        pending.physical.ledger.instance(instance_id).card_class
    )
    conditioned = condition_on_pending_trigger_decision(
        beliefs,
        actor_id=actor_id,
        actor_observed_group=true_group,
        observed_use=False,
        use_probability_by_group=use_probability_by_group,
    )
    physical = resolve_direct_before_hand_trigger(
        pending,
        profile,
        use_trigger=False,
        during_own_turn=during_own_turn,
    )
    assert physical.after.physical.ledger.instance(instance_id).zone == "hand"
    assert_conserved(pending.physical.ledger, physical.after.physical.ledger)
    latent = ObserverLatentPrivateTargetBeliefs(
        tuple(
            (
                observer_id,
                LatentPrivateTargetJointBelief(
                    belief.groups, belief.face_up, belief.masses,
                ),
            )
            for observer_id, belief in conditioned.beliefs
        )
    )
    return AcquiredPrizeHandState(physical, instance_id, latent)


def _update_one_random_reveal(
    belief: LatentPrivateTargetJointBelief,
    *,
    observed_group: PrizeGroup,
    other_hand_counts: Mapping[PrizeGroup, int],
) -> LatentPrivateTargetJointBelief:
    hand_size = 1 + sum(other_hand_counts.values())
    if any(count < 0 for count in other_hand_counts.values()):
        raise ValueError("other-hand counts must be nonnegative")

    weights = []
    evidence = 0.0
    for hidden_state, prior in belief.masses:
        tagged_group = hidden_state[2]
        observed_copies = (
            other_hand_counts.get(observed_group, 0)
            + int(tagged_group == observed_group)
        )
        weight = prior * observed_copies / hand_size
        if weight > 0.0:
            weights.append((hidden_state, weight))
            evidence += weight
    if evidence <= 0.0:
        raise ValueError("observed group is impossible in every hand world")
    return LatentPrivateTargetJointBelief(
        belief.groups,
        belief.face_up,
        tuple((hidden, weight / evidence) for hidden, weight in weights),
    )


def publicly_reveal_random_hand_card(
    state: AcquiredPrizeHandState,
    *,
    observed_instance_id: str,
    group_by_card_class: Mapping[str, PrizeGroup],
    other_hand_counts: Mapping[PrizeGroup, int],
) -> AcquiredPrizeHandState:
    """Condition every observer on one uniformly random, non-removing reveal.

    This snapshot requires all hand copies to be materialized, and the caller's
    known other-hand composition to agree with exact physical hand contents.
    The revealed copy might differ from the Prize-derived copy.
    """

    physical = state.transition.after.physical
    ledger = physical.ledger
    exposed = ledger.instance(observed_instance_id)
    if exposed.zone != "hand":
        raise ValueError("revealed card must be in hand")
    if any(zone == "hand" for _card, zone, _count in ledger.exchangeable.counts):
        raise ValueError("hand contents must be fully materialized")

    other_counts = Counter(
        group_by_card_class.get(row.card_class)
        for row in ledger.instances
        if row.zone == "hand" and row.instance_id != state.tagged_instance_id
    )
    if dict(other_counts) != {
        group: count for group, count in other_hand_counts.items() if count
    }:
        raise ValueError("known other-hand counts differ from physical hand")
    revealed_group = group_by_card_class.get(exposed.card_class)
    new_beliefs = ObserverLatentPrivateTargetBeliefs(
        tuple(
            (
                observer_id,
                _update_one_random_reveal(
                    belief,
                    observed_group=revealed_group,
                    other_hand_counts=other_hand_counts,
                ),
            )
            for observer_id, belief in state.beliefs.beliefs
        )
    )
    true_top, true_prizes = actual_joint_groups(
        physical, group_by_card_class,
    )
    tagged_group = group_by_card_class.get(
        ledger.instance(state.tagged_instance_id).card_class,
    )
    for observer_id, belief in new_beliefs.beliefs:
        truth = sum(
            p for (top, prizes, tag), p in belief.masses
            if top == true_top and prizes == true_prizes and tag == tagged_group
        )
        if truth <= 0.0:
            raise AssertionError(
                f"observer {observer_id!r} excludes physical truth"
            )
    return AcquiredPrizeHandState(
        state.transition, state.tagged_instance_id, new_beliefs,
    )
