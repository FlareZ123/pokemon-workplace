"""Correct in-play Pokémon V-UNION classification across Retreat code paths.

Appendix 7 of the official Pokémon Trading Card Game Rules identifies an
assembled Pokémon V-UNION in play as both Pokémon V and a Rule Box Pokémon.
An individual out-of-play piece has different characteristics and should not
be materialized as an in-play BoardPokemon.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from board_object_kernel import EnergyAttachment, make_board, make_pokemon
from retreat_conditional_self_free_cost import derive_conditional_self_free_cost
from retreat_cost_semantics import effective_retreat_cost
from retreat_dynamic_energy_units import (
    current_retreat_units, holder_has_rule_box, holder_is_evolution,
    holder_is_pokemon_v, holder_is_stage2,
)
from retreat_environment_modifiers import derive_environment_retreat_modifiers


def source_audit() -> None:
    records = json.loads(
        (ROOT / "resources" / "cards" / "en" / "swshp.json")
        .read_text(encoding="utf-8")
    )
    if isinstance(records, dict):
        records = records["data"]
    piece = next(c for c in records if c["id"] == "swshp-SWSH159")
    assert piece["name"] == "Mewtwo V-UNION"
    assert piece["subtypes"] == ["V-UNION"]
    union_pieces = [c for c in records if "V-UNION" in c.get("subtypes", ())]
    assert len(union_pieces) == 24
    assert len({c["name"] for c in union_pieces}) == 5


def state_classification() -> None:
    for tag in ("V-UNION", "Pokemon V-UNION", "Pokémon V-UNION"):
        tags = frozenset({tag})
        assert holder_is_pokemon_v(tags)
        assert holder_has_rule_box(tags)
        assert not holder_is_evolution(tags)
        assert not holder_is_stage2(tags)

        energy = EnergyAttachment(
            "twin", "Twin Energy", ("C", "C"), "swsh2-174",
        )
        assert current_retreat_units(
            energy, holder_tags=tags, stage2_in_play=0,
        ) == ("C",)

        enemy = make_board(
            make_pokemon("enemy", "Mewtwo V-UNION", tags=tags),
        )
        wimpod = make_pokemon(
            "wimpod", "Wimpod", print_id="pgo-25",
        )
        assert derive_conditional_self_free_cost(wimpod, enemy) is not None
        mods = derive_environment_retreat_modifiers(
            make_board(wimpod), enemy,
            stadium_print_id="swsh2-160",  # +2 cost from Galar Mine
        )
        assert effective_retreat_cost(1, mods) == 0

    assert current_retreat_units(
        EnergyAttachment("twin", "Twin Energy", ("C", "C"), "swsh2-174"),
        holder_tags=frozenset({"Basic"}), stage2_in_play=0,
    ) == ("C", "C")

    not_pokemon_v = frozenset({"Pokemon-GX"})
    assert not holder_is_pokemon_v(not_pokemon_v)
    wimpod = make_pokemon("wimpod", "Wimpod", print_id="pgo-25")
    assert derive_conditional_self_free_cost(
        wimpod, make_board(make_pokemon("enemy", "GX", tags=not_pokemon_v)),
    ) is None


def main() -> None:
    source_audit()
    state_classification()
    print("Assembled in-play V-UNION Pokémon V and Rule Box classification: PASS")
    print({"v_union_pieces_checked": 24, "distinct_pokemon": 5,
           "twin_energy_on_v_union_units": 1,
           "wimpod_punk_out_retreat_cost": 0})


if __name__ == "__main__":
    main()
