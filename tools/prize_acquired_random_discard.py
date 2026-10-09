"""Public random hand discard with latent Prize-origin identity conservation."""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Mapping
from dataclasses import dataclass
from math import isclose

from identity_materialization import assert_conserved, move_instance
from prize_acquired_hand_reveal import AcquiredPrizeHandState
from prize_position_belief import PrizeGroup
from top_prize_physical_bridge import (
    TopPrizePhysicalState,
    actual_joint_groups,
)

DiscardWorld = tuple[
    PrizeGroup,
    tuple[PrizeGroup, ...],
    PrizeGroup,
    bool,
    tuple[int, ...],
]


@dataclass(frozen=True)
class RandomHandDiscardBelief:
    groups: tuple[str, ...]
    face_up: tuple[bool, ...]
    masses: tuple[tuple[DiscardWorld, float], ...]

    def __post_init__(self) -> None:
        if not self.masses:
            raise ValueError("empty random discard belief")
        total = 0.0
        for (top, prizes, tagged, surviving, others), mass in self.masses:
            if len(prizes) != len(self.face_up):
                raise ValueError("Prize geometry mismatch")
            if len(others) != len(self.groups):
                raise ValueError("other-hand group counts length mismatch")
            if any(count < 0 for count in others):
                raise ValueError("negative other-hand group count")
            if not isinstance(surviving, bool):
                raise ValueError("tag survival must be boolean")
            if any(g is not None and g not in self.groups for g in (top, tagged, *prizes)):
                raise ValueError("unmodeled group")
            if mass < 0.0:
                raise ValueError("negative probability mass")
            total += mass
        if not isclose(total, 1.0, abs_tol=1e-12, rel_tol=0.0):
            raise ValueError("random discard masses must sum to one")

    def top_probability(self, group: PrizeGroup) -> float:
        return sum(p for (top, *_), p in self.masses if top == group)

    def tagged_probability(self, group: PrizeGroup) -> float:
        return sum(p for (_top, _prizes, tag, _survives, _other), p in self.masses if tag == group)

    def tagged_survival_probability(self) -> float:
        return sum(p for (_top, _prizes, _tag, survives, _other), p in self.masses if survives)


@dataclass(frozen=True)
class ObserverRandomHandDiscardBeliefs:
    beliefs: tuple[tuple[str, RandomHandDiscardBelief], ...]

    def belief_for(self, observer_id: str) -> RandomHandDiscardBelief:
        for known, belief in self.beliefs:
            if known == observer_id:
                return belief
        raise KeyError(observer_id)


@dataclass(frozen=True)
class RandomHandDiscardOutcome:
    physical: TopPrizePhysicalState
    tagged_instance_id: str
    discarded_instance_id: str
    beliefs: ObserverRandomHandDiscardBeliefs


def publicly_discard_random_hand_card(
    before: AcquiredPrizeHandState,
    *,
    actor_id: str,
    discarded_instance_id: str,
    group_by_card_class: Mapping[str, PrizeGroup],
    other_hand_counts: Mapping[PrizeGroup, int],
) -> RandomHandDiscardOutcome:
    """Condition each observer on the discarded class, and actor on its origin.

    One uniformly sampled hand card is discarded. The affected hand's owner
    knows whether it was the specifically tagged Prize-origin card. Other
    observers see the publicly discarded class but cannot distinguish copies
    of the same class by their former origin.
    """

    before.beliefs.belief_for(actor_id)
    original = before.transition.after.physical
    ledger = original.ledger
    tagged = ledger.instance(before.tagged_instance_id)
    discarded = ledger.instance(discarded_instance_id)
    if tagged.zone != "hand" or discarded.zone != "hand":
        raise ValueError("both tagged and discarded cards must be in hand")
    if any(zone == "hand" for _card, zone, _count in ledger.exchangeable.counts):
        raise ValueError("requires all hand copies to be materialized")

    group_order = before.beliefs.beliefs[0][1].groups
    if any(group not in group_order or count < 0 for group, count in other_hand_counts.items()):
        raise ValueError("unrecognized group or negative other-hand count")
    actual_others = Counter(
        group_by_card_class.get(card.card_class)
        for card in ledger.instances
        if card.zone == "hand" and card.instance_id != before.tagged_instance_id
    )
    if dict(actual_others) != {group: count for group, count in other_hand_counts.items() if count}:
        raise ValueError("other-hand count assumptions disagree with material hand")

    other_counts = tuple(other_hand_counts.get(g, 0) for g in group_order)
    observed_group = group_by_card_class.get(discarded.card_class)
    actual_tag_discard = discarded_instance_id == before.tagged_instance_id
    hand_size = 1 + sum(other_counts)
    next_observers = []

    for observer_id, belief in before.beliefs.beliefs:
        accumulator: dict[DiscardWorld, float] = defaultdict(float)
        evidence = 0.0
        for (top, prizes, tag), probability in belief.masses:
            if observed_group == tag and (observer_id != actor_id or actual_tag_discard):
                world = (top, prizes, tag, False, other_counts)
                weight = probability / hand_size
                accumulator[world] += weight
                evidence += weight

            other_index = group_order.index(observed_group)
            count = other_counts[other_index]
            if count and (observer_id != actor_id or not actual_tag_discard):
                updated = list(other_counts)
                updated[other_index] -= 1
                world = (top, prizes, tag, True, tuple(updated))
                weight = probability * count / hand_size
                accumulator[world] += weight
                evidence += weight

        if evidence <= 0.0:
            raise ValueError("random discard is impossible under observer belief")
        next_observers.append((
            observer_id,
            RandomHandDiscardBelief(
                belief.groups, belief.face_up,
                tuple(
                    (world, mass / evidence)
                    for world, mass in sorted(accumulator.items(), key=lambda x: repr(x[0]))
                ),
            ),
        ))

    moved = move_instance(ledger, discarded_instance_id, "discard")
    assert_conserved(ledger, moved)
    after = TopPrizePhysicalState(
        moved, original.top_instance_id,
        original.prize_instance_ids, original.face_up,
    )
    top_truth, prize_truth = actual_joint_groups(after, group_by_card_class)
    tag_truth = group_by_card_class.get(tagged.card_class)
    tag_survives = not actual_tag_discard
    true_others = Counter(
        group_by_card_class.get(card.card_class)
        for card in moved.instances
        if card.zone == "hand" and card.instance_id != before.tagged_instance_id
    )
    other_truth = tuple(true_others.get(g, 0) for g in group_order)
    exact_world = (top_truth, prize_truth, tag_truth, tag_survives, other_truth)
    for observer_id, belief in next_observers:
        if sum(p for world, p in belief.masses if world == exact_world) <= 0.0:
            raise AssertionError(f"observer {observer_id!r} excludes exact physical truth")
    return RandomHandDiscardOutcome(
        after, before.tagged_instance_id, discarded_instance_id,
        ObserverRandomHandDiscardBeliefs(tuple(next_observers)),
    )
