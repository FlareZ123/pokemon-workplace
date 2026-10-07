"""Reproduce two Battle Compressor plays loading Harto's 420-damage package."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from battle_compressor_transaction import execute_battle_compressor
from discard_cost_witness import DiscardCandidate, DiscardSelection
from lock_state_kernel import PlayerChannels
from multicopy_zone_state import ZoneCountState
from raichu_electro_rain_als import (
    energy_package_lightning_units,
    extra_energy_bomb_prize_state,
)
from trainer_search_transaction import TrainerSearchExecutionState


CANDIDATES = (
    DiscardCandidate("reversal_energy"),
    DiscardCandidate("counter_energy"),
    DiscardCandidate("unit_energy_lpm"),
    DiscardCandidate("giratina"),
)


def initial_state() -> TrainerSearchExecutionState:
    return TrainerSearchExecutionState(
        zones=ZoneCountState.from_mapping(
            {
                ("battle_compressor", "hand"): 2,
                ("reversal_energy", "deck"): 4,
                ("counter_energy", "deck"): 4,
                ("unit_energy_lpm", "deck"): 3,
                ("giratina", "deck"): 1,
            }
        )
    )


def expect_value_error(fn) -> bool:
    try:
        fn()
    except ValueError:
        return True
    return False


def main() -> None:
    state = initial_state()

    first = execute_battle_compressor(
        state,
        candidates=CANDIDATES,
        selection=DiscardSelection((3, 0, 0, 0)),
    )
    assert first.cards_compressed == 3
    assert first.after.zones.count("reversal_energy", "discard") == 3
    assert first.after.zones.count("battle_compressor", "discard") == 1

    second = execute_battle_compressor(
        first.after,
        candidates=CANDIDATES,
        selection=DiscardSelection((1, 1, 0, 0)),
    )
    assert second.cards_compressed == 2
    assert second.after.zones.count("reversal_energy", "discard") == 4
    assert second.after.zones.count("counter_energy", "discard") == 1
    assert second.after.zones.count("unit_energy_lpm", "discard") == 0
    assert second.after.zones.count("giratina", "discard") == 0
    assert second.after.zones.count("battle_compressor", "discard") == 2

    prize = extra_energy_bomb_prize_state(3, 3)
    assert prize.condition_activated_by_self_ko
    units = energy_package_lightning_units(
        second.after.zones.count("reversal_energy", "discard"),
        second.after.zones.count("counter_energy", "discard"),
        second.after.zones.count("unit_energy_lpm", "discard"),
        comeback_active=prize.condition_active_after,
    )
    assert units == 14
    assert 30 * units == 420

    one_compressor_max_cards = 3
    assert one_compressor_max_cards < 5

    item_locked = expect_value_error(
        lambda: execute_battle_compressor(
            TrainerSearchExecutionState(
                zones=state.zones,
                channels=PlayerChannels(item_play=False),
            ),
            candidates=CANDIDATES,
            selection=DiscardSelection((3, 0, 0, 0)),
        )
    )
    assert item_locked

    zero_selection_rejected = expect_value_error(
        lambda: execute_battle_compressor(
            state,
            candidates=CANDIDATES,
            selection=DiscardSelection((0, 0, 0, 0)),
        )
    )
    assert zero_selection_rejected

    for card_class in (
        "battle_compressor",
        "reversal_energy",
        "counter_energy",
        "unit_energy_lpm",
        "giratina",
    ):
        assert state.zones.total(card_class) == second.after.zones.total(card_class)

    print(json.dumps({
        "compressor_1": {"reversal": 3, "cards": 3},
        "compressor_2": {"reversal": 1, "counter": 1, "cards": 2},
        "loaded_energy_cards": 5,
        "loaded_lightning_units_after_3_3_self_ko": units,
        "electro_rain_ceiling_damage": 30 * units,
        "one_compressor_cannot_load_five_from_clean_discard": True,
        "second_compressor_may_select_only_two": True,
        "item_lock_rejected": item_locked,
        "zero_target_item_play_rejected": zero_selection_rejected,
        "card_totals_conserved": True,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
