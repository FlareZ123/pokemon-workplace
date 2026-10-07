from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from board_position_state import BoardPokemon, PokemonCard, make_state
from energy_disruption_executor import resolve_energy_disruption
from energy_disruption_profile_compiler import (
    EnergyDisruptionProfile,
    EnergyRestriction,
    OpponentTargetScope,
    compile_energy_disruption_profiles,
)
from identity_materialization import IdentityLedger, materialize, put_in_play_instance
from multicopy_zone_state import ZoneCountState
from stack_knockout_conservation import StackBoardMaterialState, attach_from_hand
from board_position_state import AttachmentKind


profiles = compile_energy_disruption_profiles(ROOT / "resources")
assert profiles
names = {row.name for row in profiles}
assert "Crushing Hammer" in names
assert "Enhanced Hammer" in names

initial = IdentityLedger(
    ZoneCountState.from_mapping({
        ("class:target", "hand"): 1,
        ("class:basic-energy", "hand"): 1,
        ("class:special-energy", "hand"): 1,
    })
)
ledger = materialize(
    initial,
    card_class="class:target",
    card_name="Target",
    source_zone="hand",
    instance_id="target-card",
)
ledger = put_in_play_instance(ledger, "target-card", "target")
board = make_state(
    (
        BoardPokemon(
            "target",
            (PokemonCard("target-card", "Target"),),
            retreat_cost=1,
        ),
    ),
    active_id="target",
)
state = StackBoardMaterialState(ledger, board)
state = attach_from_hand(
    state,
    pokemon_id="target",
    card_class="class:basic-energy",
    instance_id="basic-e",
    card_name="Basic Energy",
    kind=AttachmentKind.ENERGY,
    retreat_units=1,
)
assert state is not None
state = attach_from_hand(
    state,
    pokemon_id="target",
    card_class="class:special-energy",
    instance_id="special-e",
    card_name="Special Energy",
    kind=AttachmentKind.ENERGY,
    retreat_units=1,
)
assert state is not None

crushing = EnergyDisruptionProfile(
    card_id="fixture-crushing",
    name="Crushing Hammer",
    source_kind="trainer",
    action_class="Item",
    source_name=None,
    energy_restriction=EnergyRestriction.ANY,
    target_scope=OpponentTargetScope.SELECTED_POKEMON,
    coin_heads_required=True,
    effect_text="Flip a coin. If heads, discard an Energy from 1 of your opponent's Pokémon.",
)

tails = resolve_energy_disruption(
    crushing,
    state,
    coin_heads=False,
)
assert tails is not None
assert tails.state == state
assert tails.discarded_instance_id is None

heads = resolve_energy_disruption(
    crushing,
    state,
    target_pokemon_id="target",
    energy_instance_id="basic-e",
    coin_heads=True,
)
assert heads is not None
assert heads.discarded_instance_id == "basic-e"
assert heads.state.ledger.exchangeable.count("class:basic-energy", "discard") == 1
assert tuple(card.card_id for card in heads.state.board.get("target").attachments) == (
    "special-e",
)
assert heads.state.ledger.totals() == state.ledger.totals()

enhanced = EnergyDisruptionProfile(
    card_id="fixture-enhanced",
    name="Enhanced Hammer",
    source_kind="trainer",
    action_class="Item",
    source_name=None,
    energy_restriction=EnergyRestriction.SPECIAL,
    target_scope=OpponentTargetScope.SELECTED_POKEMON,
    coin_heads_required=False,
    effect_text="Discard a Special Energy from 1 of your opponent's Pokémon.",
)
blocked_basic = resolve_energy_disruption(
    enhanced,
    state,
    target_pokemon_id="target",
    energy_instance_id="basic-e",
    special_energy_instance_ids=frozenset({"special-e"}),
)
assert blocked_basic is None

special = resolve_energy_disruption(
    enhanced,
    state,
    target_pokemon_id="target",
    energy_instance_id="special-e",
    special_energy_instance_ids=frozenset({"special-e"}),
)
assert special is not None
assert special.discarded_instance_id == "special-e"
assert special.state.ledger.exchangeable.count("class:special-energy", "discard") == 1

counts = Counter(
    (
        row.source_kind,
        row.energy_restriction.value,
        row.target_scope.value,
        row.coin_heads_required,
    )
    for row in profiles
)
print({
    "profile_count": len(profiles),
    "unique_names": len({row.name for row in profiles}),
    "profile_families": {
        str(key): value
        for key, value in sorted(counts.items(), key=lambda item: str(item[0]))
    },
    "crushing_hammer_prints": tuple(
        row.card_id for row in profiles if row.name == "Crushing Hammer"
    ),
    "enhanced_hammer_prints": tuple(
        row.card_id for row in profiles if row.name == "Enhanced Hammer"
    ),
})
