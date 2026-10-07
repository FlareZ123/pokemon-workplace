from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from board_position_state import (
    AttachmentKind,
    BoardPokemon,
    PokemonCard,
    make_state,
)
from identity_liveness import IdentityReference
from identity_materialization import (
    IdentityLedger,
    assert_conserved,
    materialize,
    put_in_play_instance,
)
from multicopy_zone_state import ZoneCountState
from physical_zone_count import physical_zone_count
from stack_knockout_conservation import (
    StackBoardMaterialState,
    attach_from_hand,
)
from stack_zone_exit_conservation import leave_play_with_conservation
from zone_exit_identity_release import release_zone_exit_identity_group


def materialize_in_play(
    ledger,
    *,
    card_class,
    card_name,
    instance_id,
    pokemon_id,
):
    ledger = materialize(
        ledger,
        card_class=card_class,
        card_name=card_name,
        source_zone="hand",
        instance_id=instance_id,
    )
    return put_in_play_instance(ledger, instance_id, pokemon_id)


initial = IdentityLedger(
    ZoneCountState.from_mapping({
        ("bulba-class", "hand"): 1,
        ("ivy-class", "hand"): 1,
        ("bidoof-class", "hand"): 1,
        ("band-class", "hand"): 1,
    })
)
ledger = materialize_in_play(
    initial,
    card_class="bulba-class",
    card_name="Bulbasaur",
    instance_id="bulba-copy",
    pokemon_id="pokemon-a",
)
ledger = materialize_in_play(
    ledger,
    card_class="ivy-class",
    card_name="Ivysaur",
    instance_id="ivy-copy",
    pokemon_id="pokemon-a",
)
ledger = materialize_in_play(
    ledger,
    card_class="bidoof-class",
    card_name="Bidoof",
    instance_id="bidoof-copy",
    pokemon_id="pokemon-b",
)

board = make_state(
    (
        BoardPokemon(
            "pokemon-a",
            (
                PokemonCard("bulba-copy", "Bulbasaur"),
                PokemonCard("ivy-copy", "Ivysaur", "Bulbasaur"),
            ),
            retreat_cost=2,
        ),
        BoardPokemon(
            "pokemon-b",
            (PokemonCard("bidoof-copy", "Bidoof"),),
            retreat_cost=1,
        ),
    ),
    active_id="pokemon-a",
)
state = StackBoardMaterialState(ledger, board)
state = attach_from_hand(
    state,
    pokemon_id="pokemon-a",
    card_class="band-class",
    instance_id="band-copy",
    card_name="Muscle Band",
    kind=AttachmentKind.TOOL,
)
assert state is not None

moved = leave_play_with_conservation(
    state,
    "pokemon-a",
    pokemon_destination="hand",
    attachment_destination="hand",
    promote_id="pokemon-b",
    preserve_identity=True,
)
assert moved is not None
preserved_ids = moved.pokemon_card_ids + moved.attachment_card_ids
assert preserved_ids == ("bulba-copy", "ivy-copy", "band-copy")

for instance_id in preserved_ids:
    row = moved.state.ledger.instance(instance_id)
    assert row.zone == "hand"
    assert row.board_object_id is None
    assert row.attached_to is None

hold = IdentityReference(
    "effect:returned-evolution",
    "ivy-copy",
    "the enclosing effect still refers to the exact returned Evolution card",
)

before_blocked_release = moved.state
try:
    release_zone_exit_identity_group(
        moved.state,
        preserved_ids,
        references=(hold,),
    )
except ValueError:
    pass
else:
    raise AssertionError("one live reference must block atomic group release")

assert before_blocked_release == moved.state
for instance_id in preserved_ids:
    moved.state.ledger.instance(instance_id)

released = release_zone_exit_identity_group(
    moved.state,
    preserved_ids,
)
assert tuple(row.instance_id for row in released.ledger.instances) == (
    "bidoof-copy",
)
assert released.ledger.exchangeable.count("bulba-class", "hand") == 1
assert released.ledger.exchangeable.count("ivy-class", "hand") == 1
assert released.ledger.exchangeable.count("band-class", "hand") == 1
assert physical_zone_count(released.ledger, "hand") == 3
assert_conserved(initial, released.ledger)

print({
    "preserved_identity_ids": preserved_ids,
    "blocked_release_is_atomic": True,
    "released_after_reference_end": True,
    "physical_hand_size": physical_zone_count(released.ledger, "hand"),
    "remaining_materialized_ids": tuple(
        row.instance_id for row in released.ledger.instances
    ),
    "copy_totals_preserved": released.ledger.totals() == initial.totals(),
})
