"""Exact posterior over both K1 search-policy hypotheses and hidden Prize worlds.

A public target is selected after the searcher sees a full deck. An observer
who does not know the searcher's target-choice policy must retain a joint
distribution over both policy identity and hidden card configuration.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import permutations
from typing import Callable, Sequence

from revealed_print_information import SearchCard


SearchPolicy = Callable[[frozenset[str], frozenset[str]], str | None]


@dataclass(frozen=True)
class PolicyHypothesis:
    name: str
    prior: Fraction
    choose: SearchPolicy


@dataclass(frozen=True)
class PolicySearchWorld:
    policy_name: str
    ordered_prize_ids: tuple[str, ...]
    selected_print_id: str
    selected_name: str
    shuffled_top_print_id: str


@dataclass(frozen=True)
class PolicySearchPosterior:
    """Normalized exact distribution over full policy, Prize and target states."""

    masses: tuple[tuple[PolicySearchWorld, Fraction], ...]

    def __post_init__(self) -> None:
        if not self.masses:
            raise ValueError("posterior requires positive support")
        if any(mass <= 0 for _, mass in self.masses):
            raise ValueError("posterior masses must be positive")
        if sum((mass for _, mass in self.masses), Fraction()) != 1:
            raise ValueError("posterior masses must sum to one")

    def probability(
        self, event: Callable[[PolicySearchWorld], bool]
    ) -> Fraction:
        return sum((
            mass for world, mass in self.masses if event(world)
        ), Fraction())

    def condition(
        self, predicate: Callable[[PolicySearchWorld], bool]
    ) -> "PolicySearchPosterior":
        kept = tuple(
            (world, mass)
            for world, mass in self.masses
            if predicate(world)
        )
        mass = sum((p for _, p in kept), Fraction())
        if mass == 0:
            raise ValueError("observation has zero probability")
        return PolicySearchPosterior(tuple(
            (world, p / mass) for world, p in kept
        ))

    def print_reveal(self, print_id: str) -> "PolicySearchPosterior":
        return self.condition(lambda world: world.selected_print_id == print_id)

    def name_reveal(self, name: str) -> "PolicySearchPosterior":
        return self.condition(lambda world: world.selected_name == name)

    def policy_reveal(self, policy_name: str) -> "PolicySearchPosterior":
        return self.condition(lambda world: world.policy_name == policy_name)


def enumerate_policy_search_worlds(
    cards: Sequence[SearchCard],
    prize_count: int,
    policies: Sequence[PolicyHypothesis],
) -> PolicySearchPosterior:
    """Condition the normalized prior on an executed, revealed search.

    Each hypothesis has a prior weight. Ordered Prize positions are uniform.
    A deterministic hypothesis picks a physically present deck card after
    inspecting the deck; if it abstains, that initial world has no search event.
    On a successful search the top is uniformly drawn from remaining deck.
    """
    known = {card.print_id: card.name for card in cards}
    if len(known) != len(cards):
        raise ValueError("card print IDs must be unique")
    if not 0 <= prize_count < len(cards) - 1:
        raise ValueError("search must leave at least one post-search deck card")
    if not policies or any(not policy.name for policy in policies):
        raise ValueError("nonempty named policy hypotheses required")
    if len({policy.name for policy in policies}) != len(policies):
        raise ValueError("policy names must be unique")
    if any(policy.prior < 0 for policy in policies):
        raise ValueError("policy hypothesis probabilities cannot be negative")
    if sum((policy.prior for policy in policies), Fraction()) != 1:
        raise ValueError("policy priors must sum to one")

    ids = tuple(known)
    placements = tuple(permutations(ids, prize_count))
    initial_mass = Fraction(1, len(placements))
    raw: list[tuple[PolicySearchWorld, Fraction]] = []
    for policy in policies:
        if policy.prior == 0:
            continue
        for prizes in placements:
            prize_ids = frozenset(prizes)
            deck = tuple(card for card in ids if card not in prize_ids)
            selected = policy.choose(prize_ids, frozenset(deck))
            if selected is None:
                continue
            if selected not in deck:
                raise ValueError(
                    f"policy {policy.name} selected a target absent from deck"
                )
            remaining = tuple(card for card in deck if card != selected)
            branch_mass = policy.prior * initial_mass / len(remaining)
            for top in remaining:
                raw.append((
                    PolicySearchWorld(
                        policy.name,
                        prizes,
                        selected,
                        known[selected],
                        top,
                    ),
                    branch_mass,
                ))
    evidence = sum((mass for _, mass in raw), Fraction())
    if evidence == 0:
        raise ValueError("no policy executes a search in any supported world")
    return PolicySearchPosterior(tuple(
        (world, mass / evidence) for world, mass in raw
    ))
