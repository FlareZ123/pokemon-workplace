"""Verify order-dependent Energy denial from Turtonator and Handheld Fan."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from attack_copy_kernel import (
    AttackDef, CopySelector, PokemonRef, State, choose_exact, resolve_attack,
)
from attack_copy_physical_ko_bridge import (
    PhysicalBoardEventProgram, replay_copy_attack_physical_board,
)
from board_position_state import AttachmentKind, BoardPokemon, PokemonCard, make_state
from damage_calculation_kernel import AttackDamage, DamageContext
from identity_materialization import (
    IdentityLedger, assert_conserved, materialize, put_in_play_instance,
)
from multicopy_zone_state import ZoneCountState
from physical_copy_damage_reaction_bridge import (
    prepare_reacted_physical_knockouts,
    resolve_physical_copy_damage_reactions,
)
from physical_energy_backlash_reactions import (
    EnergyReactionKind, eligible_printed_energy_backlash,
)
from physical_energy_reaction_orderings import enumerate_energy_reaction_orders
from stack_knockout_conservation import StackBoardMaterialState, attach_from_hand

HAUGHTY = "persian:haughty-order"
TIMELESS = "dialga:timeless-gx"
BODY = "body:timeless-gx"


def copied_attack():
    persian = json.loads(
        (ROOT / "resources" / "cards" / "en" / "sv10.json")
        .read_text(encoding="utf-8")
    )
    print_row = next(x for x in persian if x["id"] == "sv10-150")
    haughty = next(x for x in print_row["attacks"] if x["name"] == "Haughty Order")
    assert haughty["cost"] == ["Colorless", "Colorless"]
    double_colorless = json.loads(
        (ROOT / "resources" / "cards" / "en" / "bw11.json")
        .read_text(encoding="utf-8")
    )
    dce_print = next(x for x in double_colorless if x["id"] == "bw11-113")
    assert dce_print["name"] == "Double Colorless Energy"
    assert dce_print["legalities"]["expanded"] == "Legal"
    assert "provides ColorlessColorless Energy" in dce_print["rules"][0]

    attacks = {
        HAUGHTY: AttackDef(
            HAUGHTY, "Haughty Order",
            copy_selector=CopySelector("opponent_revealed"),
            pre_event="reveal_top_10", post_event="shuffle_revealed",
            energy_cost=("Colorless", "Colorless"),
        ),
        TIMELESS: AttackDef(
            TIMELESS, "Timeless-GX", is_gx=True, effect_label=BODY,
        ),
    }
    return resolve_attack(
        actor_player="P1", actor_card_id="a-active-card",
        declared_attack_id=HAUGHTY, attacks=attacks,
        state=State(
            pokemon=(
                PokemonRef(
                    "dialga-revealed", "Dialga-GX", "P2", "revealed",
                    attacks=(TIMELESS,),
                ),
            ),
        ),
        choose=choose_exact((TIMELESS,)),
    )


def make_player(prefix: str, active_name: str, attached_name: str):
    counts = {
        (f"{prefix}-active-class", "hand"): 1,
        (f"{prefix}-bench-class", "hand"): 1,
        (f"{prefix}-attached-class", "hand"): 1,
    }
    initial = IdentityLedger(ZoneCountState.from_mapping(counts))
    ledger = initial
    for role, name in (
        ("active", active_name), ("bench", f"{prefix} backup"),
    ):
        instance = f"{prefix}-{role}-card"
        ledger = materialize(
            ledger, card_class=f"{prefix}-{role}-class",
            card_name=name, source_zone="hand", instance_id=instance,
        )
        ledger = put_in_play_instance(ledger, instance, f"{prefix}-{role}")

    board = make_state(
        (
            BoardPokemon(
                f"{prefix}-active",
                (PokemonCard(f"{prefix}-active-card", active_name),),
                retreat_cost=1,
            ),
            BoardPokemon(
                f"{prefix}-bench",
                (PokemonCard(f"{prefix}-bench-card", f"{prefix} backup"),),
                retreat_cost=1,
            ),
        ),
        active_id=f"{prefix}-active",
    )
    state = StackBoardMaterialState(ledger, board)
    attachment = attach_from_hand(
        state, pokemon_id=f"{prefix}-active",
        card_class=f"{prefix}-attached-class",
        instance_id=f"{prefix}-attached",
        card_name=attached_name,
        kind=(
            AttachmentKind.TOOL
            if prefix == "b" else AttachmentKind.ENERGY
        ),
        retreat_units=2 if prefix == "a" else 0,
    )
    assert attachment is not None
    assert_conserved(initial, attachment.ledger)
    return initial, attachment


def test_owner_order_choice_changes_energy_placement():
    initial_a, a = make_player(
        "a", "Team Rocket's Persian ex", "Double Colorless Energy",
    )
    initial_b, b = make_player(
        "b", "Turtonator", "Handheld Fan",
    )
    copy = copied_attack()
    replay = replay_copy_attack_physical_board(
        copy, b,
        event_programs={
            BODY: PhysicalBoardEventProgram(
                "b-active", DamageContext(attack=AttackDamage(150)),
            ),
        },
        hp_by_pokemon_id={"b-active": 120, "b-bench": 100},
    )
    assert replay.knocked_out_ids == ("b-active",)

    ability = eligible_printed_energy_backlash(
        replay, resources=ROOT / "resources", body_event=BODY,
        damaged_pokemon_id="b-active", source_print_id="me3-17",
        source_instance_id=None, ability_is_enabled=True,
        from_opponents_pokemon=True,
    )
    tool = eligible_printed_energy_backlash(
        replay, resources=ROOT / "resources", body_event=BODY,
        damaged_pokemon_id="b-active", source_print_id="sv6-150",
        source_instance_id="b-attached", ability_is_enabled=True,
        from_opponents_pokemon=True,
    )
    assert len(ability) == len(tool) == 1
    assert ability[0].kind is EnergyReactionKind.DISCARD
    assert tool[0].kind is EnergyReactionKind.MOVE_TO_BENCH

    base = resolve_physical_copy_damage_reactions(
        replay, a, body_event=BODY, damaged_pokemon_id="b-active",
        attacking_pokemon_id="a-active", reactions=(),
        attacker_hp_by_pokemon_id={"a-active": 220, "a-bench": 100},
        defender_hp_by_pokemon_id={"b-active": 120, "b-bench": 100},
    )

    def choose(state, reaction):
        actor = state.attacker_state.board.get("a-active")
        energy = [
            card.card_id for card in actor.attachments
            if card.kind is AttachmentKind.ENERGY
        ]
        destination = "a-bench" if reaction.kind is EnergyReactionKind.MOVE_TO_BENCH else None
        return (energy[0] if energy else None, destination)

    orderings = enumerate_energy_reaction_orders(
        base, (ability[0], tool[0]), choose=choose,
    )
    assert len(orderings) == 2
    by_order = {
        tuple(step.kind for step in row.ordered_reactions): row
        for row in orderings
    }
    discard_then_move = by_order[(
        EnergyReactionKind.DISCARD, EnergyReactionKind.MOVE_TO_BENCH,
    )]
    move_then_discard = by_order[(
        EnergyReactionKind.MOVE_TO_BENCH, EnergyReactionKind.DISCARD,
    )]

    assert tuple(item.applied for item in discard_then_move.step_outcomes) == (True, False)
    assert discard_then_move.final.attacker_state.ledger.exchangeable.count(
        "a-attached-class", "discard",
    ) == 1
    assert discard_then_move.final.attacker_state.board.get(
        "a-bench",
    ).attachments == ()

    assert tuple(item.applied for item in move_then_discard.step_outcomes) == (True, False)
    assert move_then_discard.final.attacker_state.ledger.instance(
        "a-attached",
    ).attached_to == "a-bench"
    assert tuple(
        card.card_id
        for card in move_then_discard.final.attacker_state.board.get(
            "a-bench",
        ).attachments
    ) == ("a-attached",)
    assert move_then_discard.final.attacker_state.ledger.exchangeable.count(
        "a-attached-class", "discard",
    ) == 0

    for outcome in orderings:
        assert outcome.final.defender_knocked_out_ids == ("b-active",)
        assert_conserved(initial_a, outcome.final.attacker_state.ledger)
        assert_conserved(initial_b, outcome.final.defender_state.ledger)
        pa, pb = prepare_reacted_physical_knockouts(outcome.final)
        assert pa is None and pb is not None
        assert pb.state.board.get("b-active").attachments[0].card_id == "b-attached"

    print(json.dumps({
        "source_reactions": [a.source_print_id for a in (ability[0], tool[0])],
        "outcomes": [
            {
                "order": [r.kind.value for r in row.ordered_reactions],
                "applied": [step.applied for step in row.step_outcomes],
                "attacker_dce_discard": row.final.attacker_state.ledger.exchangeable.count(
                    "a-attached-class", "discard",
                ),
                "bench_has_dce": any(
                    card.card_id == "a-attached"
                    for card in row.final.attacker_state.board.get("a-bench").attachments
                ),
            }
            for row in orderings
        ],
    }, indent=2))


def main():
    test_owner_order_choice_changes_energy_placement()
    print("Energy reaction ordering and physical noncommutativity: PASS")


if __name__ == "__main__":
    main()
