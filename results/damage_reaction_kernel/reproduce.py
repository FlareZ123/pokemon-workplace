from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from board_object_kernel import make_board, make_pokemon  # noqa: E402
from damage_board_bridge import apply_attack_damage  # noqa: E402
from damage_calculation_kernel import AttackDamage, DamageContext  # noqa: E402
from damage_reaction_kernel import (  # noqa: E402
    DamageReaction,
    DamageReactionKind,
    resolve_damage_reactions,
)


def card(set_id: str, card_id: str) -> dict:
    rows = json.loads(
        (ROOT / "resources" / "cards" / "en" / f"{set_id}.json").read_text(
            encoding="utf-8"
        )
    )
    return next(row for row in rows if row["id"] == card_id)


def main() -> None:
    zamazenta = card("sv10", "sv10-146")
    strong_bash = next(
        attack for attack in zamazenta["attacks"]
        if attack["name"] == "Strong Bash"
    )
    assert "if this Pokémon is damaged by an attack" in strong_bash["text"]
    assert "equal to the damage done to this Pokémon" in strong_bash["text"]

    spiky = card("sv9", "sv9-159")
    assert "is damaged by an attack" in spiky["rules"][0]
    assert "put 2 damage counters on the Attacking Pokémon" in spiky["rules"][0]

    attacker = make_board(make_pokemon("attacker", "Attacker"))
    defender = make_board(make_pokemon("defender", "Zamazenta"))

    after_damage, result = apply_attack_damage(
        defender,
        "defender",
        DamageContext(attack=AttackDamage(150)),
    )
    mirror = resolve_damage_reactions(
        attacker,
        after_damage,
        result,
        reactions=(
            DamageReaction(DamageReactionKind.MIRROR_FINAL_DAMAGE),
        ),
        attacker_hp_by_object_id={"attacker": 150},
        defender_hp_by_object_id={"defender": 130},
    )
    assert mirror.triggered
    assert mirror.counters_placed_on_attacker == 15
    assert mirror.attacker_knocked_out_ids == ("attacker",)
    assert mirror.defender_knocked_out_ids == ("defender",)

    survivor = resolve_damage_reactions(
        attacker,
        after_damage,
        result,
        reactions=(
            DamageReaction(DamageReactionKind.MIRROR_FINAL_DAMAGE),
        ),
        attacker_hp_by_object_id={"attacker": 160},
        defender_hp_by_object_id={"defender": 130},
    )
    assert survivor.attacker_knocked_out_ids == ()
    assert survivor.defender_knocked_out_ids == ("defender",)

    prevented_defender, prevented_result = apply_attack_damage(
        defender,
        "defender",
        DamageContext(
            attack=AttackDamage(150),
            prevent_all_damage=True,
        ),
    )
    prevented = resolve_damage_reactions(
        attacker,
        prevented_defender,
        prevented_result,
        reactions=(
            DamageReaction(DamageReactionKind.MIRROR_FINAL_DAMAGE),
        ),
        attacker_hp_by_object_id={"attacker": 10},
        defender_hp_by_object_id={"defender": 130},
    )
    assert not prevented.triggered
    assert prevented.counters_placed_on_attacker == 0
    assert prevented.attacker_knocked_out_ids == ()
    assert prevented.defender_knocked_out_ids == ()

    two_spiky = resolve_damage_reactions(
        attacker,
        after_damage,
        result,
        reactions=(
            DamageReaction(DamageReactionKind.FIXED_COUNTERS, 2),
            DamageReaction(DamageReactionKind.FIXED_COUNTERS, 2),
        ),
        attacker_hp_by_object_id={"attacker": 40},
        defender_hp_by_object_id={"defender": 130},
    )
    assert two_spiky.counters_placed_on_attacker == 4
    assert two_spiky.attacker_knocked_out_ids == ("attacker",)
    assert two_spiky.defender_knocked_out_ids == ("defender",)

    print(
        {
            "mirror_simultaneous_ko": (
                mirror.attacker_knocked_out_ids,
                mirror.defender_knocked_out_ids,
            ),
            "prevented_triggered": prevented.triggered,
            "two_spiky_counters": two_spiky.counters_placed_on_attacker,
        }
    )


if __name__ == "__main__":
    main()
