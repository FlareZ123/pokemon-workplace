"""Aichi Regidrago bonus-turn counterplay against a pre-staged Mimikyu.

The canonical copy kernel verifies legal nested attack identity and GX-use
state. The source-card HP comparison verifies an unprotected attack target's
lethal damage. This does not model the full board damage/KO/prize transition.
"""

from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from attack_copy_kernel import (  # noqa: E402
    AttackDef, CopySelector, PokemonRef, State,
    TurnBoundaryEffect, choose_exact, resolve_attack,
)

APEX = "regidrago:apex-dragon"
TIMELESS = "dialga:timeless-gx"
TRIFROST = "kyurem:trifrost"


def card(set_id: str, ident: str) -> dict:
    rows = json.loads(
        (ROOT / "resources" / "cards" / "en" / f"{set_id}.json")
        .read_text(encoding="utf-8")
    )
    return next(row for row in rows if row["id"] == ident)


def main() -> None:
    regidrago = card("swsh12", "swsh12-136")
    dialga = card("sm5", "sm5-100")
    kyurem = card("sv6pt5", "sv6pt5-47")
    mimikyu = card("sm2", "sm2-58")
    assert regidrago["name"] == "Regidrago VSTAR"
    assert regidrago["retreatCost"] == ["Colorless"] * 3
    assert kyurem["types"] == ["Water"]
    # Kyurem is a Dragon-type Pokémon in the canonical print, check below.
    assert "Dragon" in kyurem["types"]
    assert mimikyu["hp"] == "70"
    assert mimikyu["subtypes"] == ["Basic"]
    assert len([a for a in mimikyu["attacks"] if a["name"] == "Copycat"]) == 1
    trifrost = next(a for a in kyurem["attacks"] if a["name"] == "Trifrost")
    assert "110 damage to 3 of your opponent's Pokémon" in trifrost["text"]
    assert "Discard all Energy from this Pokémon" in trifrost["text"]
    assert int(mimikyu["hp"]) < 110
    assert any(a["name"] == "Timeless-GX" for a in dialga["attacks"])

    fixture = json.loads(
        (ROOT / "results" / "regidrago_budew_promotion_baselines"
         / "aichi9_counts.json").read_text(encoding="utf-8")
    )
    assert len(fixture["decklists"]) == 9
    assert all(row["kyurem_sv6pt5_47"] == 1
               for row in fixture["decklists"])

    defs = {
        APEX: AttackDef(
            APEX, "Apex Dragon",
            copy_selector=CopySelector(
                source="own_discard", required_type="Dragon"
            )
        ),
        TIMELESS: AttackDef(
            TIMELESS, "Timeless-GX", is_gx=True,
            turn_boundary_effect=TurnBoundaryEffect(
                take_another_turn=True, skip_pokemon_checkup=True
            ),
        ),
        TRIFROST: AttackDef(TRIFROST, "Trifrost"),
    }
    state = State(pokemon=(
        PokemonRef("p1-drago", "Regidrago VSTAR", "P1",
                   "active", types=("Dragon",), attacks=(APEX,)),
        PokemonRef("p1-dialga", "Dialga-GX", "P1",
                   "discard", types=("Dragon",), attacks=(TIMELESS,)),
        PokemonRef("p1-kyurem", "Kyurem", "P1",
                   "discard", types=("Dragon",), attacks=(TRIFROST,)),
        PokemonRef("p2-rider", "Shadow Rider Calyrex VMAX", "P2",
                   "active", types=("Psychic",)),
        PokemonRef("p2-mimikyu", "Mimikyu", "P2",
                   "bench", types=("Psychic",)),
    ))
    first = resolve_attack(
        actor_player="P1", actor_card_id="p1-drago",
        declared_attack_id=APEX, attacks=defs, state=state,
        choose=choose_exact((TIMELESS,)),
    )
    assert first.body_chain == (APEX, TIMELESS)
    assert first.state.last_attack_for("P1") == APEX
    assert first.state.gx_used_by == frozenset({"P1"})
    assert first.state.pending_turn_boundary is not None
    assert first.state.pending_turn_boundary.take_another_turn

    bonus_state = replace(first.state, pending_turn_boundary=None)
    second = resolve_attack(
        actor_player="P1", actor_card_id="p1-drago",
        declared_attack_id=APEX, attacks=defs, state=bonus_state,
        choose=choose_exact((TRIFROST,)),
    )
    assert second.body_chain == (APEX, TRIFROST)
    assert second.state.last_attack_for("P1") == APEX
    assert second.state.gx_used_by == frozenset({"P1"})
    assert all("p2-mimikyu" != p.card_id or p.zone == "bench"
               for p in second.state.pokemon)

    print(json.dumps({
        "published_regidrago_lists_with_kyurem": 9,
        "shadow_rider_champion_mimikyu_copies": 1,
        "mimikyu_hp": int(mimikyu["hp"]),
        "trifrost_damage_to_unprotected_mimikyu": 110,
        "unprotected_mimikyu_is_knocked_out_by_trifrost": True,
        "declared_attack_history_after_bonus_trifrost":
            second.state.last_attack_for("P1"),
        "source_attack_body_after_bonus_trifrost":
            list(second.body_chain),
        "attacking_regidrago_must_discard_all_attached_energy": True,
        "limitations": "Full damage/KO/prize transitions and target protections not executed.",
    }, indent=2))


if __name__ == "__main__":
    main()
