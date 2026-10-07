"""Exact typed target allocation for compiled Trainer deck-search outputs.

This module supplies a conservative semantic layer between literal search labels
and physical target copies. It gives trusted structural card classes a small
inheritance lattice while keeping orthogonal properties explicit.

The allocator never lets one physical target copy satisfy two distinct demand
units. This is the main safety property missing from a naive label-expansion
scheme.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Sequence

from trainer_search_profile_compiler import SearchOutput


POKEMON = "pokemon"
TRAINER = "trainer"
ENERGY = "energy"

BASIC_POKEMON = "basic_pokemon"
EVOLUTION_POKEMON = "evolution_pokemon"
STAGE_1_POKEMON = "stage_1_pokemon"
STAGE_2_POKEMON = "stage_2_pokemon"

ITEM = "item"
POKEMON_TOOL = "pokemon_tool"
SUPPORTER = "supporter"
STADIUM = "stadium"

BASIC_ENERGY = "basic_energy"
SPECIAL_ENERGY = "special_energy"

TYPE_PREFIX = "type:"
TEAM_PREFIX = "team:"


_PARENT_TAGS = {
    BASIC_POKEMON: (POKEMON,),
    EVOLUTION_POKEMON: (POKEMON,),
    STAGE_1_POKEMON: (EVOLUTION_POKEMON,),
    STAGE_2_POKEMON: (EVOLUTION_POKEMON,),
    ITEM: (TRAINER,),
    POKEMON_TOOL: (TRAINER,),
    SUPPORTER: (TRAINER,),
    STADIUM: (TRAINER,),
    BASIC_ENERGY: (ENERGY,),
    SPECIAL_ENERGY: (ENERGY,),
}

_TRAINER_SUBTYPES = frozenset(
    {ITEM, POKEMON_TOOL, SUPPORTER, STADIUM}
)
_POKEMON_STAGES = frozenset(
    {BASIC_POKEMON, STAGE_1_POKEMON, STAGE_2_POKEMON}
)
_ENERGY_CLASSES = frozenset(
    {BASIC_ENERGY, SPECIAL_ENERGY}
)
_SUPERTYPES = frozenset(
    {POKEMON, TRAINER, ENERGY}
)

_TYPE_NAMES = frozenset(
    {
        "grass",
        "fire",
        "water",
        "lightning",
        "psychic",
        "fighting",
        "darkness",
        "metal",
        "fairy",
        "colorless",
        "dragon",
    }
)


class UnsupportedSearchSelector(ValueError):
    """Raised when a literal label needs semantics outside this lattice."""


@dataclass(frozen=True)
class SearchSelector:
    label: str
    required_tags: frozenset[str]

    def matches(self, target: "TargetGroup") -> bool:
        return self.required_tags <= target.tags


@dataclass(frozen=True)
class TargetGroup:
    """Copies of one physical target class with trusted semantic tags."""

    name: str
    copies: int
    tags: frozenset[str]

    def __post_init__(self) -> None:
        if self.copies < 0:
            raise ValueError("copies must be non-negative")
        closed = close_tags(self.tags)
        validate_closed_tags(closed)
        object.__setattr__(self, "tags", closed)


@dataclass(frozen=True)
class DemandChannel:
    """One strategic resource class and the number of distinct cards needed."""

    name: str
    copies: int
    selector: SearchSelector

    def __post_init__(self) -> None:
        if self.copies < 0:
            raise ValueError("copies must be non-negative")


@dataclass(frozen=True)
class TypedTargetAllocation:
    """Useful output vectors obtainable from the represented physical targets."""

    profiles: tuple[tuple[int, ...], ...]
    full_demand_feasible: bool
    minimum_unmet_units: int


def close_tags(tags: frozenset[str] | set[str]) -> frozenset[str]:
    """Return transitive structural supertypes for a trusted tag set."""

    closed = set(tags)
    changed = True
    while changed:
        changed = False
        for tag in tuple(closed):
            for parent in _PARENT_TAGS.get(tag, ()):
                if parent not in closed:
                    closed.add(parent)
                    changed = True
    return frozenset(closed)


def validate_closed_tags(tags: frozenset[str]) -> None:
    """Reject structural contradictions that would create fictitious overlap."""

    if len(tags & _SUPERTYPES) > 1:
        raise ValueError("a target cannot have multiple card supertypes")
    if len(tags & _TRAINER_SUBTYPES) > 1:
        raise ValueError("a Trainer target cannot have multiple Trainer subtypes")
    if len(tags & _POKEMON_STAGES) > 1:
        raise ValueError("a Pokémon target cannot have multiple stages")
    if len(tags & _ENERGY_CLASSES) > 1:
        raise ValueError("an Energy target cannot be both Basic and Special")


def _normalized_words(label: str) -> str:
    value = label.casefold().replace("pokémon", "pokemon")
    value = re.sub(r"\s+card$", "", value)
    return re.sub(r"\s+", " ", value).strip()


def selector_from_label(label: str) -> SearchSelector:
    """Compile a supported literal search label into a conjunction of tags."""

    normalized = _normalized_words(label)

    direct = {
        "pokemon": frozenset({POKEMON}),
        "basic pokemon": frozenset({BASIC_POKEMON}),
        "evolution pokemon": frozenset({EVOLUTION_POKEMON}),
        "stage 1 pokemon": frozenset({STAGE_1_POKEMON}),
        "stage 2 pokemon": frozenset({STAGE_2_POKEMON}),
        "trainer": frozenset({TRAINER}),
        "item": frozenset({ITEM}),
        "pokemon tool": frozenset({POKEMON_TOOL}),
        "supporter": frozenset({SUPPORTER}),
        "stadium": frozenset({STADIUM}),
        "energy": frozenset({ENERGY}),
        "basic energy": frozenset({BASIC_ENERGY}),
        "special energy": frozenset({SPECIAL_ENERGY}),
        "basic team aqua pokemon": frozenset(
            {BASIC_POKEMON, f"{TEAM_PREFIX}team_aqua"}
        ),
        "basic team magma pokemon": frozenset(
            {BASIC_POKEMON, f"{TEAM_PREFIX}team_magma"}
        ),
    }
    if normalized in direct:
        return SearchSelector(
            label=label,
            required_tags=close_tags(direct[normalized]),
        )

    if normalized == "pokemon of different types":
        raise UnsupportedSearchSelector(
            "different-types search is a cross-selection diversity constraint"
        )

    pokemon_type = re.fullmatch(r"([a-z]+) pokemon", normalized)
    if pokemon_type is not None:
        type_name = pokemon_type.group(1)
        if type_name in _TYPE_NAMES:
            return SearchSelector(
                label=label,
                required_tags=frozenset(
                    {POKEMON, f"{TYPE_PREFIX}{type_name}"}
                ),
            )

    energy_type = re.fullmatch(
        r"(?:basic )?([a-z]+) energy",
        normalized,
    )
    if energy_type is not None:
        type_name = energy_type.group(1)
        if type_name in _TYPE_NAMES:
            tags = {
                ENERGY,
                f"{TYPE_PREFIX}{type_name}",
            }
            if normalized.startswith("basic "):
                tags.add(BASIC_ENERGY)
            return SearchSelector(
                label=label,
                required_tags=close_tags(tags),
            )

    raise UnsupportedSearchSelector(
        f"unsupported compiled search label: {label!r}"
    )


def make_demand(
    name: str,
    label: str,
    *,
    copies: int = 1,
) -> DemandChannel:
    return DemandChannel(
        name=name,
        copies=copies,
        selector=selector_from_label(label),
    )


def _axis_limit(
    output: SearchOutput,
    targets: Sequence[TargetGroup],
    remaining: tuple[int, ...],
) -> int:
    selector = selector_from_label(output.label)
    available = sum(
        count
        for target, count in zip(targets, remaining)
        if selector.matches(target)
    )
    if output.max_units is None:
        return available
    return min(output.max_units, available)


def enumerate_typed_target_profiles(
    outputs: Sequence[SearchOutput],
    targets: Sequence[TargetGroup],
    demands: Sequence[DemandChannel],
) -> TypedTargetAllocation:
    """Enumerate useful demand vectors under exact physical target allocation.

    Each retrieval unit must choose one remaining physical target group that
    matches the card-text search selector. That selected copy is then assigned
    to at most one currently unmet strategic demand whose selector it also
    matches.

    Selecting cards that satisfy no modeled demand is omitted because it cannot
    improve demand feasibility. The zero-output profile is also omitted.
    """

    output_axes = tuple(outputs)
    target_groups = tuple(targets)
    demand_channels = tuple(demands)

    if not demand_channels:
        raise ValueError("demands cannot be empty")
    if any(demand.copies < 0 for demand in demand_channels):
        raise ValueError("demand copies must be non-negative")

    for output in output_axes:
        selector_from_label(output.label)

    initial_remaining = tuple(
        target.copies
        for target in target_groups
    )
    zero_output = (0,) * len(demand_channels)

    states: set[
        tuple[tuple[int, ...], tuple[int, ...]]
    ] = {(initial_remaining, zero_output)}

    for output in output_axes:
        output_selector = selector_from_label(output.label)
        next_axis_states: set[
            tuple[tuple[int, ...], tuple[int, ...]]
        ] = set()

        for remaining, supplied in states:
            axis_limit = _axis_limit(
                output,
                target_groups,
                remaining,
            )
            layer = {(remaining, supplied)}
            next_axis_states.update(layer)

            for _ in range(axis_limit):
                following: set[
                    tuple[tuple[int, ...], tuple[int, ...]]
                ] = set()
                for current_remaining, current_supplied in layer:
                    for target_index, target in enumerate(target_groups):
                        if current_remaining[target_index] <= 0:
                            continue
                        if not output_selector.matches(target):
                            continue

                        for demand_index, demand in enumerate(demand_channels):
                            if current_supplied[demand_index] >= demand.copies:
                                continue
                            if not demand.selector.matches(target):
                                continue

                            reduced = list(current_remaining)
                            reduced[target_index] -= 1
                            increased = list(current_supplied)
                            increased[demand_index] += 1
                            following.add(
                                (
                                    tuple(reduced),
                                    tuple(increased),
                                )
                            )

                if not following:
                    break
                next_axis_states.update(following)
                layer = following

        states = next_axis_states

    profiles = tuple(
        sorted(
            {
                supplied
                for _, supplied in states
                if any(supplied)
            }
        )
    )
    full = tuple(
        demand.copies
        for demand in demand_channels
    )
    full_feasible = full in profiles
    minimum_unmet = min(
        (
            sum(
                max(0, needed - supplied)
                for needed, supplied in zip(
                    full,
                    profile,
                )
            )
            for profile in profiles
        ),
        default=sum(full),
    )

    return TypedTargetAllocation(
        profiles=profiles,
        full_demand_feasible=full_feasible,
        minimum_unmet_units=minimum_unmet,
    )
