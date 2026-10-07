"""Alolan Raichu / Electrode-GX Prize-state and Energy-unit ALS kernel.

Card-grounded Harto Miki package:
- 4 Reversal Energy: 3 of every type when its comeback condition is active on
  Alolan Raichu; otherwise 1 Colorless.
- 4 Counter Energy: 2 of every type when its comeback condition is active on
  Alolan Raichu; otherwise 1 Colorless.
- 3 Unit Energy LightningPsychicMetal: always 1 Lightning/Psychic/Metal.
- Electrode-GX Extra Energy Bomb attaches 5 Energy cards from discard, then
  Knocks itself Out.
- Alolan Raichu Electro Rain discards any amount of Lightning Energy and places
  30 damage once for each Energy discarded.

The kernel deliberately separates five physical Energy cards from the number of
Lightning Energy units those cards provide after the self-KO Prize transition.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

from post_knockout_game_resolution import (
    Outcome,
    resolve_prize_and_board_loss_conditions,
)


EVERY_TYPE = frozenset(
    {
        "Grass",
        "Fire",
        "Water",
        "Lightning",
        "Psychic",
        "Fighting",
        "Darkness",
        "Metal",
        "Fairy",
        "Colorless",
    }
)


@dataclass(frozen=True)
class AttachedEnergy:
    name: str
    units: int
    types: frozenset[str]

    def __post_init__(self) -> None:
        if self.units <= 0:
            raise ValueError("Energy units must be positive")
        if not self.types:
            raise ValueError("provided Energy types cannot be empty")


@dataclass(frozen=True)
class ExtraEnergyBombState:
    own_prizes_before: int
    opponent_prizes_before: int
    opponent_prizes_after: int
    condition_active_before: bool
    condition_active_after: bool
    condition_activated_by_self_ko: bool
    terminal_loss: bool


@dataclass(frozen=True)
class ElectroRainMaximum:
    state: ExtraEnergyBombState
    attached_cards: tuple[AttachedEnergy, ...]
    lightning_units: int
    damage_placements: int
    maximum_damage: int


def extra_energy_bomb_prize_state(
    own_prizes_remaining: int,
    opponent_prizes_remaining: int,
) -> ExtraEnergyBombState:
    """Apply Electrode-GX's two-Prize self-KO at the count/game boundary."""

    if not 1 <= own_prizes_remaining <= 6:
        raise ValueError("own_prizes_remaining must be in [1, 6]")
    if not 1 <= opponent_prizes_remaining <= 6:
        raise ValueError("opponent_prizes_remaining must be in [1, 6]")

    taken = min(2, opponent_prizes_remaining)
    opponent_after = opponent_prizes_remaining - taken

    resolution = resolve_prize_and_board_loss_conditions(
        player_ids=("self", "opponent"),
        prizes_remaining={
            "self": own_prizes_remaining,
            "opponent": opponent_after,
        },
        pokemon_in_play={
            # The modeled line assumes Alolan Raichu survives the Electrode KO
            # and the opponent also still has at least one Pokemon in play.
            "self": 1,
            "opponent": 1,
        },
    )
    terminal_loss = resolution.outcome("self") == Outcome.LOSS

    before = own_prizes_remaining > opponent_prizes_remaining
    after = (
        not terminal_loss
        and own_prizes_remaining > opponent_after
    )
    return ExtraEnergyBombState(
        own_prizes_before=own_prizes_remaining,
        opponent_prizes_before=opponent_prizes_remaining,
        opponent_prizes_after=opponent_after,
        condition_active_before=before,
        condition_active_after=after,
        condition_activated_by_self_ko=(not before and after),
        terminal_loss=terminal_loss,
    )


def harto_energy_pool(*, comeback_active: bool) -> tuple[AttachedEnergy, ...]:
    """Return the 11-card Harto Special Energy pool under one Prize state."""

    reversal = AttachedEnergy(
        "Reversal Energy",
        3 if comeback_active else 1,
        EVERY_TYPE if comeback_active else frozenset({"Colorless"}),
    )
    counter = AttachedEnergy(
        "Counter Energy",
        2 if comeback_active else 1,
        EVERY_TYPE if comeback_active else frozenset({"Colorless"}),
    )
    unit = AttachedEnergy(
        "Unit Energy LightningPsychicMetal",
        1,
        frozenset({"Lightning", "Psychic", "Metal"}),
    )
    return (reversal,) * 4 + (counter,) * 4 + (unit,) * 3


def lightning_units(cards: tuple[AttachedEnergy, ...]) -> int:
    """Count currently provided Lightning Energy units on the chosen cards."""

    return sum(
        card.units
        for card in cards
        if "Lightning" in card.types
    )


def maximum_electro_rain_after_bomb(
    own_prizes_remaining: int,
    opponent_prizes_remaining: int,
    *,
    attached_card_count: int = 5,
) -> ElectroRainMaximum | None:
    """Maximize Electro Rain units after one Extra Energy Bomb self-KO.

    Returns None if the self-KO ends the game before the player can attack.
    """

    state = extra_energy_bomb_prize_state(
        own_prizes_remaining,
        opponent_prizes_remaining,
    )
    if state.terminal_loss:
        return None

    pool = harto_energy_pool(comeback_active=state.condition_active_after)
    if not 0 <= attached_card_count <= len(pool):
        raise ValueError("attached_card_count is outside the Harto Energy pool")

    best_cards: tuple[AttachedEnergy, ...] = ()
    best_units = -1
    for indexes in combinations(range(len(pool)), attached_card_count):
        cards = tuple(pool[index] for index in indexes)
        units = lightning_units(cards)
        if units > best_units:
            best_units = units
            best_cards = cards

    placements = max(0, best_units)
    return ElectroRainMaximum(
        state=state,
        attached_cards=best_cards,
        lightning_units=placements,
        damage_placements=placements,
        maximum_damage=30 * placements,
    )


def prize_state_matrix() -> tuple[ExtraEnergyBombState, ...]:
    return tuple(
        extra_energy_bomb_prize_state(own, opponent)
        for own in range(1, 7)
        for opponent in range(1, 7)
    )
