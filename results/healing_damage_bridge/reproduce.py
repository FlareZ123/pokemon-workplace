from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from board_object_kernel import make_board, make_pokemon
from damage_board_bridge import resolve_attack_damage_phase
from damage_calculation_kernel import AttackDamage, DamageContext
from healing_damage_bridge import apply_healing_to_object_board
from healing_profile_compiler import HealingProfile, HealingTarget


potion = HealingProfile(
    card_id="fixture-potion",
    name="Potion",
    source_kind="trainer",
    action_class="Item",
    source_name=None,
    target=HealingTarget.SELECTED_OWN_POKEMON,
    heal_damage=30,
    effect_text="Heal 30 damage from 1 of your Pokémon.",
)

damaged = make_board(
    make_pokemon(
        "target",
        "Target",
        damage_counters=16,
    )
)
hp = {"target": 200}
incoming = DamageContext(AttackDamage(50))

without_heal = resolve_attack_damage_phase(
    damaged,
    damage_target_id="target",
    damage_context=incoming,
    hp_by_object_id=hp,
)
assert without_heal.board.get("target").damage_counters == 21
assert without_heal.knocked_out_ids == ("target",)

healed = apply_healing_to_object_board(
    potion,
    damaged,
    selected_object_id="target",
)
assert healed is not None
assert healed.get("target").damage_counters == 13

with_heal = resolve_attack_damage_phase(
    healed,
    damage_target_id="target",
    damage_context=incoming,
    hp_by_object_id=hp,
)
assert with_heal.board.get("target").damage_counters == 18
assert with_heal.knocked_out_ids == ()

overheal_board = make_board(
    make_pokemon(
        "target",
        "Target",
        damage_counters=2,
    )
)
overhealed = apply_healing_to_object_board(
    potion,
    overheal_board,
    selected_object_id="target",
)
assert overhealed is not None
assert overhealed.get("target").damage_counters == 0

clean = make_board(make_pokemon("target", "Target"))
assert apply_healing_to_object_board(
    potion,
    clean,
    selected_object_id="target",
) is None

print({
    "starting_damage": 160,
    "incoming_damage": 50,
    "ko_without_heal": without_heal.knocked_out_ids,
    "damage_after_heal_then_attack": with_heal.board.get("target").damage_counters * 10,
    "ko_after_heal": with_heal.knocked_out_ids,
    "overheal_floor": overhealed.get("target").damage_counters,
})
