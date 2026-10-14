"""Observation-consistent first-search decisions across hidden Prize worlds.

The physical search action and discard payment must be selected from public/
player-visible state. A specific target may be chosen after the deck is searched,
when the searching player has learned its contents.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Sequence

from discard_cost_witness import DiscardSelection
from physical_staged_trainer_policy import (
    PhysicalSearchOption,
    _possible_payments,
)
from trainer_search_transaction import (
    TrainerSearchExecutionState,
    execute_trainer_retrieval_transaction,
)


@dataclass(frozen=True)
class K0BeliefWorld:
    state: TrainerSearchExecutionState
    weight: Fraction


@dataclass(frozen=True)
class AcquisitionGoal:
    card_class: str
    copies: int = 1

    def __post_init__(self) -> None:
        if not self.card_class or self.copies <= 0:
            raise ValueError("acquisition goals need a named positive count")


@dataclass(frozen=True)
class K0PhysicalSearchFamily:
    """One pre-search action with several post-search target choices."""

    name: str
    variants: tuple[PhysicalSearchOption, ...]

    def __post_init__(self) -> None:
        if not self.name or not self.variants:
            raise ValueError("search family must be named and nonempty")
        first = self.variants[0]
        stable = (
            first.action_card_class,
            first.profile,
            first.targets,
            first.discard_candidates,
            first.pay_optional_discard,
            first.play_condition_met,
        )
        for variant in self.variants[1:]:
            other = (
                variant.action_card_class,
                variant.profile,
                variant.targets,
                variant.discard_candidates,
                variant.pay_optional_discard,
                variant.play_condition_met,
            )
            if stable != other:
                raise ValueError(
                    "post-search variants must share their played card, "
                    "targets, payment policy, and conditional branch"
                )


@dataclass(frozen=True)
class K0SearchBeliefResult:
    selected_family: str | None
    selected_payment: DiscardSelection | None
    world_retrieval_variants: tuple[str | None, ...]
    world_completed_units: tuple[int, ...]
    expected_utility: Fraction
    oracle_expected_utility: Fraction
    value_of_hidden_information: Fraction


def _visible_signature(state: TrainerSearchExecutionState):
    public = tuple(
        (card_class, zone, count)
        for card_class, zone, count in state.zones.counts
        if zone not in {"deck", "prize"}
    )
    totals = tuple(sorted({
        card_class: state.zones.total(card_class)
        for card_class, _zone, _count in state.zones.counts
    }.items()))
    return public, totals, state.budget, state.channels


def _acquired(state: TrainerSearchExecutionState, goals: tuple[AcquisitionGoal, ...]) -> int:
    return sum(
        min(goal.copies, state.zones.count(goal.card_class, "hand"))
        for goal in goals
    )


def evaluate_k0_physical_search(
    worlds: Sequence[K0BeliefWorld],
    *,
    families: Sequence[K0PhysicalSearchFamily],
    acquisition_goals: Sequence[AcquisitionGoal],
    reward_per_unit: Fraction = Fraction(1),
    penalty_per_discard: Fraction = Fraction(0),
) -> K0SearchBeliefResult:
    """Choose one action/payment for all indistinguishable physical worlds.

    The target choice may vary by world after a permitted deck inspection, but
    the pre-search card and payment selection must be identical. We require a
    legal retrieval variant for every world and do not silently condition the
    chosen action on hidden truth.

    An intentionally clairvoyant comparator may choose an action/payment in
    each world independently. Its utility is only an information upper bound
    within the supplied action family.
    """

    possibilities = tuple(worlds)
    available = tuple(families)
    goals = tuple(acquisition_goals)
    if not possibilities or not goals:
        raise ValueError("worlds and goals must both be nonempty")
    if len({goal.card_class for goal in goals}) != len(goals):
        raise ValueError("repeated acquisition goal classes double-count cards")
    if any(w.weight <= 0 for w in possibilities):
        raise ValueError("world weights must be positive")
    if sum((w.weight for w in possibilities), Fraction()) != 1:
        raise ValueError("world weights must total exactly 1")
    if reward_per_unit < 0 or penalty_per_discard < 0:
        raise ValueError("utility reward and discard penalty must be nonnegative")

    signature = _visible_signature(possibilities[0].state)
    if any(_visible_signature(w.state) != signature for w in possibilities[1:]):
        raise ValueError(
            "belief worlds must agree on observed zones, deck composition, "
            "and live action permissions"
        )

    rewards: list[tuple[Fraction, ...]] = []
    variants: list[tuple[str | None, ...]] = []
    completed: list[tuple[int, ...]] = []
    first_actions: list[tuple[str | None, DiscardSelection | None]] = []

    unchanged = tuple(_acquired(w.state, goals) for w in possibilities)
    rewards.append(tuple(reward_per_unit * n for n in unchanged))
    variants.append((None,) * len(possibilities))
    completed.append(unchanged)
    first_actions.append((None, None))

    for family in available:
        lead = family.variants[0]
        for payment in _possible_payments(possibilities[0].state, lead):
            world_rewards = []
            world_variants = []
            world_completed = []
            for world in possibilities:
                legal_outcomes = []
                for option in family.variants:
                    try:
                        transaction = execute_trainer_retrieval_transaction(
                            world.state,
                            profile=option.profile,
                            action_card_class=option.action_card_class,
                            targets=option.targets,
                            retrieval_action=option.retrieval_action,
                            discard_candidates=option.discard_candidates,
                            discard_selection=payment,
                            pay_optional_discard=option.pay_optional_discard,
                            play_condition_met=option.play_condition_met,
                        )
                    except ValueError:
                        continue
                    count = _acquired(transaction.after, goals)
                    value = (
                        reward_per_unit * count
                        - penalty_per_discard * transaction.discard_cost
                    )
                    legal_outcomes.append((value, count, option.name))
                if not legal_outcomes:
                    break
                # Target choice occurs after inspection, so it may depend on
                # the actual deck contents learned through this search.
                utility, achieved, label = max(legal_outcomes)
                world_rewards.append(utility)
                world_completed.append(achieved)
                world_variants.append(label)

            if len(world_rewards) == len(possibilities):
                rewards.append(tuple(world_rewards))
                variants.append(tuple(world_variants))
                completed.append(tuple(world_completed))
                first_actions.append((family.name, payment))

    def expected(values: tuple[Fraction, ...]) -> Fraction:
        return sum(
            (world.weight * value for world, value in zip(possibilities, values)),
            Fraction(),
        )

    best_index = max(
        range(len(rewards)),
        key=lambda i: (
            expected(rewards[i]),
            -(sum((w.weight for w in possibilities), Fraction())
              if first_actions[i][0] is not None else Fraction()),
        ),
    )
    best_expected = expected(rewards[best_index])
    oracle = sum(
        (
            world.weight * max(candidate[i] for candidate in rewards)
            for i, world in enumerate(possibilities)
        ),
        Fraction(),
    )
    assert oracle >= best_expected
    family, selection = first_actions[best_index]
    return K0SearchBeliefResult(
        selected_family=family,
        selected_payment=selection,
        world_retrieval_variants=variants[best_index],
        world_completed_units=completed[best_index],
        expected_utility=best_expected,
        oracle_expected_utility=oracle,
        value_of_hidden_information=oracle - best_expected,
    )
