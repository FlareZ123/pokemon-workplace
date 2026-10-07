from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from board_position_state import BoardPokemon, PokemonCard, make_state
from healing_profile_compiler import (
    HealingProfile,
    HealingTarget,
    apply_healing_profile,
    compile_healing_profiles,
)


profiles = compile_healing_profiles(ROOT / "resources")
assert profiles
assert all(row.heal_damage > 0 and row.heal_damage % 10 == 0 for row in profiles)
keys = tuple(
    (row.card_id, row.source_kind, row.source_name)
    for row in profiles
)
assert len(keys) == len(set(keys))

potions = [
    row
    for row in profiles
    if row.name == "Potion"
    and row.source_kind == "trainer"
    and row.target == HealingTarget.SELECTED_OWN_POKEMON
    and row.heal_damage == 30
]
assert potions, "expected at least one legal Potion heal-30 profile"

board = make_state(
    (
        BoardPokemon(
            "active",
            (PokemonCard("active-card", "Active"),),
            retreat_cost=1,
            damage_counters=7,
        ),
        BoardPokemon(
            "bench",
            (PokemonCard("bench-card", "Bench"),),
            retreat_cost=1,
            damage_counters=2,
        ),
    ),
    active_id="active",
)

trainer = HealingProfile(
    card_id="fixture-potion",
    name="Fixture Potion",
    source_kind="trainer",
    action_class="Item",
    source_name=None,
    target=HealingTarget.SELECTED_OWN_POKEMON,
    heal_damage=30,
    effect_text="Heal 30 damage from 1 of your Pokémon.",
)
healed = apply_healing_profile(
    trainer,
    board,
    selected_pokemon_id="active",
)
assert healed is not None
assert healed.get("active").damage_counters == 4
assert healed.get("bench").damage_counters == 2

over_healed = apply_healing_profile(
    trainer,
    board,
    selected_pokemon_id="bench",
)
assert over_healed is not None
assert over_healed.get("bench").damage_counters == 0

undamaged = make_state(
    (
        BoardPokemon(
            "active",
            (PokemonCard("clean-card", "Clean"),),
            retreat_cost=0,
        ),
    ),
    active_id="active",
)
assert apply_healing_profile(
    trainer,
    undamaged,
    selected_pokemon_id="active",
) is None

attack = HealingProfile(
    card_id="fixture-drain",
    name="Fixture Drain",
    source_kind="attack",
    action_class="Attack",
    source_name="Drain",
    target=HealingTarget.SOURCE_POKEMON,
    heal_damage=30,
    effect_text="Heal 30 damage from this Pokémon.",
)
same = apply_healing_profile(
    attack,
    undamaged,
    source_pokemon_id="active",
)
assert same == undamaged

counts = Counter((row.source_kind, row.target.value) for row in profiles)
amounts = Counter(row.heal_damage for row in profiles)
print({
    "profile_count": len(profiles),
    "unique_card_names": len({row.name for row in profiles}),
    "by_source_and_target": {
        f"{source}:{target}": count
        for (source, target), count in sorted(counts.items())
    },
    "heal_amounts": dict(sorted(amounts.items())),
    "potion_prints": tuple(row.card_id for row in potions),
})
