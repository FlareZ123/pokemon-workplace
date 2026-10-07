"""Reproduce Pokemon TCG KO-trigger visibility after attack-phase removal."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from knockout_redirection_routes import destinations_for_redirection
from knockout_redirection_taxonomy import ATTACHED_ENERGY_TO_HAND
from knockout_zone_routing import discard_pending_with_zone_routes
from pre_ko_attachment_snapshot import apply_attack_attachment_discard
from results.knockout_redirection_routes.reproduce import build_pending
from simultaneous_knockout_conservation import prepare_knock_out_batch


def main() -> None:
    initial, original_pending = build_pending()
    pre_attack_state = original_pending.state

    after_attack_effect = apply_attack_attachment_discard(
        pre_attack_state,
        pokemon_id="a",
        card_ids=("water-1",),
    )
    assert after_attack_effect is not None
    assert after_attack_effect.ledger.exchangeable.count(
        "basic-water", "discard"
    ) == 1

    board = after_attack_effect.board
    assert board is not None
    target = board.get("a")
    assert tuple(card.card_id for card in target.attachments) == (
        "water-2",
        "dce-a",
        "band-a",
    )

    pending = prepare_knock_out_batch(after_attack_effect, ("a",))
    assert pending is not None

    assert destinations_for_redirection(
        pending,
        pokemon_id="a",
        routing_signature=ATTACHED_ENERGY_TO_HAND,
        selected_energy_ids=("water-1", "water-2"),
    ) is None

    routes = destinations_for_redirection(
        pending,
        pokemon_id="a",
        routing_signature=ATTACHED_ENERGY_TO_HAND,
        selected_energy_ids=("water-2",),
    )
    assert routes == {"water-2": "hand"}

    result = discard_pending_with_zone_routes(
        pending,
        promote_id="b",
        destinations=routes,
    )
    assert result is not None
    assert result.board is not None
    assert result.board.active_id == "b"

    assert result.ledger.exchangeable.count("basic-water", "discard") == 1
    assert result.ledger.exchangeable.count("basic-water", "hand") == 1
    assert result.ledger.exchangeable.count("dce", "discard") == 1
    assert result.ledger.exchangeable.count("muscle-band", "discard") == 1
    assert result.ledger.totals() == initial.totals()

    assert apply_attack_attachment_discard(
        pre_attack_state,
        pokemon_id="a",
        card_ids=(),
    ) is None
    assert apply_attack_attachment_discard(
        pre_attack_state,
        pokemon_id="a",
        card_ids=("water-1", "water-1"),
    ) is None
    assert apply_attack_attachment_discard(
        pre_attack_state,
        pokemon_id="a",
        card_ids=("unknown",),
    ) is None
    assert apply_attack_attachment_discard(
        pre_attack_state,
        pokemon_id="b",
        card_ids=("water-1",),
    ) is None

    print("Pre-KO attachment snapshot regressions passed")


if __name__ == "__main__":
    main()
