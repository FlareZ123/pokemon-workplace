"""Source-card tests for conditional Regidrago VSTAR post-Trifrost recharge."""

from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from regidrago_post_trifrost_recharge import (  # noqa: E402
    RechargeState, find_recharge_routes, pays_apex_dragon,
)


def card(set_id: str, ident: str) -> dict:
    rows = json.loads(
        (ROOT / "resources" / "cards" / "en" / f"{set_id}.json")
        .read_text(encoding="utf-8")
    )
    return next(row for row in rows if row["id"] == ident)


def labels(s: RechargeState) -> set[str]:
    return {r.label for r in find_recharge_routes(s)}


def main() -> None:
    drago = card("swsh12", "swsh12-136")
    kyurem = card("sv6pt5", "sv6pt5-47")
    crispin = card("sv7", "sv7-133")
    raihan = card("swsh7", "swsh7-152")
    dde = card("xy6", "xy6-97")
    assert drago["types"] == ["Dragon"]
    apex = next(a for a in drago["attacks"] if a["name"] == "Apex Dragon")
    assert apex["cost"] == ["Grass", "Grass", "Fire"]
    assert "Legacy Star" == drago["abilities"][0]["name"]
    assert "top 7 cards" in drago["abilities"][0]["text"]
    assert "up to 2 cards from your discard pile" in drago["abilities"][0]["text"]
    trifrost = next(a for a in kyurem["attacks"] if a["name"] == "Trifrost")
    assert "Discard all Energy from this Pokémon" in trifrost["text"]
    assert "up to 2 Basic Energy cards of different types" in crispin["rules"][0]
    assert "put 1 of them into your hand. Attach the other" in crispin["rules"][0]
    assert "only if any of your Pokémon were Knocked Out" in raihan["rules"][0]
    assert "Attach a basic Energy card from your discard pile" in raihan["rules"][0]
    assert "If you do, search your deck for a card" in raihan["rules"][0]
    assert "provides only 2 Energy at a time" in dde["rules"][0]
    assert "only be attached to Dragon Pokémon" in dde["rules"][0]

    assert pays_apex_dragon(basic_type="Grass")
    assert pays_apex_dragon(basic_type="Fire")
    assert not pays_apex_dragon(basic_type="Grass", double_dragon_cards=0)
    assert not pays_apex_dragon(basic_type="Fire", double_dragon_cards=0)
    assert not pays_apex_dragon(basic_type="Grass", double_dragon_cards=0)

    crispy = RechargeState(
        crispin_access=True, raihan_access=False, double_dragon_hand=1,
        grass_deck=1, fire_deck=1
    )
    assert labels(crispy) == {"Crispin + held Double Dragon Energy"}
    assert labels(replace(crispy, fire_deck=0)) == set()
    assert labels(replace(crispy, double_dragon_hand=0)) == set()

    rai = RechargeState(
        crispin_access=False, raihan_access=True,
        knockout_last_opponent_turn=True,
        grass_discard=1, double_dragon_deck=1
    )
    assert labels(rai) == {"Raihan + searched Double Dragon Energy"}
    assert labels(replace(rai, knockout_last_opponent_turn=False)) == set()
    assert labels(replace(rai, grass_discard=0)) == set()
    assert labels(replace(rai, double_dragon_deck=0)) == set()

    legacy_crispin = replace(
        crispy, double_dragon_hand=0, double_dragon_discard=1
    )
    assert labels(legacy_crispin) == {
        "Crispin + Legacy Star + discarded Double Dragon Energy"
    }
    assert labels(replace(legacy_crispin, legacy_star_unused=False)) == set()

    legacy_raihan = replace(
        rai, double_dragon_deck=0, double_dragon_discard=1
    )
    assert labels(legacy_raihan) == {
        "Raihan + Legacy Star + discarded Double Dragon Energy"
    }
    assert labels(replace(legacy_raihan, legacy_star_ability_live=False)) == set()
    assert labels(replace(legacy_raihan, any_card_remaining_in_deck=False)) == set()

    both = replace(
        legacy_raihan, crispin_access=True, grass_deck=1, fire_deck=1,
    )
    assert len(labels(both)) == 2
    assert labels(replace(both, supporter_unused=False)) == set()
    assert labels(replace(both, manual_attachment_unused=False)) == set()

    fixture = json.loads(
        (ROOT / "results" / "regidrago_budew_promotion_baselines"
         / "aichi9_counts.json").read_text(encoding="utf-8")
    )
    rows = fixture["decklists"]
    assert len(rows) == 9
    assert sum(row["crispin"] > 0 for row in rows) == 8
    assert sum(row["crispin"] for row in rows) == 9
    assert sum(row["raihan"] > 0 for row in rows) == 9
    assert sum(row["raihan"] for row in rows) == 11
    assert sum(row["double_dragon_energy"] for row in rows) == 34
    assert all(row["basic_grass"] > 0 and row["basic_fire"] > 0 for row in rows)

    print(json.dumps({
        "published_lists": len(rows),
        "crispin_present_in_lists": sum(r["crispin"] > 0 for r in rows),
        "crispin_copies": sum(r["crispin"] for r in rows),
        "raihan_present_in_lists": sum(r["raihan"] > 0 for r in rows),
        "raihan_copies": sum(r["raihan"] for r in rows),
        "double_dragon_energy_copies": sum(r["double_dragon_energy"] for r in rows),
        "recharge_route_witnesses": {
            "crispin_holding_double_dragon":
                list(find_recharge_routes(crispy)[0].actions),
            "raihan_searching_double_dragon":
                list(find_recharge_routes(rai)[0].actions),
            "crispin_legacy":
                list(find_recharge_routes(legacy_crispin)[0].actions),
            "raihan_legacy":
                list(find_recharge_routes(legacy_raihan)[0].actions),
        },
    }, indent=2))


if __name__ == "__main__":
    main()
