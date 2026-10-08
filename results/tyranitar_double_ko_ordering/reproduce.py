"""Reproduce a source-authorized double Knock Out from Tyranitar-GX Dusty Ruckus.

Two competing KO replacement pairs are active:
  Aegislash Durable Blade vs Tyranitar-GX Lost Out (Active KO)
  Huntail Diver's Catch vs Tyranitar-GX Lost Out (Benched Lapras KO)

Compares two representations of Lost Out: one per Knocked Out target versus
one globally grouped effect. No conclusion is drawn about which granularity
is mandated by official card-text timing rules.
"""

from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from board_position_state import (
    AttachmentKind, BoardPokemon, PokemonCard, make_state,
)
from build_expanded_legality_baseline import classify_effective_legality
from identity_materialization import (
    IdentityLedger, assert_conserved, materialize, put_in_play_instance,
)
from ko_order_outcome_space import ko_order_outcomes
from ko_order_signature_projection import project_with_zone_signatures
from ko_order_terminal_projection import project_terminal_outcomes
from ko_redirection_authorized_order import (
    AuthorizedOrderStatus, OrderingPlayers, authorize_and_resolve_order,
)
from ko_trigger_order_authority import (
    ADVANCED_RULEBOOK_3_4, TPCI_FEB_2026,
    OrderingContext, TimingWindow, TriggerKind,
)
from knockout_redirection_ordering import resolved_route_map
from knockout_redirection_routes import destinations_for_redirection
from knockout_redirection_taxonomy import (
    ALL_TO_LOST, ATTACHED_ENERGY_TO_HAND, SELF_TO_HAND,
)
from knockout_zone_routing import discard_pending_with_zone_routes
from multicopy_zone_state import ZoneCountState
from simultaneous_knockout_conservation import prepare_knock_out_batch
from stack_knockout_conservation import StackBoardMaterialState, attach_from_hand


def card(set_id, card_id):
    cards = json.loads(
        (ROOT / "resources" / "cards" / "en" / f"{set_id}.json").read_text(
            encoding="utf-8"
        )
    )
    return next(item for item in cards if item["id"] == card_id)


def validate_attack_window():
    tyranitar = card("sm8", "sm8-121")
    aegislash = card("sm11", "sm11-95")
    lapras = card("bw4", "bw4-25")
    huntail = card("sv10", "sv10-55")
    for item in (tyranitar, aegislash, lapras, huntail):
        assert classify_effective_legality(item)[0] == "Legal"

    assert tyranitar["types"] == ["Darkness"]
    dusty = next(
        attack for attack in tyranitar["attacks"]
        if attack["name"] == "Dusty Ruckus"
    )
    assert dusty["damage"] == "130"
    assert "Benched Basic Pokémon" in dusty["text"]
    lost_out = next(
        ability for ability in tyranitar["abilities"]
        if ability["name"] == "Lost Out"
    )
    assert "all cards attached to it in the Lost Zone" in lost_out["text"]

    assert aegislash["hp"] == "130"
    assert "Stage 2" in aegislash["subtypes"]
    assert {"type": "Darkness", "value": "×2"} in aegislash["weaknesses"]
    durable = next(
        ability for ability in aegislash["abilities"]
        if ability["name"] == "Durable Blade"
    )
    assert "instead of the discard pile" in durable["text"]

    assert lapras["hp"] == "100" and "Basic" in lapras["subtypes"]
    assert lapras["types"] == ["Water"]
    assert huntail["hp"] == "110" and "Stage 1" in huntail["subtypes"]
    assert huntail["types"] == ["Water"]
    catch = next(
        ability for ability in huntail["abilities"]
        if ability["name"] == "Diver's Catch"
    )
    assert "all Basic Water Energy attached" in catch["text"]

    # Already-damaged Lapras has 70 damage; Aegislash starts at 0 damage.
    # 130 * 2 Weakness knocks out Aegislash, and 70 + 30 Bench splash
    # Knocks Out Lapras. Huntail is an Evolution and avoids Basic-only spread.
    assert int(dusty["damage"]) * 2 >= int(aegislash["hp"])
    assert 70 + 30 >= int(lapras["hp"])
    assert "Basic" not in huntail["subtypes"]


