from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from board_attachment_conservation import BoardMaterialState
from board_object_kernel import EnergyAttachment, make_board, make_pokemon
from energy_movement_conservation import move_energy_with_conservation
from identity_materialization import IdentityLedger, assert_conserved, attach_instance, materialize
from multicopy_zone_state import ZoneCountState

initial = IdentityLedger(ZoneCountState.from_mapping({("dce", "hand"): 1}))
ledger = materialize(initial, card_class="dce", card_name="DCE", source_zone="hand", instance_id="e")
ledger = attach_instance(ledger, "e", "a")
energy = EnergyAttachment("e", "DCE", ("C", "C"))
state = BoardMaterialState(ledger, make_board(make_pokemon("a", "A", energy=(energy,)), (make_pokemon("b", "B"),)))
moved = move_energy_with_conservation(state, "e", source_object_id="a", target_object_id="b")
assert moved is not None and moved.board is not None
assert moved.board.get("a").energy == ()
assert moved.board.get("b").energy == (energy,)
assert moved.ledger.instance("e").attached_to == "b"
assert_conserved(initial, moved.ledger)
print("Energy movement conservation regressions passed")
