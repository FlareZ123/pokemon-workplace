"""Face-down Prize taking with belief updates and reveal timing."""

from __future__ import annotations

from dataclasses import dataclass

from identity_materialization import (
    IdentityLedger,
    assert_conserved,
    dematerialize,
    materialize,
    move_instance,
)
from prize_belief_kernel import PrizeBelief

PRIZE = "prize"
PENDING = "prize_pending"
HAND = "hand"


@dataclass(frozen=True)
class PrizeTakeBeliefBranch:
    observed_group: str | None
    probability: float
    remaining_belief: PrizeBelief


@dataclass(frozen=True)
class PrizeTruthBeliefState:
    ledger: IdentityLedger
    belief: PrizeBelief
    group_by_card_class: tuple[tuple[str, str | None], ...]

    def __post_init__(self) -> None:
        keys = [card_class for card_class, _group in self.group_by_card_class]
        if len(keys) != len(set(keys)):
            raise ValueError("card-class belief-group mappings must be unique")
        if self.group_by_card_class != tuple(
            sorted(self.group_by_card_class, key=lambda row: row[0])
        ):
            raise ValueError("card-class belief-group mappings must be sorted")
        mapping = dict(self.group_by_card_class)
        if any(
            group is not None and group not in self.belief.groups
            for group in mapping.values()
        ):
            raise ValueError("mapped groups must occur in the Prize belief")

        prize_count = sum(
            count
            for _card_class, zone, count in self.ledger.exchangeable.counts
            if zone == PRIZE
        ) + sum(row.zone == PRIZE for row in self.ledger.instances)
        if prize_count != self.belief.prize_count:
            raise ValueError(
                "Prize count and belief prize_count differ: "
                f"ledger={prize_count}, belief={self.belief.prize_count}"
            )

        actual = [0] * len(self.belief.groups)
        prize_classes: list[str] = []
        for card_class, zone, count in self.ledger.exchangeable.counts:
            if zone == PRIZE:
                prize_classes.extend([card_class] * count)
        for row in self.ledger.instances:
            if row.zone == PRIZE:
                prize_classes.append(row.card_class)
        for card_class in prize_classes:
            if card_class not in mapping:
                raise ValueError(
                    f"missing Prize-belief group mapping for {card_class!r}"
                )
            group = mapping[card_class]
            if group is not None:
                actual[self.belief.groups.index(group)] += 1
        actual_state = tuple(actual)
        if not any(
            state == actual_state and mass > 0.0
            for state, mass in self.belief.masses
        ):
            raise ValueError(
                "current Prize composition has zero probability under the belief: "
                f"{actual_state!r}"
            )


@dataclass(frozen=True)
class PrizeTakeEvent:
    instance_id: str
    card_class: str
    card_name: str
    observed_group: str | None
    observation_probability: float


@dataclass(frozen=True)
class PrizeTakeStart:
    state: PrizeTruthBeliefState
    event: PrizeTakeEvent


def _observation_count(
    belief: PrizeBelief,
    state: tuple[int, ...],
    observed_group: str | None,
) -> tuple[int, int | None]:
    if observed_group is None:
        return belief.prize_count - sum(state), None
    try:
        index = belief.groups.index(observed_group)
    except ValueError as error:
        raise ValueError("observed_group must be modeled or None") from error
    return state[index], index


def take_face_down_prize_observation(
    belief: PrizeBelief,
    observed_group: str | None,
) -> tuple[float, PrizeBelief]:
    """Condition on the identity group seen while taking one unknown Prize."""

    if belief.prize_count <= 0:
        raise ValueError("cannot take a Prize when none remain")

    output: dict[tuple[int, ...], float] = {}
    probability = 0.0
    for state, mass in belief.masses:
        count, index = _observation_count(belief, state, observed_group)
        if count <= 0:
            continue
        weight = mass * count / belief.prize_count
        next_state = list(state)
        if index is not None:
            next_state[index] -= 1
        key = tuple(next_state)
        output[key] = output.get(key, 0.0) + weight
        probability += weight

    if probability <= 0.0:
        raise ValueError("observation has zero probability under this belief")

    remaining = PrizeBelief(
        belief.groups,
        belief.prize_count - 1,
        tuple(
            (state, weight / probability)
            for state, weight in sorted(output.items())
        ),
    )
    return probability, remaining


def take_face_down_prize_branches(
    belief: PrizeBelief,
) -> tuple[PrizeTakeBeliefBranch, ...]:
    """Enumerate all possible one-Prize observations and posterior beliefs."""

    if belief.prize_count <= 0:
        return ()

    branches: list[PrizeTakeBeliefBranch] = []
    for observed_group in (*belief.groups, None):
        try:
            probability, remaining = take_face_down_prize_observation(
                belief,
                observed_group,
            )
        except ValueError as error:
            if "zero probability" in str(error):
                continue
            raise
        branches.append(
            PrizeTakeBeliefBranch(
                observed_group,
                probability,
                remaining,
            )
        )

    total = sum(branch.probability for branch in branches)
    if abs(total - 1.0) > 1e-12:
        raise AssertionError(f"Prize-take branch probability changed: {total}")
    return tuple(branches)


def begin_face_down_prize_take(
    state: PrizeTruthBeliefState,
    *,
    card_class: str,
    card_name: str,
    observed_group: str | None,
    instance_id: str,
) -> PrizeTakeStart:
    mapping = dict(state.group_by_card_class)
    if card_class not in mapping:
        raise ValueError("selected Prize card class has no belief-group mapping")
    if mapping[card_class] != observed_group:
        raise ValueError(
            "observed group does not match the selected physical card class"
        )

    probability, remaining_belief = take_face_down_prize_observation(
        state.belief,
        observed_group,
    )
    ledger = materialize(
        state.ledger,
        card_class=card_class,
        card_name=card_name,
        source_zone=PRIZE,
        instance_id=instance_id,
    )
    ledger = move_instance(ledger, instance_id, PENDING)
    next_state = PrizeTruthBeliefState(
        ledger,
        remaining_belief,
        state.group_by_card_class,
    )
    assert_conserved(state.ledger, next_state.ledger)
    return PrizeTakeStart(
        next_state,
        PrizeTakeEvent(
            instance_id=instance_id,
            card_class=card_class,
            card_name=card_name,
            observed_group=observed_group,
            observation_probability=probability,
        ),
    )


def complete_prize_take_to_hand(
    state: PrizeTruthBeliefState,
    instance_id: str,
) -> PrizeTruthBeliefState:
    current = state.ledger.instance(instance_id)
    if current.zone != PENDING:
        raise ValueError("Prize instance is not in the before-hand pending zone")
    ledger = move_instance(state.ledger, instance_id, HAND)
    ledger = dematerialize(ledger, instance_id)
    next_state = PrizeTruthBeliefState(
        ledger,
        state.belief,
        state.group_by_card_class,
    )
    assert_conserved(state.ledger, next_state.ledger)
    return next_state