def initial_materialized_state():
    counts = {
        (card_class, "hand"): 1
        for card_class in (
            "honedge", "doublade", "aegislash", "lapras",
            "clamperl", "huntail", "muscle-band", "dce",
        )
    }
    counts[("basic-water", "hand")] = 2
    initial = IdentityLedger(ZoneCountState.from_mapping(counts))
    ledger = initial
    for cls, name, instance, holder in (
        ("honedge", "Honedge", "honedge-a", "a"),
        ("doublade", "Doublade", "doublade-a", "a"),
        ("aegislash", "Aegislash", "aegislash-a", "a"),
        ("lapras", "Lapras", "lapras-b", "b"),
        ("clamperl", "Clamperl", "clamperl-c", "c"),
        ("huntail", "Huntail", "huntail-c", "c"),
    ):
        ledger = materialize(
            ledger, card_class=cls, card_name=name,
            source_zone="hand", instance_id=instance,
        )
        ledger = put_in_play_instance(ledger, instance, holder)

    board = make_state(
        (
            BoardPokemon(
                "a",
                (
                    PokemonCard("honedge-a", "Honedge"),
                    PokemonCard("doublade-a", "Doublade", evolves_from="Honedge"),
                    PokemonCard("aegislash-a", "Aegislash", evolves_from="Doublade"),
                ),
                retreat_cost=3,
            ),
            BoardPokemon(
                "b", (PokemonCard("lapras-b", "Lapras"),),
                retreat_cost=2,
                damage_counters=7,
            ),
            BoardPokemon(
                "c", (
                    PokemonCard("clamperl-c", "Clamperl"),
                    PokemonCard("huntail-c", "Huntail", evolves_from="Clamperl"),
                ),
                retreat_cost=1,
            ),
        ),
        active_id="a",
    )
    state = StackBoardMaterialState(ledger, board)
    for instance in ("water-1", "water-2"):
        state = attach_from_hand(
            state, pokemon_id="b", card_class="basic-water",
            instance_id=instance, card_name="Basic Water Energy",
            kind=AttachmentKind.ENERGY, retreat_units=1,
        )
        assert state is not None
    state = attach_from_hand(
        state, pokemon_id="b", card_class="dce", instance_id="dce-b",
        card_name="Double Colorless Energy",
        kind=AttachmentKind.ENERGY, retreat_units=2,
    )
    assert state is not None
    state = attach_from_hand(
        state, pokemon_id="a", card_class="muscle-band",
        instance_id="band-a", card_name="Muscle Band",
        kind=AttachmentKind.TOOL,
    )
    assert state is not None
    assert_conserved(initial, state.ledger)

    pending = prepare_knock_out_batch(state, ("a", "b"))
    assert pending is not None
    assert set(pending.knocked_out_ids) == {"a", "b"}
    return initial, pending


def redirection(pending, pokemon_id, signature, selected=()):
    routes = destinations_for_redirection(
        pending, pokemon_id=pokemon_id,
        routing_signature=signature, selected_energy_ids=selected,
    )
    assert routes is not None
    return routes


def programs_for(pending):
    durable = redirection(pending, "a", SELF_TO_HAND)
    lost_a = redirection(pending, "a", ALL_TO_LOST)
    lost_b = redirection(pending, "b", ALL_TO_LOST)
    recovered = redirection(
        pending, "b", ATTACHED_ENERGY_TO_HAND, ("water-1", "water-2")
    )
    grouped = {
        "durable-blade-a": durable,
        "lost-out-all": {**lost_a, **lost_b},
        "divers-catch-b": recovered,
    }
    per_target = {
        "durable-blade-a": durable,
        "lost-out-a": lost_a,
        "lost-out-b": lost_b,
        "divers-catch-b": recovered,
    }
    return grouped, per_target


