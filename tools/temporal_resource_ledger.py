"""Exact staged hand-resource ledger with provenance-aware discard witnesses.

The ledger is deliberately small. It models a sequence of actions that:

- consume named cards from hand;
- pay exact discard costs from the post-consumption hand;
- generate named cards into hand after the cost is paid.

Copies remain exchangeable within (card class, provenance) buckets. Provenance
tracks whether a discarded card came from the initial hand or from an earlier
action. A final hand requirement can make an early payload expendable when a
later action is able to reacquire it.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Mapping, Sequence


INITIAL_ORIGIN = "initial"
HAND_ZONE = "hand"
DISCARD_ZONE = "discard"
CONSUMED_ZONE = "consumed"


@dataclass(frozen=True)
class ResourceLedgerState:
    """Sparse immutable counts keyed by (card_class, origin, zone)."""

    counts: tuple[tuple[str, str, str, int], ...] = ()

    def __post_init__(self) -> None:
        seen: set[tuple[str, str, str]] = set()
        for card_class, origin, zone, count in self.counts:
            if not card_class or not origin or not zone:
                raise ValueError("card_class, origin, and zone must be non-empty")
            if count <= 0:
                raise ValueError("sparse counts must be positive")
            key = (card_class, origin, zone)
            if key in seen:
                raise ValueError(f"duplicate ledger key: {key!r}")
            seen.add(key)
        if self.counts != tuple(sorted(self.counts)):
            raise ValueError("ledger counts must use canonical sorted order")

    @classmethod
    def from_mapping(
        cls,
        counts: Mapping[tuple[str, str, str], int],
    ) -> "ResourceLedgerState":
        return cls(
            tuple(
                sorted(
                    (card_class, origin, zone, count)
                    for (card_class, origin, zone), count in counts.items()
                    if count > 0
                )
            )
        )

    @classmethod
    def initial_hand(cls, cards: Sequence[str]) -> "ResourceLedgerState":
        counts: dict[tuple[str, str, str], int] = {}
        for card_class in cards:
            key = (card_class, INITIAL_ORIGIN, HAND_ZONE)
            counts[key] = counts.get(key, 0) + 1
        return cls.from_mapping(counts)

    def count(
        self,
        card_class: str,
        zone: str,
        *,
        origin: str | None = None,
    ) -> int:
        return sum(
            count
            for current_class, current_origin, current_zone, count in self.counts
            if current_class == card_class
            and current_zone == zone
            and (origin is None or current_origin == origin)
        )

    def origin_count(self, origin: str, zone: str) -> int:
        return sum(
            count
            for _card_class, current_origin, current_zone, count in self.counts
            if current_origin == origin and current_zone == zone
        )

    def move(
        self,
        card_class: str,
        origin: str,
        source_zone: str,
        destination_zone: str,
        *,
        amount: int = 1,
    ) -> "ResourceLedgerState":
        if amount <= 0:
            raise ValueError("amount must be positive")
        if source_zone == destination_zone:
            return self
        available = self.count(card_class, source_zone, origin=origin)
        if available < amount:
            raise ValueError(
                f"cannot move {amount} {card_class!r} from {source_zone!r} "
                f"with origin {origin!r}; only {available} available"
            )

        counts = {
            (current_class, current_origin, zone): count
            for current_class, current_origin, zone, count in self.counts
        }
        source = (card_class, origin, source_zone)
        destination = (card_class, origin, destination_zone)
        remaining = available - amount
        if remaining:
            counts[source] = remaining
        else:
            counts.pop(source)
        counts[destination] = counts.get(destination, 0) + amount
        return ResourceLedgerState.from_mapping(counts)

    def add(
        self,
        card_class: str,
        origin: str,
        zone: str = HAND_ZONE,
        *,
        amount: int = 1,
    ) -> "ResourceLedgerState":
        if amount <= 0:
            raise ValueError("amount must be positive")
        counts = {
            (current_class, current_origin, current_zone): count
            for current_class, current_origin, current_zone, count in self.counts
        }
        key = (card_class, origin, zone)
        counts[key] = counts.get(key, 0) + amount
        return ResourceLedgerState.from_mapping(counts)


@dataclass(frozen=True)
class TemporalAction:
    name: str
    consumes: tuple[str, ...] = ()
    discard_cost: int = 0
    generates: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("action name must be non-empty")
        if self.discard_cost < 0:
            raise ValueError("discard_cost must be non-negative")
        if any(not card for card in self.consumes + self.generates):
            raise ValueError("card classes must be non-empty")


@dataclass(frozen=True)
class ActionWitness:
    action: str
    consumed: tuple[tuple[str, str, int], ...]
    discarded: tuple[tuple[str, str, int], ...]
    generated: tuple[tuple[str, str, int], ...]

    @property
    def initial_discards(self) -> int:
        return sum(
            count
            for _card_class, origin, count in self.discarded
            if origin == INITIAL_ORIGIN
        )


@dataclass(frozen=True)
class SequenceWitness:
    final_state: ResourceLedgerState
    actions: tuple[ActionWitness, ...]

    @property
    def initial_discards(self) -> int:
        return sum(action.initial_discards for action in self.actions)

    @property
    def total_discards(self) -> int:
        return sum(
            count
            for action in self.actions
            for _card_class, _origin, count in action.discarded
        )


def _hand_buckets(state: ResourceLedgerState) -> tuple[tuple[str, str, int], ...]:
    return tuple(
        (card_class, origin, count)
        for card_class, origin, zone, count in state.counts
        if zone == HAND_ZONE
    )


def _named_consumptions(
    state: ResourceLedgerState,
    names: tuple[str, ...],
) -> tuple[tuple[ResourceLedgerState, tuple[tuple[str, str, int], ...]], ...]:
    """Enumerate exact provenance choices for named one-card consumptions."""

    states: tuple[tuple[ResourceLedgerState, tuple[tuple[str, str, int], ...]], ...] = (
        (state, ()),
    )
    for card_class in names:
        next_states = []
        for current, consumed in states:
            origins = sorted(
                {
                    origin
                    for current_class, origin, zone, count in current.counts
                    if current_class == card_class and zone == HAND_ZONE and count > 0
                }
            )
            for origin in origins:
                moved = current.move(
                    card_class,
                    origin,
                    HAND_ZONE,
                    CONSUMED_ZONE,
                )
                next_states.append(
                    (moved, consumed + ((card_class, origin, 1),))
                )
        states = tuple(next_states)
        if not states:
            return ()
    return states


def _discard_selections(
    state: ResourceLedgerState,
    cost: int,
    forbidden_classes: frozenset[str],
) -> tuple[tuple[tuple[str, str, int], ...], ...]:
    if cost == 0:
        return ((),)

    buckets = tuple(
        (card_class, origin, count)
        for card_class, origin, count in _hand_buckets(state)
        if card_class not in forbidden_classes
    )
    if sum(count for _card_class, _origin, count in buckets) < cost:
        return ()

    selections = []
    for amounts in product(*(range(min(count, cost) + 1) for _, _, count in buckets)):
        if sum(amounts) != cost:
            continue
        selections.append(
            tuple(
                (card_class, origin, amount)
                for (card_class, origin, _count), amount in zip(buckets, amounts)
                if amount
            )
        )
    return tuple(selections)


def apply_action(
    state: ResourceLedgerState,
    action: TemporalAction,
    *,
    step_index: int,
    forbidden_discard_classes: frozenset[str] = frozenset(),
) -> tuple[tuple[ResourceLedgerState, ActionWitness], ...]:
    """Enumerate exact executions of one action from the current hand state."""

    outcomes = []
    for consumed_state, consumed in _named_consumptions(state, action.consumes):
        for selection in _discard_selections(
            consumed_state,
            action.discard_cost,
            forbidden_discard_classes,
        ):
            after = consumed_state
            for card_class, origin, count in selection:
                after = after.move(
                    card_class,
                    origin,
                    HAND_ZONE,
                    DISCARD_ZONE,
                    amount=count,
                )

            generated_origin = f"{step_index}:{action.name}"
            generated_counts: dict[str, int] = {}
            for card_class in action.generates:
                generated_counts[card_class] = generated_counts.get(card_class, 0) + 1
                after = after.add(card_class, generated_origin)

            witness = ActionWitness(
                action=action.name,
                consumed=tuple(sorted(consumed)),
                discarded=tuple(sorted(selection)),
                generated=tuple(
                    sorted(
                        (card_class, generated_origin, count)
                        for card_class, count in generated_counts.items()
                    )
                ),
            )
            outcomes.append((after, witness))
    return tuple(outcomes)


def execute_sequence(
    initial_state: ResourceLedgerState,
    actions: Sequence[TemporalAction],
    *,
    final_hand_requirements: Mapping[str, int] | None = None,
    forbidden_discard_classes: frozenset[str] = frozenset(),
) -> tuple[SequenceWitness, ...]:
    """Enumerate feasible staged executions and retain exact discard provenance."""

    frontier: tuple[SequenceWitness, ...] = (SequenceWitness(initial_state, ()),)
    for step_index, action in enumerate(actions):
        next_frontier = []
        for partial in frontier:
            for after, action_witness in apply_action(
                partial.final_state,
                action,
                step_index=step_index,
                forbidden_discard_classes=forbidden_discard_classes,
            ):
                next_frontier.append(
                    SequenceWitness(
                        final_state=after,
                        actions=partial.actions + (action_witness,),
                    )
                )
        frontier = tuple(next_frontier)
        if not frontier:
            return ()

    requirements = final_hand_requirements or {}
    return tuple(
        witness
        for witness in frontier
        if all(
            witness.final_state.count(card_class, HAND_ZONE) >= required
            for card_class, required in requirements.items()
        )
    )


def best_witness(witnesses: Sequence[SequenceWitness]) -> SequenceWitness | None:
    """Choose a deterministic witness minimizing initial-hand discard consumption."""

    if not witnesses:
        return None
    return min(
        witnesses,
        key=lambda witness: (
            witness.initial_discards,
            witness.total_discards,
            repr(witness.actions),
        ),
    )


def minimum_initial_filler(
    fixed_initial_cards: Sequence[str],
    actions: Sequence[TemporalAction],
    *,
    final_hand_requirements: Mapping[str, int] | None = None,
    filler_class: str = "initial_filler",
    max_fillers: int = 20,
    forbidden_discard_classes: frozenset[str] = frozenset(),
) -> tuple[int, SequenceWitness]:
    """Find the smallest initial filler stock that permits the whole sequence."""

    if max_fillers < 0:
        raise ValueError("max_fillers must be non-negative")
    for count in range(max_fillers + 1):
        state = ResourceLedgerState.initial_hand(
            tuple(fixed_initial_cards) + (filler_class,) * count
        )
        witness = best_witness(
            execute_sequence(
                state,
                actions,
                final_hand_requirements=final_hand_requirements,
                forbidden_discard_classes=forbidden_discard_classes,
            )
        )
        if witness is not None:
            return count, witness
    raise ValueError("sequence is infeasible within max_fillers")
