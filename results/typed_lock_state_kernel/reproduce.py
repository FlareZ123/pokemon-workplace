from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.lock_state_kernel import (  # noqa: E402
    PlayerChannels,
    PokemonState,
    apply_play_lock,
    apply_temporary_attack_lock,
    apply_temporary_retreat_lock,
    clear_attack_effects_on_position_or_evolution_change,
    garbotoxin_condition_met,
    stealthy_hood_protects,
    suppress_tool_effect,
)


def main() -> None:
    base = PlayerChannels()

    item_locked = apply_play_lock(base, "item")
    assert not item_locked.item_play
    assert item_locked.tool_play

    trainer_locked = apply_play_lock(base, "trainer")
    assert not trainer_locked.item_play
    assert not trainer_locked.tool_play
    assert not trainer_locked.supporter_play
    assert not trainer_locked.stadium_play
    assert trainer_locked.pokemon_play
    assert trainer_locked.basic_energy_play
    assert trainer_locked.special_energy_play

    special_energy_locked = apply_play_lock(base, "special_energy_play")
    assert not special_energy_locked.special_energy_play
    assert special_energy_locked.basic_energy_play

    all_hand_locked = apply_play_lock(base, "all_cards_from_hand")
    assert not all_hand_locked.item_play
    assert not all_hand_locked.tool_play
    assert not all_hand_locked.supporter_play
    assert not all_hand_locked.stadium_play
    assert not all_hand_locked.pokemon_play
    assert not all_hand_locked.basic_energy_play
    assert not all_hand_locked.special_energy_play

    target = apply_temporary_retreat_lock(PokemonState())
    target = apply_temporary_attack_lock(target)
    assert target.temporary_retreat_lock
    assert target.temporary_attack_lock
    cleared = clear_attack_effects_on_position_or_evolution_change(target)
    assert not cleared.temporary_retreat_lock
    assert not cleared.temporary_attack_lock

    garbodor = PokemonState(tool_attached=True)
    hood_holder = PokemonState(tool_attached=True)
    assert garbotoxin_condition_met(garbodor)
    assert stealthy_hood_protects(hood_holder)

    garbodor_under_tower = suppress_tool_effect(garbodor)
    hood_under_tower = suppress_tool_effect(hood_holder)
    assert garbotoxin_condition_met(garbodor_under_tower)
    assert garbodor_under_tower.tool_attached
    assert not garbodor_under_tower.tool_effect_enabled
    assert not stealthy_hood_protects(hood_under_tower)

    print("typed lock-state kernel regressions passed")


if __name__ == "__main__":
    main()
