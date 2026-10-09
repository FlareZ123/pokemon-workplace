"""Continue public random-hand discards while retaining uncertain Prize origin."""

from __future__ import annotations

from collections import Counter, defaultdict
from math import isclose
from collections.abc import Mapping

from identity_materialization import assert_conserved, move_instance
from prize_acquired_random_discard import (
    DiscardWorld,
    ObserverRandomHandDiscardBeliefs,
    RandomHandDiscardBelief,
    RandomHandDiscardOutcome,
)
from prize_position_belief import PrizeGroup
from top_prize_physical_bridge import TopPrizePhysicalState, actual_joint_groups


def continue_random_hand_discard(
    before: RandomHandDiscardOutcome,
    *,
    actor_id: str,
    discarded_instance_id: str,
    group_by_card_class: Mapping[str, PrizeGroup],
) -> RandomHandDiscardOutcome:
    """Do another uniformly random physical hand discard and update all beliefs.

    The same publicly observed class can have several possible private origins.
    The affected hand owner learns whether the tagged physical copy left.
    Posterior worlds carry the remaining count of other hand cards, so the
    second draw uses the correct *conditional* without-replacement geometry.
    """

    before.beliefs.belief_for(actor_id)
    ledger = before.physical.ledger
    chosen = ledger.instance(discarded_instance_id)
    tagged = ledger.instance(before.tagged_instance_id)
    if chosen.zone != "hand":
        raise ValueError("discarded physical copy must be in hand")
    if tagged.zone not in {"hand", "discard"}:
        raise ValueError("tagged Prize copy left the modeled hand/discard context")
    if any(zone == "hand" for _class, zone, _count in ledger.exchangeable.counts):
        raise ValueError("hand must be fully materialized")
    total_cards = sum(card.zone == "hand" for card in ledger.instances)
    group_order = before.beliefs.beliefs[0][1].groups
    observed_group = group_by_card_class.get(chosen.card_class)
    if observed_group not in group_order:
        raise ValueError("discarded card group must be explicitly modeled")
    chosen_is_tag = chosen.instance_id == before.tagged_instance_id
    observed_index = group_order.index(observed_group)

    next_observers = []
    for observer_id, belief in before.beliefs.beliefs:
        output: dict[DiscardWorld, float] = defaultdict(float)
        evidence = 0.0
        for (top, prizes, tag_group, tagged_in_hand, other), prior in belief.masses:
            hand_size = int(tagged_in_hand) + sum(other)
            if hand_size != total_cards:
                raise ValueError("belief and physical hand sizes disagree")
            if tagged_in_hand and tag_group == observed_group:
                if observer_id != actor_id or chosen_is_tag:
                    world = (top, prizes, tag_group, False, other)
                    mass = prior / hand_size
                    output[world] += mass
                    evidence += mass

            other_copies = other[observed_index]
            if other_copies:
                if observer_id != actor_id or not chosen_is_tag:
                    remaining = list(other)
                    remaining[observed_index] -= 1
                    world = (top, prizes, tag_group, tagged_in_hand, tuple(remaining))
                    mass = prior * other_copies / hand_size
                    output[world] += mass
                    evidence += mass

        if isclose(evidence, 0.0, rel_tol=0.0, abs_tol=1e-15):
            raise ValueError("selected hand observation has zero belief likelihood")
        next_observers.append((
            observer_id,
            RandomHandDiscardBelief(
                belief.groups, belief.face_up,
                tuple(
                    (world, mass / evidence)
                    for world, mass in sorted(output.items(), key=lambda x: repr(x[0]))
                ),
            ),
        ))

    next_ledger = move_instance(ledger, discarded_instance_id, "discard")
    assert_conserved(ledger, next_ledger)
    physical = TopPrizePhysicalState(
        next_ledger,
        before.physical.top_instance_id,
        before.physical.prize_instance_ids,
        before.physical.face_up,
    )
    true_top, true_prizes = actual_joint_groups(physical, group_by_card_class)
    true_tag = group_by_card_class.get(tagged.card_class)
    true_tag_survives = next_ledger.instance(before.tagged_instance_id).zone == "hand"
    true_other = Counter(
        group_by_card_class.get(row.card_class)
        for row in next_ledger.instances
        if row.zone == "hand" and row.instance_id != before.tagged_instance_id
    )
    true_state = (
        true_top, true_prizes, true_tag, true_tag_survives,
        tuple(true_other.get(g, 0) for g in group_order),
    )
    for observer_id, posterior in next_observers:
        if sum(mass for state, mass in posterior.masses if state == true_state) <= 0.0:
            raise AssertionError(
                f"observer {observer_id!r} assigns no probability to physical truth"
            )

    return RandomHandDiscardOutcome(
        physical,
        before.tagged_instance_id,
        discarded_instance_id,
        ObserverRandomHandDiscardBeliefs(tuple(next_observers)),
    )
