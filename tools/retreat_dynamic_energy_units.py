"""Refresh state-dependent attached Energy units before Retreat payment."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Iterable

from board_object_kernel import EnergyAttachment
from energy_board_conservation import EnergyBoardState
from retreat_energy_transaction import (
    RetreatEnergyTransactionResult,
    RetreatEnergyTransactionState,
    retreat_with_energy_destinations,
)


IGNITION_ENERGY_PRINT_IDS = frozenset({
    "rsv10pt5-86",
    "me2-124",
})
TWIN_ENERGY_PRINT_IDS = frozenset({
    "swsh2-174",
    "swsh2-209",
})
NEO_UPPER_ENERGY_PRINT_IDS = frozenset({
    "sv5-162",
})
COUNTER_ENERGY_PRINT_IDS = frozenset({
    "sm4-100",
    "sm4-122",
})
REVERSAL_ENERGY_PRINT_IDS = frozenset({
    "sv2-192",
    "sv4-266",
})
SUPER_BOOST_ENERGY_PRINT_IDS = frozenset({
    "sm5-136",
})
DYNAMIC_UNIT_PRINT_IDS = frozenset().union(
    IGNITION_ENERGY_PRINT_IDS,
    TWIN_ENERGY_PRINT_IDS,
    NEO_UPPER_ENERGY_PRINT_IDS,
    COUNTER_ENERGY_PRINT_IDS,
    REVERSAL_ENERGY_PRINT_IDS,
    SUPER_BOOST_ENERGY_PRINT_IDS,
)

_STAGE1_TAGS = frozenset({"Stage1", "Stage 1"})
_STAGE2_TAGS = frozenset({"Stage2", "Stage 2"})
_EVOLUTION_TAGS = _STAGE1_TAGS | _STAGE2_TAGS | frozenset({"Evolution"})
_POKEMON_V_TAGS = frozenset({
    "Pokemon V",
    "Pokémon V",
    "Pokemon VMAX",
    "Pokémon VMAX",
    "Pokemon VSTAR",
    "Pokémon VSTAR",
})
_POKEMON_GX_TAGS = frozenset({"Pokemon-GX", "Pokémon-GX"})
_POKEMON_EX_TAGS = frozenset({"Pokemon-EX", "Pokémon-EX"})
_RULE_BOX_TAGS = frozenset({
    "RuleBox",
    "Rule Box",
    "Pokemon ex",
    "Pokémon ex",
    "Radiant",
    "Prism Star",
}) | _POKEMON_V_TAGS | _POKEMON_GX_TAGS | _POKEMON_EX_TAGS


@dataclass(frozen=True)
class RetreatEnergyProviderContext:
    """Non-board facts needed by supported dynamic Energy providers."""

    own_prizes_remaining: int | None = None
    opponent_prizes_remaining: int | None = None

    def __post_init__(self) -> None:
        values = (self.own_prizes_remaining, self.opponent_prizes_remaining)
        if (values[0] is None) != (values[1] is None):
            raise ValueError("Prize counts must be both known or both unknown")
        if any(value is not None and value < 0 for value in values):
            raise ValueError("Prize counts must be non-negative")

    @property
    def prize_counts_known(self) -> bool:
        return self.own_prizes_remaining is not None

    @property
    def behind_on_prizes(self) -> bool | None:
        if not self.prize_counts_known:
            return None
        assert self.own_prizes_remaining is not None
        assert self.opponent_prizes_remaining is not None
        return self.own_prizes_remaining > self.opponent_prizes_remaining


def holder_is_evolution(tags: frozenset[str]) -> bool:
    return bool(tags & _EVOLUTION_TAGS)


def holder_is_stage2(tags: frozenset[str]) -> bool:
    return bool(tags & _STAGE2_TAGS)


def holder_is_pokemon_v(tags: frozenset[str]) -> bool:
    return bool(tags & _POKEMON_V_TAGS)


def holder_is_pokemon_gx(tags: frozenset[str]) -> bool:
    return bool(tags & _POKEMON_GX_TAGS)


def holder_is_pokemon_ex(tags: frozenset[str]) -> bool:
    return bool(tags & _POKEMON_EX_TAGS)


def holder_has_rule_box(tags: frozenset[str]) -> bool:
    return bool(tags & _RULE_BOX_TAGS)


def _units(count: int) -> tuple[str, ...]:
    return ("C",) * count


def current_retreat_units(
    energy: EnergyAttachment,
    *,
    holder_tags: frozenset[str],
    stage2_in_play: int,
    context: RetreatEnergyProviderContext | None = None,
) -> tuple[str, ...]:
    """Resolve exact supported dynamic unit counts from current game state.

    The returned symbols are Colorless because Retreat only depends on Energy
    quantity. Provider type remains a separate attack-payment concern.

    Prize-dependent cards preserve the represented snapshot when Prize counts
    are unknown rather than guessing whether their conditional mode is active.
    Unknown prints also preserve their represented snapshot.
    """

    if context is None:
        context = RetreatEnergyProviderContext()

    if (
        energy.card_name == "Ignition Energy"
        and energy.print_id in IGNITION_ENERGY_PRINT_IDS
    ):
        return _units(3 if holder_is_evolution(holder_tags) else 1)

    if (
        energy.card_name == "Twin Energy"
        and energy.print_id in TWIN_ENERGY_PRINT_IDS
    ):
        restricted = (
            holder_is_pokemon_v(holder_tags)
            or holder_is_pokemon_gx(holder_tags)
        )
        return _units(1 if restricted else 2)

    if (
        energy.card_name == "Neo Upper Energy"
        and energy.print_id in NEO_UPPER_ENERGY_PRINT_IDS
    ):
        return _units(2 if holder_is_stage2(holder_tags) else 1)

    if (
        energy.card_name == "Super Boost Energy ◇"
        and energy.print_id in SUPER_BOOST_ENERGY_PRINT_IDS
    ):
        return _units(4 if stage2_in_play >= 3 else 1)

    if (
        energy.card_name == "Counter Energy"
        and energy.print_id in COUNTER_ENERGY_PRINT_IDS
    ):
        eligible_holder = not (
            holder_is_pokemon_gx(holder_tags)
            or holder_is_pokemon_ex(holder_tags)
        )
        if not eligible_holder:
            return _units(1)
        behind = context.behind_on_prizes
        if behind is None:
            return energy.units
        return _units(2 if behind else 1)

    if (
        energy.card_name == "Reversal Energy"
        and energy.print_id in REVERSAL_ENERGY_PRINT_IDS
    ):
        eligible_holder = (
            holder_is_evolution(holder_tags)
            and not holder_has_rule_box(holder_tags)
        )
        if not eligible_holder:
            return _units(1)
        behind = context.behind_on_prizes
        if behind is None:
            return energy.units
        return _units(3 if behind else 1)

    return energy.units



def unresolved_selected_prize_provider_ids(
    state: RetreatEnergyTransactionState,
    selected_energy_ids: Iterable[str],
    *,
    retreat_cost: int,
    context: RetreatEnergyProviderContext | None = None,
) -> tuple[str, ...]:
    """Report selected Prize-dependent cards only when legality is ambiguous.

    For Retreat, eligible Counter/Reversal Energy always supply at least one
    unit. If the selected physical cards already pay the cost at their lower
    bound, a Retreat is safe without knowing the Prize counts.
    """
    if retreat_cost <= 0 or (context is not None and context.prize_counts_known):
        return ()

    active = state.energy.board.get(state.energy.board.active_id)
    selected = frozenset(selected_energy_ids)
    lower_units = 0
    upper_units = 0
    uncertain: list[str] = []

    for energy in active.energy:
        if energy.instance_id not in selected:
            continue
        if (
            energy.card_name == "Counter Energy"
            and energy.print_id in COUNTER_ENERGY_PRINT_IDS
            and not holder_is_pokemon_gx(active.tags)
            and not holder_is_pokemon_ex(active.tags)
        ):
            lower, upper = 1, 2
            uncertain.append(energy.instance_id)
        elif (
            energy.card_name == "Reversal Energy"
            and energy.print_id in REVERSAL_ENERGY_PRINT_IDS
            and holder_is_evolution(active.tags)
            and not holder_has_rule_box(active.tags)
        ):
            lower, upper = 1, 3
            uncertain.append(energy.instance_id)
        else:
            lower = upper = len(energy.units)
        lower_units += lower
        upper_units += upper

    if lower_units < retreat_cost <= upper_units:
        return tuple(sorted(uncertain))
    return ()


def refresh_active_retreat_energy_units(
    state: RetreatEnergyTransactionState,
    *,
    context: RetreatEnergyProviderContext | None = None,
) -> RetreatEnergyTransactionState:
    """Refresh supported dynamic providers on the current Active Pokemon."""

    board = state.energy.board
    active = board.get(board.active_id)
    stage2_in_play = sum(
        1
        for pokemon in board.objects
        if holder_is_stage2(pokemon.tags)
    )
    refreshed_energy = tuple(
        replace(
            energy,
            units=current_retreat_units(
                energy,
                holder_tags=active.tags,
                stage2_in_play=stage2_in_play,
                context=context,
            ),
        )
        for energy in active.energy
    )
    if refreshed_energy == active.energy:
        return state

    refreshed_active = replace(active, energy=refreshed_energy)
    refreshed_board = replace(
        board,
        objects=tuple(
            refreshed_active if pokemon.object_id == active.object_id else pokemon
            for pokemon in board.objects
        ),
    )
    refreshed_board.validate()
    refreshed_energy_state = EnergyBoardState(
        zones=state.energy.zones,
        board=refreshed_board,
        instance_classes=state.energy.instance_classes,
    )
    return RetreatEnergyTransactionState(
        unified=state.unified,
        energy=refreshed_energy_state,
    )


def retreat_with_dynamic_energy_units(
    state: RetreatEnergyTransactionState,
    bench_object_id: str,
    *,
    retreat_cost: int,
    discard_energy_ids: Iterable[str],
    provider_context: RetreatEnergyProviderContext | None = None,
    opposing_scoop_up_block_active: bool = False,
    prism_star_energy_ids: Iterable[str] = (),
) -> RetreatEnergyTransactionResult | None:
    """Refresh supported providers, then execute the conserved Retreat."""

    selected = tuple(discard_energy_ids)
    refreshed = refresh_active_retreat_energy_units(
        state,
        context=provider_context,
    )
    if unresolved_selected_prize_provider_ids(
        refreshed,
        selected,
        retreat_cost=retreat_cost,
        context=provider_context,
    ):
        return None
    return retreat_with_energy_destinations(
        refreshed,
        bench_object_id,
        retreat_cost=retreat_cost,
        discard_energy_ids=selected,
        opposing_scoop_up_block_active=opposing_scoop_up_block_active,
        prism_star_energy_ids=prism_star_energy_ids,
    )
