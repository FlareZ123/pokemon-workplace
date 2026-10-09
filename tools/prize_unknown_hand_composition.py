"""Observer-relative hidden hand composition tied to a Prize-derived card."""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Mapping
from dataclasses import dataclass
from math import isclose

from identity_materialization import assert_conserved, move_instance
from prize_acquired_hand_reveal import AcquiredPrizeHandState
from prize_acquired_random_discard import (
    DiscardWorld,
    ObserverRandomHandDiscardBeliefs,
    RandomHandDiscardBelief,
    RandomHandDiscardOutcome,
)
from prize_position_belief import PrizeGroup
from top_prize_physical_bridge import TopPrizePhysicalState, actual_joint_groups

HandWorld = tuple[
    PrizeGroup,
    tuple[PrizeGroup, ...],
    PrizeGroup,
    tuple[int, ...],
]


@dataclass(frozen=True)
class LatentHandCompositionBelief:
    groups: tuple[str, ...]
    face_up: tuple[bool, ...]
    masses: tuple[tuple[HandWorld, float], ...]

    def __post_init__(self) -> None:
        if not self.masses:
            raise ValueError("hand composition belief cannot be empty")
        total = 0.0
        for (top, prizes, tag, others), probability in self.masses:
            if len(prizes) != len(self.face_up) or len(others) != len(self.groups):
                raise ValueError("hidden topology dimensions differ")
            if any(n < 0 for n in others):
                raise ValueError("negative other hand group count")
            if any(
                group is not None and group not in self.groups
                for group in (top, tag, *prizes)
            ):
                raise ValueError("unknown card group in hidden belief")
            if probability < 0.0:
                raise ValueError("negative probability")
            total += probability
        if not isclose(total, 1.0, abs_tol=1e-12, rel_tol=0.0):
            raise ValueError("hidden hand probability mass must total one")


@dataclass(frozen=True)
class ObserverLatentHandCompositionBeliefs:
    beliefs: tuple[tuple[str, LatentHandCompositionBelief], ...]

    def belief_for(self, observer_id: str) -> LatentHandCompositionBelief:
        for current, belief in self.beliefs:
            if current == observer_id:
                return belief
        raise KeyError(observer_id)


def expand_private_prize_hand_composition(
    before: AcquiredPrizeHandState,
    *,
    conditional_other_counts: Mapping[
        str,
        Mapping[PrizeGroup, Mapping[tuple[int, ...], float]],
    ],
) -> ObserverLatentHandCompositionBeliefs:
    """Extend private Prize-origin belief by an observer-specific hand hypothesis.

    Each observer supplies P(other-hand counts | tagged Prize group).
    Correlation with top/remaining Prizes is preserved through that tag group.
    """

    result = []
    for observer_id, belief in before.beliefs.beliefs:
        by_tag = conditional_other_counts[observer_id]
        expanded: dict[HandWorld, float] = defaultdict(float)
        for (top, prizes, tag), prior in belief.masses:
            possibilities = by_tag[tag]
            if not isclose(
                sum(possibilities.values()), 1.0,
                abs_tol=1e-12, rel_tol=0.0,
            ):
                raise ValueError("conditional hand hypotheses must sum to one")
            for other, conditional in possibilities.items():
                if len(other) != len(belief.groups):
                    raise ValueError("hand hypotheses have wrong group dimensions")
                if conditional < 0.0:
                    raise ValueError("negative conditional hand probability")
                if conditional > 0.0:
                    expanded[(top, prizes, tag, other)] += prior * conditional
        result.append((
            observer_id,
            LatentHandCompositionBelief(
                belief.groups, belief.face_up,
                tuple(sorted(expanded.items(), key=lambda row: repr(row[0]))),
            ),
        ))
    return ObserverLatentHandCompositionBeliefs(tuple(result))


def publicly_discard_unknown_other_hand(
    before: AcquiredPrizeHandState,
    hypotheses: ObserverLatentHandCompositionBeliefs,
    *,
    actor_id: str,
    discarded_instance_id: str,
    group_by_card_class: Mapping[str, PrizeGroup],
) -> RandomHandDiscardOutcome:
    """Resolve one uniform random hand discard with uncertain other-hand cards."""

    hypotheses.belief_for(actor_id)
    ledger = before.transition.after.physical.ledger
    chosen = ledger.instance(discarded_instance_id)
    tag = ledger.instance(before.tagged_instance_id)
    if chosen.zone != "hand" or tag.zone != "hand":
        raise ValueError("discarded and tagged instances must start in hand")
    if any(zone == "hand" for _class, zone, _n in ledger.exchangeable.counts):
        raise ValueError("hand must be physically materialized")
    public_group = group_by_card_class.get(chosen.card_class)
    selected_tag = discarded_instance_id == before.tagged_instance_id
    hand_size = sum(row.zone == "hand" for row in ledger.instances)
    result = []

    for observer_id, belief in hypotheses.beliefs:
        if public_group not in belief.groups:
            raise ValueError("public card group must be modeled")
        idx = belief.groups.index(public_group)
        updated: dict[DiscardWorld, float] = defaultdict(float)
        evidence = 0.0
        for (top, prizes, hidden_tag, others), prior in belief.masses:
            if sum(others) + 1 != hand_size:
                raise ValueError("hidden hand state conflicts with public hand size")

            if hidden_tag == public_group:
                if observer_id != actor_id or selected_tag:
                    world = (top, prizes, hidden_tag, False, others)
                    weight = prior / hand_size
                    updated[world] += weight
                    evidence += weight

            other_copies = others[idx]
            if other_copies and (observer_id != actor_id or not selected_tag):
                remaining = list(others)
                remaining[idx] -= 1
                world = (top, prizes, hidden_tag, True, tuple(remaining))
                weight = prior * other_copies / hand_size
                updated[world] += weight
                evidence += weight

        if evidence <= 0.0:
            raise ValueError("publicly discarded card is impossible under belief")
        result.append((
            observer_id,
            RandomHandDiscardBelief(
                belief.groups, belief.face_up,
                tuple(
                    (world, weight / evidence)
                    for world, weight in sorted(updated.items(), key=lambda x: repr(x[0]))
                ),
            ),
        ))

    moved = move_instance(ledger, discarded_instance_id, "discard")
    assert_conserved(ledger, moved)
    before_physical = before.transition.after.physical
    physical = TopPrizePhysicalState(
        moved,
        before_physical.top_instance_id,
        before_physical.prize_instance_ids,
        before_physical.face_up,
    )
    true_top, true_prizes = actual_joint_groups(physical, group_by_card_class)
    true_tag = group_by_card_class.get(tag.card_class)
    true_other = Counter(
        group_by_card_class.get(row.card_class)
        for row in moved.instances
        if row.zone == "hand" and row.instance_id != before.tagged_instance_id
    )
    for observer_id, posterior in result:
        true_world = (
            true_top, true_prizes, true_tag, not selected_tag,
            tuple(true_other.get(group, 0) for group in posterior.groups),
        )
        if sum(p for world, p in posterior.masses if world == true_world) <= 0.0:
            raise AssertionError(
                f"observer {observer_id!r} excludes exact materialized truth"
            )
    return RandomHandDiscardOutcome(
        physical, before.tagged_instance_id, discarded_instance_id,
        ObserverRandomHandDiscardBeliefs(tuple(result)),
    )
