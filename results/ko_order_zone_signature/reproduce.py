"""Cross-check KO zone signatures against the full conserved disposal kernel."""

from pathlib import Path
from random import Random
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from identity_materialization import assert_conserved
from ko_order_zone_signature import terminal_zone_signature
from knockout_redirection_routes import destinations_for_redirection
from knockout_redirection_taxonomy import POKEMON_TO_LOST, SELF_TO_HAND
from knockout_zone_routing import discard_pending_with_zone_routes
from results.knockout_redirection_routes.reproduce import build_pending


def main():
    initial, pending = build_pending()
    board = pending.state.board
    assert board is not None
    pokemon = next(row for row in board.pokemon if row.pokemon_id == "a")
    ids = tuple(
        [card.card_id for card in pokemon.stack]
        + [card.card_id for card in pokemon.attachments]
    )

    def disposed(routes):
        state = discard_pending_with_zone_routes(
            pending,
            promote_id="b",
            destinations=routes,
        )
        assert state is not None
        assert_conserved(initial, state.ledger)
        return state

    # Two copy-identity-different routes project to one terminal state.
    left = {"water-1": "hand", "water-2": "discard"}
    right = {"water-1": "discard", "water-2": "hand"}
    assert left != right
    assert terminal_zone_signature(pending, destinations=left) == terminal_zone_signature(
        pending, destinations=right
    )
    assert disposed(left) == disposed(right)

    hand = destinations_for_redirection(
        pending, pokemon_id="a", routing_signature=SELF_TO_HAND
    )
    lost = destinations_for_redirection(
        pending, pokemon_id="a", routing_signature=POKEMON_TO_LOST
    )
    assert hand is not None and lost is not None
    assert terminal_zone_signature(pending, destinations=hand) != terminal_zone_signature(
        pending, destinations=lost
    )
    assert disposed(hand) != disposed(lost)

    # Independent property test: signatures identify exactly the full
    # terminal states for a fixed pending batch and promotion.
    rng = Random(20261008)
    by_signature = {}
    samples = 220
    for _ in range(samples):
        routes = {
            instance_id: rng.choice(("hand", "discard", "lost_zone"))
            for instance_id in ids
            if rng.random() < 0.7
        }
        signature = terminal_zone_signature(pending, destinations=routes)
        state = disposed(routes)
        if signature in by_signature:
            assert by_signature[signature] == state
        else:
            assert all(old_state != state for old_state in by_signature.values())
            by_signature[signature] = state

    assert len(by_signature) < samples
    for bad in (
        {"water-1": "attached"},
        {"aegislash-a": "in_play"},
        {"water-1": ""},
        {"survivor-bidoof": "hand"},
    ):
        try:
            terminal_zone_signature(pending, destinations=bad)
        except ValueError:
            pass
        else:
            raise AssertionError(f"invalid route was accepted: {bad}")

    print(
        f"KO zone signature regression passed: {samples} sampled valid route "
        f"programs collapsed to {len(by_signature)} terminal states"
    )


if __name__ == "__main__":
    main()
