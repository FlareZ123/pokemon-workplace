"""Compare signature-compressed and full KO terminal projections exactly."""

from pathlib import Path
from random import Random
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from ko_order_signature_projection import project_with_zone_signatures
from ko_order_terminal_projection import project_terminal_outcomes
from knockout_redirection_routes import destinations_for_redirection
from knockout_redirection_taxonomy import (
    ATTACHED_ENERGY_TO_HAND,
    POKEMON_TO_LOST,
    SELF_TO_HAND,
)
from results.knockout_redirection_routes.reproduce import build_pending


def compare(pending, programs, precedences=()):
    full = project_terminal_outcomes(
        pending, programs, promote_id="b", precedences=precedences
    )
    fast = project_with_zone_signatures(
        pending, programs, promote_id="b", precedences=precedences
    )
    assert fast.outcomes == full
    assert fast.physical_disposals == len(full)
    assert fast.physical_disposals <= fast.instance_route_outcomes
    assert sum(row.order_count for row in fast.outcomes) == sum(
        row.order_count for row in full
    )
    return fast


def main():
    initial, pending = build_pending()

    copies = {
        "first": {"water-1": "hand", "water-2": "discard"},
        "second": {"water-1": "discard", "water-2": "hand"},
    }
    fast = compare(pending, copies)
    assert fast.instance_route_outcomes == 2
    assert fast.physical_disposals == 1
    assert fast.outcomes[0].order_count == 2
    assert fast.outcomes[0].state.ledger.totals() == initial.totals()

    def program(signature, selected=()):
        routes = destinations_for_redirection(
            pending,
            pokemon_id="a",
            routing_signature=signature,
            selected_energy_ids=selected,
        )
        assert routes is not None
        return routes

    programs = {
        "return": program(SELF_TO_HAND),
        "lost": program(POKEMON_TO_LOST),
        "recover": program(ATTACHED_ENERGY_TO_HAND, ("water-1", "water-2")),
    }
    assert compare(pending, programs).physical_disposals == 4
    assert compare(
        pending, programs, (("return", "lost"), ("return", "recover"))
    ).physical_disposals == 1

    board = pending.state.board
    assert board is not None
    pokemon = next(row for row in board.pokemon if row.pokemon_id == "a")
    ids = tuple(
        [card.card_id for card in pokemon.stack]
        + [card.card_id for card in pokemon.attachments]
    )
    rng = Random(20261009)
    saved = 1
    for n in range(1, 6):
        for _ in range(24):
            programs = {
                f"e{i}": {
                    card_id: rng.choice(("hand", "discard", "lost_zone"))
                    for card_id in ids
                    if rng.random() < 0.5
                }
                for i in range(n)
            }
            precedences = tuple(
                (f"e{i}", f"e{j}")
                for i in range(n)
                for j in range(i + 1, n)
                if rng.random() < 0.16
            )
            result = compare(pending, programs, precedences)
            saved += result.instance_route_outcomes - result.physical_disposals
    assert saved > 0
    print(
        "Signature-compressed KO projection passed: 120 randomized "
        f"full-kernel cross-checks, at least {saved} conserved disposal calls saved"
    )


if __name__ == "__main__":
    main()
