"""Show why optional attack damage can worsen a real Expanded Prize outcome."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from board_object_kernel import make_board, make_pokemon
from build_expanded_legality_baseline import classify_effective_legality
from damage_board_bridge import apply_attack_damage
from damage_calculation_kernel import AttackDamage, AttackDamageMode, DamageContext
from damage_reaction_kernel import (
    DamageReaction, DamageReactionKind, resolve_damage_reactions,
)
from post_knockout_game_resolution import (
    Outcome, resolve_prize_and_board_loss_conditions,
)


def load_print(card_id: str) -> dict:
    set_id = card_id.split("-")[0]
    cards = json.loads(
        (ROOT / "resources" / "cards" / "en" / f"{set_id}.json")
        .read_text(encoding="utf-8")
    )
    result = next(row for row in cards if row["id"] == card_id)
    assert classify_effective_legality(result)[0] == "Legal"
    sets = json.loads((ROOT / "resources" / "sets" / "en.json").read_text(encoding="utf-8"))
    row = next(entry for entry in sets if entry["id"] == set_id)
    assert row["legalities"]["expanded"] == "Legal"
    return result


def card_parameters() -> tuple[int, int, int, int, int]:
    cetitan = load_print("sv10-65")
    zamazenta = load_print("sv10-146")
    crushing = next(a for a in cetitan["attacks"] if a["name"] == "Crushing Press")
    strong_bash = next(a for a in zamazenta["attacks"] if a["name"] == "Strong Bash")

    assert cetitan["name"] == "Cetitan ex"
    assert zamazenta["name"] == "Zamazenta"
    assert any("Pokémon ex rule" in rule for rule in cetitan["rules"])
    assert not zamazenta.get("rules")
    assert cetitan["types"] == ["Water"]
    assert zamazenta["weaknesses"] == [{"type": "Fire", "value": "×2"}]
    assert zamazenta["resistances"] == [{"type": "Grass", "value": "-30"}]
    assert crushing["text"].startswith("You may discard a Stadium in play.")
    assert "if this Pokémon is damaged by an attack" in strong_bash["text"]
    assert "equal to the damage done to this Pokémon" in strong_bash["text"]
    assert "even if this Pokémon is Knocked Out" in strong_bash["text"]

    base = int(re.match(r"\d+", crushing["damage"]).group())
    more = int(re.search(r"does (\d+) more damage", crushing["text"]).group(1))
    return int(cetitan["hp"]), int(zamazenta["hp"]), base, more, 150


def outcome_for_choice(
    cetitan_hp: int, zamazenta_hp: int, base: int,
    bonus: int, initial_cetitan_damage: int,
    *, discard_stadium: bool,
) -> dict:
    attacker = make_board(
        make_pokemon(
            "cetitan", "Cetitan ex", print_id="sv10-65",
            damage_counters=initial_cetitan_damage // 10,
        ),
        bench=(make_pokemon("a-backup", "Player A backup"),),
    )
    defender = make_board(
        make_pokemon("zamazenta", "Zamazenta", print_id="sv10-146"),
        bench=(make_pokemon("b-backup", "Player B backup"),),
    )
    context = DamageContext(
        attack=AttackDamage(
            base,
            mode=AttackDamageMode.PLUS,
            modifier=bonus if discard_stadium else 0,
        ),
    )
    after_damage, damage = apply_attack_damage(defender, "zamazenta", context)
    reacted = resolve_damage_reactions(
        attacker,
        after_damage,
        damage,
        reactions=(DamageReaction(DamageReactionKind.MIRROR_FINAL_DAMAGE),),
        attacker_hp_by_object_id={"cetitan": cetitan_hp, "a-backup": 100},
        defender_hp_by_object_id={"zamazenta": zamazenta_hp, "b-backup": 100},
    )

    attacker_ko = "cetitan" in reacted.attacker_knocked_out_ids
    defender_ko = "zamazenta" in reacted.defender_knocked_out_ids

    # One Prize for a non-rule-box Zamazenta, two for a Pokémon ex Cetitan.
    # Each player has a surviving Benched Pokémon; the pre-attack Prize
    # counts are A=1, B=2, so these awards may resolve the game.
    prizes_a = 1 - int(defender_ko)
    prizes_b = 2 - 2 * int(attacker_ko)
    game = resolve_prize_and_board_loss_conditions(
        player_ids=("A", "B"),
        prizes_remaining={"A": prizes_a, "B": prizes_b},
        pokemon_in_play={
            "A": 2 - int(attacker_ko),
            "B": 2 - int(defender_ko),
        },
    )
    return {
        "discard_stadium": discard_stadium,
        "damage_to_zamazenta": damage.final_damage,
        "reflected_counters": reacted.counters_placed_on_attacker,
        "cetitan_damage_after": (
            reacted.attacker_board.get("cetitan").damage_counters * 10
        ),
        "cetitan_ko": attacker_ko,
        "zamazenta_ko": defender_ko,
        "prizes_remaining": {"A": prizes_a, "B": prizes_b},
        "player_a_outcome": game.outcome("A").value,
    }


def main() -> None:
    cetitan_hp, zamazenta_hp, base, bonus, starting_damage = card_parameters()

    no_boost = outcome_for_choice(
        cetitan_hp, zamazenta_hp, base, bonus, starting_damage,
        discard_stadium=False,
    )
    boosted = outcome_for_choice(
        cetitan_hp, zamazenta_hp, base, bonus, starting_damage,
        discard_stadium=True,
    )

    assert (cetitan_hp, zamazenta_hp, base, bonus, starting_damage) == (
        300, 130, 140, 140, 150,
    )
    assert no_boost["damage_to_zamazenta"] == 140
    assert boosted["damage_to_zamazenta"] == 280
    assert no_boost["reflected_counters"] == 14
    assert boosted["reflected_counters"] == 28
    assert no_boost["cetitan_damage_after"] == 290
    assert boosted["cetitan_damage_after"] == 430
    assert not no_boost["cetitan_ko"]
    assert boosted["cetitan_ko"]
    assert no_boost["zamazenta_ko"] and boosted["zamazenta_ko"]
    assert no_boost["player_a_outcome"] == Outcome.WIN.value
    assert boosted["player_a_outcome"] == Outcome.TIE.value

    # Both routes KO the defender, while only the boosted route KOs
    # Cetitan, exactly if base < HP_remaining <= base + bonus.
    critical_damage = [
        already_damaged
        for already_damaged in range(0, cetitan_hp, 10)
        if already_damaged + base < cetitan_hp
        <= already_damaged + base + bonus
    ]
    assert critical_damage == list(range(20, 160, 10))
    assert len(critical_damage) == 14

    print(json.dumps({
        "prints": ["sv10-65", "sv10-146"],
        "no_boost": no_boost,
        "boosted": boosted,
        "dangerous_starting_damage": critical_damage,
        "status": "PASS",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