def physical_bits(state):
    counts = state.ledger.exchangeable
    aegis = "hand" if counts.count("aegislash", "hand") else "lost_zone"
    water = "hand" if counts.count("basic-water", "hand") == 2 else "lost_zone"
    return aegis, water


def main():
    validate_attack_window()
    initial, pending = initial_materialized_state()
    grouped, per_target = programs_for(pending)
    context = OrderingContext(
        timing_window=TimingWindow.DURING_TURN,
        trigger_kind=TriggerKind.POKEMON_KNOCKED_OUT,
        simultaneous_knockout_count=2,
        interaction_id="tyranitar_dusty_ruckus_double_knock_out",
    )
    roles = OrderingPlayers(
        current_player="attacker",
        knocked_out_pokemon_owner="defender",
    )
    source_ids = (ADVANCED_RULEBOOK_3_4, TPCI_FEB_2026)
    target_states = {
        ("hand", "hand"), ("hand", "lost_zone"),
        ("lost_zone", "hand"), ("lost_zone", "lost_zone"),
    }

    for representation, programs, multiplicities in (
        ("grouped", grouped, [1, 1, 2, 2]),
        ("per-target", per_target, [6, 6, 6, 6]),
    ):
        outcomes = ko_order_outcomes(programs)
        assert len(outcomes) == 4
        assert sorted(o.order_count for o in outcomes) == multiplicities
        assert sum(o.order_count for o in outcomes) == (
            6 if representation == "grouped" else 24
        )

        full = project_terminal_outcomes(pending, programs, promote_id="c")
        fast = project_with_zone_signatures(pending, programs, promote_id="c")
        assert fast.outcomes == full
        assert fast.physical_disposals == 4

        observed = set()
        for outcome in outcomes:
            choice = authorize_and_resolve_order(
                programs, outcome.witness_order, context=context,
                source_ids=source_ids, players=roles,
                submitted_by="attacker",
            )
            assert choice.status == AuthorizedOrderStatus.RESOLVED
            assert choice.chooser == "attacker"
            assert choice.resolutions is not None
            state = discard_pending_with_zone_routes(
                pending, promote_id="c",
                destinations=resolved_route_map(choice.resolutions),
            )
            assert state is not None and state.board is not None
            assert state.board.active_id == "c"
            assert [row.pokemon_id for row in state.board.pokemon] == ["c"]
            assert_conserved(initial, state.ledger)
            assert state.ledger.exchangeable.count("lapras", "lost_zone") == 1
            assert state.ledger.exchangeable.count("dce", "lost_zone") == 1
            assert state.ledger.exchangeable.count("muscle-band", "discard") + state.ledger.exchangeable.count("muscle-band", "lost_zone") == 1
            observed.add(physical_bits(state))
        assert observed == target_states

        # The defender cannot claim current-turn-player ordering authority.
        denied = authorize_and_resolve_order(
            programs, outcomes[0].witness_order, context=context,
            source_ids=source_ids, players=roles, submitted_by="defender",
        )
        assert denied.status == AuthorizedOrderStatus.UNAUTHORIZED_CHOOSER

    # Both choices of effect-instance granularity yield the same four
    # conserved physical endpoints, despite different permutation counts.
    grouped_states = {
        row.state for row in project_terminal_outcomes(
            pending, grouped, promote_id="c"
        )
    }
    per_target_states = {
        row.state for row in project_terminal_outcomes(
            pending, per_target, promote_id="c"
        )
    }
    assert grouped_states == per_target_states
    assert len(grouped_states) == 4

    print(
        "Tyranitar-GX double KO succeeded: four conserved destinations "
        "under grouped (6) and per-target (24) abstract effect orderings; "
        "v3.4 and TPCi both authorize the current attacking player"
    )


if __name__ == "__main__":
    main()
