"""Physical attached-Energy objects shared by payment and discard semantics."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from energy_action_budget import (
    EnergyRouteProfile,
    EnergyRouteType,
    evaluate_energy_routes,
    unit,
)
from energy_discard_solver import (
    minimum_basic_named_card_subsets,
    minimum_card_subsets_generic,
)


@dataclass(frozen=True)
class AttachedEnergyCard:
    """One physical Energy card with its current provider behavior."""

    key: str
    card_name: str
    units: int
    provided_symbols: frozenset[str]
    basic_energy_name: str | None = None

    def __post_init__(self) -> None:
        if not self.key:
            raise ValueError("key must be non-empty")
        if self.units <= 0:
            raise ValueError("units must be positive")
        if not self.provided_symbols:
            raise ValueError("provided_symbols must be non-empty")

    @property
    def is_basic(self) -> bool:
        return self.basic_energy_name is not None

    def matches_basic_named(self, energy_type: str) -> bool:
        return self.basic_energy_name == energy_type


def _route_units(
    cards: Sequence[AttachedEnergyCard],
):
    return tuple(
        unit(*card.provided_symbols)
        for card in cards
        for _ in range(card.units)
    )


def attack_ready(
    attack_cost: Sequence[str],
    cards: Sequence[AttachedEnergyCard],
    *,
    reductions: Iterable[tuple[str, int]] = (),
    target_tags: Iterable[str] = (),
) -> bool:
    """Evaluate attack payment from physical attached-card objects."""

    route = EnergyRouteType(
        "attached physical Energy cards",
        1,
        (
            EnergyRouteProfile(
                units=_route_units(cards),
                reductions=tuple(reductions),
            ),
        ),
    )
    return evaluate_energy_routes(
        attack_cost,
        {},
        target_tags,
        (route,),
    ).exact_feasible


def _solver_cards(
    cards: Sequence[AttachedEnergyCard],
) -> list[dict[str, object]]:
    return [
        {
            "name": card.card_name,
            "units": card.units,
            "basic": card.is_basic,
            "basic_energy_name": card.basic_energy_name,
        }
        for card in cards
    ]


def _outcomes(
    cards: Sequence[AttachedEnergyCard],
    subsets: Sequence[Sequence[int]],
) -> tuple[tuple[AttachedEnergyCard, ...], ...]:
    outcomes = []
    for subset in subsets:
        removed = set(subset)
        outcomes.append(
            tuple(card for index, card in enumerate(cards) if index not in removed)
        )
    return tuple(outcomes)


def minimum_generic_discard_outcomes(
    cards: Sequence[AttachedEnergyCard],
    required_units: int,
) -> dict[str, object]:
    """Minimize physical cards while maximizing a generic Energy-unit discard."""

    result = minimum_card_subsets_generic(
        _solver_cards(cards),
        required_units,
    )
    return {
        **result,
        "remaining_states": _outcomes(cards, result["subsets"]),
    }


def minimum_basic_named_discard_outcomes(
    cards: Sequence[AttachedEnergyCard],
    energy_type: str,
    required_cards: int,
) -> dict[str, object]:
    """Solve a Basic <type> Energy physical-card requirement."""

    result = minimum_basic_named_card_subsets(
        _solver_cards(cards),
        energy_type,
        required_cards,
    )
    return {
        **result,
        "remaining_states": _outcomes(cards, result["subsets"]),
    }


def discard_all_basic_named(
    cards: Sequence[AttachedEnergyCard],
    energy_type: str,
) -> tuple[AttachedEnergyCard, ...]:
    """Discard every physical card named Basic <type> Energy."""

    return tuple(
        card
        for card in cards
        if not card.matches_basic_named(energy_type)
    )
