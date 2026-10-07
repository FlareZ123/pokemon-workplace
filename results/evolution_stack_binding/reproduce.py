from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from board_object_kernel import EnergyAttachment, ToolAttachment, make_board, make_pokemon
from evolution_stack_binding import (
    begin_next_turn, devolve_top, ordinary_evolve, validate_ledger_binding,
)
from evolution_stack_state import PokemonStack, StackCard, make_evolution_state
from identity_materialization import CardInstance, IdentityLedger
from multicopy_zone_state import ZoneCountState


def ledger(*rows: CardInstance) -> IdentityLedger:
    return IdentityLedger(
        ZoneCountState.from_mapping({}),
        tuple(sorted(rows, key=lambda row: row.instance_id)),
    )


def main() -> None:
    energy = EnergyAttachment(
        "energy", "Double Colorless Energy", ("C", "C"), print_id="bw11-113"
    )
    tool = ToolAttachment("tool", "Air Balloon", print_id="me1-166")
    active = make_pokemon(
        "active", "Bulbasaur", print_id="base-print", tags=("Grass", "Basic"),
        energy=(energy,), tool=tool, temporary_attack_lock=True,
        damage_counters=4, special_conditions=("Poisoned",),
    )
    pivot = make_pokemon("pivot", "Pivot", tags=("Basic",))
    board = make_board(active, (pivot,))

    bulba = StackCard(
        "bulba", "Bulbasaur", 0, 80,
        tags=frozenset({"Grass", "Basic"}), print_id="base-print",
    )
    ivy = StackCard(
        "ivy", "Ivysaur", 1, 110, "Bulbasaur",
        frozenset({"Grass", "Stage 1"}), print_id="ivy-print",
    )
    venus = StackCard(
        "venus", "Mega Venusaur ex", 2, 380, "Ivysaur",
        frozenset({"Grass", "Stage 2", "MEGA", "ex"}), print_id="venus-print",
    )
    pivot_card = StackCard("pivot-card", "Pivot", 0, 100, tags=frozenset({"Basic"}))
    state = make_evolution_state(
        board,
        (PokemonStack("active", (bulba,)), PokemonStack("pivot", (pivot_card,))),
    )
    identities = ledger(
        CardInstance(
            "bulba", "bulba-class", "Bulbasaur", "in_play", board_object_id="active"
        ),
        CardInstance(
            "energy", "dce-class", "Double Colorless Energy",
            "attached", attached_to="active",
        ),
        CardInstance("ivy", "ivy-class", "Ivysaur", "hand"),
        CardInstance(
            "pivot-card", "pivot-class", "Pivot", "in_play", board_object_id="pivot"
        ),
        CardInstance(
            "tool", "balloon-class", "Air Balloon", "attached", attached_to="active"
        ),
        CardInstance("venus", "venus-class", "Mega Venusaur ex", "hand"),
    )
    validate_ledger_binding(state, identities)

    first = ordinary_evolve(state, identities, "active", ivy)
    assert first is not None
    evolved = first.state.board.get("active")
    assert evolved.card_name == "Ivysaur"
    assert evolved.print_id == "ivy-print"
    assert evolved.damage_counters == 4
    assert evolved.energy == (energy,) and evolved.tool == tool
    assert not evolved.pokemon_state.temporary_attack_lock
    assert not evolved.special_conditions
    assert [card.instance_id for card in first.state.stack("active").cards] == ["bulba", "ivy"]
    assert first.ledger.instance("ivy").zone == "in_play"
    assert first.ledger.instance("ivy").board_object_id == "active"
    assert ordinary_evolve(first.state, first.ledger, "active", venus) is None

    ready = begin_next_turn(first.state)
    second = ordinary_evolve(ready, first.ledger, "active", venus)
    assert second is not None
    assert second.state.board.get("active").card_name == "Mega Venusaur ex"
    assert second.state.board.get("active").print_id == "venus-print"
    assert [card.instance_id for card in second.state.stack("active").cards] == [
        "bulba", "ivy", "venus"
    ]

    devolved = devolve_top(second.state, second.ledger, "active", destination_zone="hand")
    assert devolved is not None
    assert devolved.removed_instance_id == "venus"
    assert not devolved.knockout_required
    assert devolved.state.board.get("active").card_name == "Ivysaur"
    assert devolved.state.board.get("active").print_id == "ivy-print"
    assert devolved.ledger.instance("venus").zone == "hand"
    assert devolved.ledger.instance("venus").board_object_id is None
    assert not devolved.state.stack("active").evolution_eligible
    assert ordinary_evolve(devolved.state, devolved.ledger, "active", venus) is None

    direct_ivy = make_pokemon("direct", "Ivysaur", tags=("Grass", "Stage 1"))
    direct_board = make_board(direct_ivy, (pivot,))
    direct_state = make_evolution_state(
        direct_board,
        (
            PokemonStack("direct", (StackCard(
                "direct-ivy", "Ivysaur", 1, 110, "Bulbasaur",
                frozenset({"Grass", "Stage 1"}),
            ),)),
            PokemonStack("pivot", (pivot_card,)),
        ),
    )
    direct_ledger = ledger(
        CardInstance(
            "direct-ivy", "ivy-class", "Ivysaur", "in_play", board_object_id="direct"
        ),
        CardInstance(
            "pivot-card", "pivot-class", "Pivot", "in_play", board_object_id="pivot"
        ),
    )
    validate_ledger_binding(direct_state, direct_ledger)
    assert devolve_top(
        direct_state, direct_ledger, "direct", destination_zone="hand"
    ) is None

    candy_active = make_pokemon(
        "candy", "Mega Venusaur ex", tags=("Grass", "Stage 2", "MEGA", "ex"),
        damage_counters=9,
    )
    candy_pivot = make_pokemon("candy-pivot", "Pivot", tags=("Basic",))
    candy_board = make_board(candy_active, (candy_pivot,))
    candy_state = make_evolution_state(
        candy_board,
        (
            PokemonStack("candy", (bulba, venus)),
            PokemonStack("candy-pivot", (
                StackCard("candy-pivot-card", "Pivot", 0, 100, tags=frozenset({"Basic"})),
            )),
        ),
    )
    candy_ledger = ledger(
        CardInstance(
            "bulba", "bulba-class", "Bulbasaur", "in_play", board_object_id="candy"
        ),
        CardInstance(
            "candy-pivot-card", "pivot-class", "Pivot",
            "in_play", board_object_id="candy-pivot",
        ),
        CardInstance(
            "venus", "venus-class", "Mega Venusaur ex", "in_play", board_object_id="candy"
        ),
    )
    validate_ledger_binding(candy_state, candy_ledger)
    candy_devolved = devolve_top(
        candy_state, candy_ledger, "candy", destination_zone="deck"
    )
    assert candy_devolved is not None and candy_devolved.knockout_required
    assert candy_devolved.state.board.get("candy").card_name == "Bulbasaur"
    assert candy_devolved.state.board.get("candy").print_id == "base-print"
    assert candy_devolved.ledger.instance("venus").zone == "deck"
    assert candy_devolved.ledger.instance("venus").board_object_id is None

    print("evolution stack binding regressions passed")


if __name__ == "__main__":
    main()
