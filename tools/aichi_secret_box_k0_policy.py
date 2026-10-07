"""Belief-constrained first Secret Box payment in the Aichi Vileplume model.

This audit isolates clean states where Secret Box is already in hand and no
other represented full-deck inspection is available before it. The payment is
chosen from K0-observable state. After Secret Box resolves its search, the
existing exact-deck recursion is reused because the player has inspected the
deck and can infer Prize composition.

The outer opening/draw distribution is Monte Carlo. Hidden Prize allocation for
each compressed observation is integrated exactly with multivariate
hypergeometric weights.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
from math import comb, sqrt
import random

from aichi_vileplume_als import BASICS
from aichi_vileplume_secret_box import (
    DECK_INDEX,
    DECK_NAMES,
    HAND_INDEX,
    SECRET_BOX_DECK,
    _compress_deck,
    _compress_hand,
    _core_possible,
    _discard_selections,
)


@dataclass(frozen=True)
class CleanBoxObservation:
    hand: tuple[int, ...]
    unknown_pool: tuple[int, ...]
    bunnelby_in_play: bool


@dataclass(frozen=True)
class ObservationValue:
    hidden_denominator: int
    oracle_success_weight: int
    k0_success_weight: int
    discard_selections: int

    @property
    def oracle_success(self) -> float:
        return self.oracle_success_weight / self.hidden_denominator

    @property
    def k0_success(self) -> float:
        return self.k0_success_weight / self.hidden_denominator

    @property
    def information_gap(self) -> float:
        return (
            self.oracle_success_weight - self.k0_success_weight
        ) / self.hidden_denominator


@dataclass(frozen=True)
class CleanBoxAuditResult:
    trials: int
    qualifying_states: int
    unique_observations: int
    positive_gap_states: int
    positive_gap_observations: int
    hidden_denominator: int
    oracle_success_weight: int
    k0_success_weight: int
    sum_gap_square: float

    @property
    def qualifying_rate(self) -> float:
        return self.qualifying_states / self.trials

    @property
    def oracle_conditional_success(self) -> float:
        if self.qualifying_states == 0:
            return 0.0
        return self.oracle_success_weight / (
            self.qualifying_states * self.hidden_denominator
        )

    @property
    def k0_conditional_success(self) -> float:
        if self.qualifying_states == 0:
            return 0.0
        return self.k0_success_weight / (
            self.qualifying_states * self.hidden_denominator
        )

    @property
    def conditional_gap(self) -> float:
        return self.oracle_conditional_success - self.k0_conditional_success

    @property
    def overall_gap(self) -> float:
        return (
            self.oracle_success_weight - self.k0_success_weight
        ) / (self.trials * self.hidden_denominator)

    @property
    def overall_gap_half_width_95(self) -> float:
        if self.trials <= 1:
            return 0.0
        mean = self.overall_gap
        second_moment = self.sum_gap_square / self.trials
        variance = max(0.0, second_moment - mean * mean)
        standard_error = sqrt(variance / self.trials)
        return 1.96 * standard_error


def _active_for_opening(opening: tuple[str, ...]) -> str:
    basics = [card for card in opening if card in BASICS]
    if not basics:
        raise ValueError("opening must contain a Basic")
    if "Jirachi" in basics:
        return "Jirachi"
    non_bunnelby = [card for card in basics if card != "Bunnelby"]
    return non_bunnelby[0] if non_bunnelby else "Bunnelby"


def _decrement(counter: Counter[str], card: str) -> None:
    counter[card] -= 1
    if counter[card] == 0:
        del counter[card]


def _clean_box_observation(
    opening: tuple[str, ...],
    draw: str,
) -> CleanBoxObservation | None:
    active = _active_for_opening(opening)
    if active in {"Jirachi", "Fan Rotom"}:
        return None

    hand = Counter(opening + (draw,))
    _decrement(hand, active)

    if hand["Secret Box"] == 0:
        return None

    # These represented actions can inspect the full deck before Secret Box.
    # Excluding them isolates a clean first-search payment boundary.
    if any(
        hand[card] > 0
        for card in ("Tag Call", "Guzma & Hala", "Artazon", "Fan Rotom")
    ):
        return None

    bunnelby_in_play = active == "Bunnelby"
    if not bunnelby_in_play and hand["Bunnelby"] > 0:
        _decrement(hand, "Bunnelby")
        bunnelby_in_play = True

    compressed_hand = _compress_hand(hand.elements())
    if (
        bunnelby_in_play
        and compressed_hand[HAND_INDEX["tm_evolution"]] > 0
        and compressed_hand[HAND_INDEX["jet_energy"]] > 0
    ):
        # The narrow core is already satisfied without exposing a Box decision.
        return None

    base_hand = list(compressed_hand)
    base_hand[HAND_INDEX["secret_box"]] -= 1
    if sum(base_hand) < 3:
        return None

    unknown = Counter(SECRET_BOX_DECK)
    for card in opening + (draw,):
        _decrement(unknown, card)

    tracked = _compress_deck(unknown.elements())
    untracked = sum(unknown.values()) - sum(tracked)
    pool = tracked + (untracked,)
    if sum(pool) != 52:
        raise AssertionError(f"unknown pool should contain 52 cards, got {sum(pool)}")

    return CleanBoxObservation(
        hand=compressed_hand,
        unknown_pool=pool,
        bunnelby_in_play=bunnelby_in_play,
    )


@lru_cache(maxsize=None)
def _hidden_deck_worlds(
    unknown_pool: tuple[int, ...],
    prize_count: int = 6,
) -> tuple[tuple[tuple[int, ...], int], ...]:
    """Return exact tracked deck counts and labeled-combination weights."""

    if prize_count < 0 or prize_count > sum(unknown_pool):
        raise ValueError("invalid prize count")

    worlds: list[tuple[tuple[int, ...], int]] = []
    allocation = [0] * len(unknown_pool)

    def visit(index: int, left: int, weight: int) -> None:
        if index == len(unknown_pool):
            if left != 0:
                return
            deck = tuple(
                unknown_pool[i] - allocation[i]
                for i in range(len(DECK_NAMES))
            )
            worlds.append((deck, weight))
            return

        remaining_capacity = sum(unknown_pool[index + 1 :])
        lower = max(0, left - remaining_capacity)
        upper = min(unknown_pool[index], left)
        for prized in range(lower, upper + 1):
            allocation[index] = prized
            visit(
                index + 1,
                left - prized,
                weight * comb(unknown_pool[index], prized),
            )
        allocation[index] = 0

    visit(0, prize_count, 1)

    denominator = comb(sum(unknown_pool), prize_count)
    if sum(weight for _deck, weight in worlds) != denominator:
        raise AssertionError("hidden Prize weights do not sum to denominator")
    return tuple(worlds)


def _post_box_success(
    observation: CleanBoxObservation,
    deck: tuple[int, ...],
    selection: tuple[int, ...],
) -> bool:
    """Pay Box with one fixed visible-hand choice, then grant K1 after search."""

    next_hand = list(observation.hand)
    next_hand[HAND_INDEX["secret_box"]] -= 1
    for index, discarded in enumerate(selection):
        next_hand[index] -= discarded
        if next_hand[index] < 0:
            raise AssertionError("discard selection exceeds visible hand")

    next_deck = list(deck)

    if next_deck[DECK_INDEX["tag_call"]] > 0:
        next_deck[DECK_INDEX["tag_call"]] -= 1
        next_hand[HAND_INDEX["tag_call"]] += 1

    if (
        next_hand[HAND_INDEX["tm_evolution"]] == 0
        and next_deck[DECK_INDEX["tm_evolution"]] > 0
    ):
        next_deck[DECK_INDEX["tm_evolution"]] -= 1
        next_hand[HAND_INDEX["tm_evolution"]] += 1
    elif next_deck[DECK_INDEX["tool_other"]] > 0:
        next_deck[DECK_INDEX["tool_other"]] -= 1
        next_hand[HAND_INDEX["other"]] += 1
    elif next_deck[DECK_INDEX["tm_evolution"]] > 0:
        next_deck[DECK_INDEX["tm_evolution"]] -= 1
        next_hand[HAND_INDEX["tm_evolution"]] += 1

    if (
        next_hand[HAND_INDEX["gnh"]] == 0
        and next_deck[DECK_INDEX["gnh"]] > 0
    ):
        next_deck[DECK_INDEX["gnh"]] -= 1
        next_hand[HAND_INDEX["gnh"]] += 1
    elif next_deck[DECK_INDEX["supporter_other"]] > 0:
        next_deck[DECK_INDEX["supporter_other"]] -= 1
        next_hand[HAND_INDEX["other"]] += 1
    elif next_deck[DECK_INDEX["tag_team_other"]] > 0:
        next_deck[DECK_INDEX["tag_team_other"]] -= 1
        next_hand[HAND_INDEX["other"]] += 1
    elif next_deck[DECK_INDEX["gnh"]] > 0:
        next_deck[DECK_INDEX["gnh"]] -= 1
        next_hand[HAND_INDEX["gnh"]] += 1

    if next_deck[DECK_INDEX["artazon"]] > 0:
        next_deck[DECK_INDEX["artazon"]] -= 1
        next_hand[HAND_INDEX["artazon"]] += 1

    return _core_possible(
        (
            tuple(next_hand),
            tuple(next_deck),
            False,
            False,
            False,
            observation.bunnelby_in_play,
            False,
        )
    )


@lru_cache(maxsize=None)
def value_observation(observation: CleanBoxObservation) -> ObservationValue:
    base_hand = list(observation.hand)
    base_hand[HAND_INDEX["secret_box"]] -= 1
    selections = tuple(_discard_selections(tuple(base_hand), 3))
    if not selections:
        raise AssertionError("qualifying Box observation lacks a payment")

    selection_success = [0] * len(selections)
    oracle_success = 0
    worlds = _hidden_deck_worlds(observation.unknown_pool)
    denominator = comb(sum(observation.unknown_pool), 6)

    for deck, weight in worlds:
        any_success = False
        for index, selection in enumerate(selections):
            if _post_box_success(observation, deck, selection):
                selection_success[index] += weight
                any_success = True
        if any_success:
            oracle_success += weight

    return ObservationValue(
        hidden_denominator=denominator,
        oracle_success_weight=oracle_success,
        k0_success_weight=max(selection_success),
        discard_selections=len(selections),
    )


def simulate_clean_box_audit(
    trials: int,
    *,
    seed: int = 20261007,
) -> CleanBoxAuditResult:
    """Sample accepted visible states and integrate hidden Prize truth exactly."""

    if trials <= 0:
        raise ValueError("trials must be positive")

    rng = random.Random(seed)
    observations: Counter[CleanBoxObservation] = Counter()

    for _ in range(trials):
        while True:
            indices = rng.sample(range(60), 8)
            opening = tuple(SECRET_BOX_DECK[index] for index in indices[:7])
            if any(card in BASICS for card in opening):
                break
        draw = SECRET_BOX_DECK[indices[7]]
        observation = _clean_box_observation(opening, draw)
        if observation is not None:
            observations[observation] += 1

    denominator = comb(52, 6)
    oracle_total = 0
    k0_total = 0
    positive_gap_states = 0
    positive_gap_observations = 0
    sum_gap_square = 0.0

    for observation, frequency in observations.items():
        value = value_observation(observation)
        if value.hidden_denominator != denominator:
            raise AssertionError("unexpected hidden-state denominator")
        oracle_total += frequency * value.oracle_success_weight
        k0_total += frequency * value.k0_success_weight

        gap = value.information_gap
        if gap > 0.0:
            positive_gap_states += frequency
            positive_gap_observations += 1
        sum_gap_square += frequency * gap * gap

    qualifying = sum(observations.values())
    return CleanBoxAuditResult(
        trials=trials,
        qualifying_states=qualifying,
        unique_observations=len(observations),
        positive_gap_states=positive_gap_states,
        positive_gap_observations=positive_gap_observations,
        hidden_denominator=denominator,
        oracle_success_weight=oracle_total,
        k0_success_weight=k0_total,
        sum_gap_square=sum_gap_square,
    )


def main() -> None:
    result = simulate_clean_box_audit(50_000)
    print(f"trials={result.trials}")
    print(f"qualifying={result.qualifying_states} ({result.qualifying_rate:.6%})")
    print(f"unique_observations={result.unique_observations}")
    print(f"positive_gap_states={result.positive_gap_states}")
    print(f"positive_gap_observations={result.positive_gap_observations}")
    print(f"oracle_conditional={result.oracle_conditional_success:.9%}")
    print(f"k0_conditional={result.k0_conditional_success:.9%}")
    print(f"conditional_gap_pp={result.conditional_gap * 100:.9f}")
    print(f"overall_gap_pp={result.overall_gap * 100:.9f}")
    print(f"overall_gap_95_half_width_pp={result.overall_gap_half_width_95 * 100:.9f}")


if __name__ == "__main__":
    main()
