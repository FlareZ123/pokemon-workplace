"""K0 versus oracle discard policy for direct Guzma & Hala in Aichi Vileplume."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
from math import comb, sqrt
import random

from aichi_secret_box_k0_policy import _active_for_opening, _decrement
from aichi_vileplume_als import BASICS, DECK

BASICS_BY_ENDPOINT = {
    "core": (),
    "pidgeot": ("Pidgey",),
    "stoutland": ("Lillipup",),
    "dual": ("Pidgey", "Lillipup"),
    "item": ("Oddish",),
    "item_pidgeot": ("Oddish", "Pidgey"),
    "item_stoutland": ("Oddish", "Lillipup"),
}
STAGES_BY_ENDPOINT = {
    "core": (),
    "pidgeot": ("Pidgeotto", "Pidgeot ex"),
    "stoutland": ("Herdier", "Stoutland"),
    "dual": ("Pidgeotto", "Pidgeot ex", "Herdier", "Stoutland"),
    "item": ("Gloom", "Vileplume"),
    "item_pidgeot": ("Gloom", "Vileplume", "Pidgeotto", "Pidgeot ex"),
    "item_stoutland": ("Gloom", "Vileplume", "Herdier", "Stoutland"),
}
ENDPOINTS = tuple(BASICS_BY_ENDPOINT)
BASE_TRACKED = (
    "Technical Machine: Evolution",
    "Jet Energy",
    "Artazon",
    "Fan Rotom",
    "Bunnelby",
)
FAN_TARGETS = ("Bunnelby", "Pidgey", "Lillipup")


@dataclass(frozen=True)
class Observation:
    endpoint: str
    hand: tuple[int, ...]
    unknown_pool: tuple[int, ...]
    active: str


@dataclass(frozen=True)
class EndpointResult:
    endpoint: str
    unique_observations: int
    positive_gap_states: int
    positive_gap_observations: int
    oracle_weight: int
    k0_weight: int
    denominator: int
    qualifying: int
    trials: int
    sum_gap_square: float
    max_gap: float

    @property
    def oracle_conditional(self) -> float:
        return self.oracle_weight / (self.qualifying * self.denominator)

    @property
    def k0_conditional(self) -> float:
        return self.k0_weight / (self.qualifying * self.denominator)

    @property
    def conditional_gap(self) -> float:
        return self.oracle_conditional - self.k0_conditional

    @property
    def overall_gap(self) -> float:
        return (self.oracle_weight - self.k0_weight) / (self.trials * self.denominator)

    @property
    def half_width_95(self) -> float:
        mean = self.overall_gap
        second = self.sum_gap_square / self.trials
        variance = max(0.0, second - mean * mean)
        return 1.96 * sqrt(variance / self.trials)


def _unique(names):
    return tuple(dict.fromkeys(names))


@lru_cache(maxsize=None)
def _tracked(endpoint: str):
    return _unique(BASE_TRACKED + BASICS_BY_ENDPOINT[endpoint] + STAGES_BY_ENDPOINT[endpoint])


@lru_cache(maxsize=None)
def _hand_names(endpoint: str):
    return _unique(
        ("Technical Machine: Evolution", "Jet Energy", "Bunnelby")
        + BASICS_BY_ENDPOINT[endpoint]
    ) + ("other",)


def _visible(opening: tuple[str, ...], draw: str):
    active = _active_for_opening(opening)
    if active in {"Jirachi", "Fan Rotom"}:
        return None
    hand = Counter(opening + (draw,))
    _decrement(hand, active)
    if hand["Guzma & Hala"] == 0:
        return None
    if any(hand[name] > 0 for name in ("Tag Call", "Artazon", "Fan Rotom")):
        return None
    _decrement(hand, "Guzma & Hala")
    return active, hand


def _observation(opening, draw, endpoint, visible):
    active, hand = visible
    names = _hand_names(endpoint)
    direct = names[:-1]
    hand_tuple = tuple(hand[name] for name in direct)
    hand_tuple += (sum(hand.values()) - sum(hand_tuple),)

    unknown = Counter(DECK)
    for card in opening + (draw,):
        _decrement(unknown, card)
    tracked = _tracked(endpoint)
    pool = tuple(unknown[name] for name in tracked)
    pool += (52 - sum(pool),)
    if sum(pool) != 52:
        raise AssertionError("unknown pool must contain 52 cards")
    return Observation(endpoint, hand_tuple, pool, active)


@lru_cache(maxsize=None)
def _worlds(unknown_pool: tuple[int, ...], prize_count: int = 6):
    """Return tracked deck counts and exact labeled Prize weights."""
    allocation = [0] * len(unknown_pool)
    worlds = []

    def visit(index: int, left: int, weight: int):
        if index == len(unknown_pool):
            if left == 0:
                worlds.append((
                    tuple(
                        unknown_pool[i] - allocation[i]
                        for i in range(len(unknown_pool) - 1)
                    ),
                    weight,
                ))
            return
        remaining = sum(unknown_pool[index + 1:])
        lower = max(0, left - remaining)
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
    if sum(weight for _, weight in worlds) != denominator:
        raise AssertionError("hidden Prize weights do not sum to denominator")
    return tuple(worlds)


def _selections(hand: tuple[int, ...], count: int = 2):
    out = []
    chosen = [0] * len(hand)

    def visit(index, left):
        if index == len(hand):
            if left == 0:
                out.append(tuple(chosen))
            return
        for use in range(min(hand[index], left) + 1):
            chosen[index] = use
            visit(index + 1, left - use)
        chosen[index] = 0

    visit(0, count)
    return tuple(out)


def _basic_possible(endpoint, hand, deck, active, artazon):
    needs = Counter(BASICS_BY_ENDPOINT[endpoint])
    needs["Bunnelby"] += 1
    direct = Counter({name: hand[name] for name in needs})
    direct[active] += 1

    actions = [None]
    if artazon:
        for name in _unique(tuple(needs) + ("Fan Rotom",)):
            if deck[name] > 0:
                actions.append(name)

    for fetch in actions:
        have = direct.copy()
        if fetch == "Fan Rotom":
            for name in FAN_TARGETS:
                missing = max(0, needs[name] - have[name])
                if missing and deck[name] >= missing:
                    have[name] += missing
        elif fetch is not None:
            have[fetch] += 1
        if all(have[name] >= count for name, count in needs.items()):
            return True
    return False


def _succeeds(observation: Observation, deck_tuple, selection):
    endpoint = observation.endpoint
    hand_names = _hand_names(endpoint)
    deck_names = _tracked(endpoint)
    hand = Counter(dict(zip(hand_names, observation.hand)))
    deck = Counter(dict(zip(deck_names, deck_tuple)))

    paid = selection is not None
    if paid:
        for name, amount in zip(hand_names, selection):
            hand[name] -= amount
            if hand[name] < 0:
                raise AssertionError("discard exceeds visible hand")

    artazon = deck["Artazon"] > 0
    if artazon:
        deck["Artazon"] -= 1

    if paid:
        for name in ("Technical Machine: Evolution", "Jet Energy"):
            if hand[name] == 0 and deck[name] > 0:
                deck[name] -= 1
                hand[name] += 1

    if hand["Technical Machine: Evolution"] == 0 or hand["Jet Energy"] == 0:
        return False
    if any(deck[name] <= 0 for name in STAGES_BY_ENDPOINT[endpoint]):
        return False
    return _basic_possible(endpoint, hand, deck, observation.active, artazon)


@lru_cache(maxsize=None)
def _value(observation: Observation):
    actions = (None,) + _selections(observation.hand)
    weights = [0] * len(actions)
    oracle = 0
    worlds = _worlds(observation.unknown_pool)
    denominator = comb(52, 6)

    for deck, weight in worlds:
        any_success = False
        for index, action in enumerate(actions):
            if _succeeds(observation, deck, action):
                weights[index] += weight
                any_success = True
        if any_success:
            oracle += weight
    return denominator, oracle, max(weights), len(actions)


def simulate(trials: int = 10_000, seed: int = 20261007):
    rng = random.Random(seed)
    groups = {endpoint: Counter() for endpoint in ENDPOINTS}
    qualifying = 0

    for _ in range(trials):
        while True:
            indices = rng.sample(range(60), 8)
            opening = tuple(DECK[index] for index in indices[:7])
            if any(card in BASICS for card in opening):
                break
        draw = DECK[indices[7]]
        visible = _visible(opening, draw)
        if visible is None:
            continue
        qualifying += 1
        for endpoint in ENDPOINTS:
            groups[endpoint][_observation(opening, draw, endpoint, visible)] += 1

    denominator = comb(52, 6)
    results = []
    for endpoint in ENDPOINTS:
        oracle_total = 0
        k0_total = 0
        positive_states = 0
        positive_observations = 0
        sum_sq = 0.0
        max_gap = 0.0

        for observation, frequency in groups[endpoint].items():
            den, oracle, k0, _actions = _value(observation)
            if den != denominator:
                raise AssertionError("hidden denominator mismatch")
            oracle_total += frequency * oracle
            k0_total += frequency * k0
            gap = (oracle - k0) / denominator
            if gap > 0:
                positive_states += frequency
                positive_observations += 1
                max_gap = max(max_gap, gap)
            sum_sq += frequency * gap * gap

        results.append(EndpointResult(
            endpoint, len(groups[endpoint]), positive_states,
            positive_observations, oracle_total, k0_total, denominator,
            qualifying, trials, sum_sq, max_gap,
        ))
    return qualifying, tuple(results)


def main():
    trials = 10_000
    qualifying, results = simulate(trials)
    print(f"trials={trials}")
    print(f"qualifying={qualifying} ({qualifying / trials:.6%})")
    for result in results:
        print(result.endpoint)
        print(f"  unique_observations={result.unique_observations}")
        print(f"  positive_gap_states={result.positive_gap_states}")
        print(f"  positive_gap_observations={result.positive_gap_observations}")
        print(f"  oracle_conditional={result.oracle_conditional:.9%}")
        print(f"  k0_conditional={result.k0_conditional:.9%}")
        print(f"  conditional_gap_pp={result.conditional_gap * 100:.9f}")
        print(f"  overall_gap_pp={result.overall_gap * 100:.9f}")
        print(f"  half_width_95_pp={result.half_width_95 * 100:.9f}")
        print(f"  max_observation_gap_pp={result.max_gap * 100:.9f}")


if __name__ == "__main__":
    main()
