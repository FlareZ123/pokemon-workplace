"""Card pool and explicit current-semantic regression for targeted switch Trainers."""
from collections import Counter
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.trainer_gust_catalog import (
    CATEGORIES, CORRECTED_POKEMON_CATCHER_EFFECT, OLD_NO_FLIP_PRINT_IDS,
    catalog, summary,
)


def main():
    root = Path(__file__).resolve().parents[2] / "resources"
    rows = catalog(root)
    s = summary(rows)
    assert s["print_count"] == 75
    assert s["distinct_names"] == 22
    assert set(row.card_name for row in rows) == set(CATEGORIES)
    assert not any(row.profile.family == "unclassified" for row in rows)

    targeted = [row for row in rows if row.profile.player_selects_existing_bench]
    assert len(targeted) == 57
    assert len({r.card_name for r in targeted}) == 16
    assert s["target_scopes"] == {
        "any": 46,
        "basic": 3,
        "gx_or_legacy_ex": 2,
        "mega_evolution": 1,
        "pokemon_v_family": 3,
        "remaining_hp_le_50": 2,
    }

    # Avoid mistaking an opponent's hand -> Bench -> Active transition, or
    # the opponent selecting its own replacement, for Boss-style gust.
    for name in ("Erika's Invitation", "Repel", "Ryme", "Escape Rope"):
        assert not CATEGORIES[name].player_selects_existing_bench
    assert CATEGORIES["Kieran"].family == "no_opponent_switch"
    assert CATEGORIES["Team Rocket's Bother-Bot"].family == "non_pokemon_zone_swap"
    assert CATEGORIES["Boss's Orders"].target_scope == "any"
    assert CATEGORIES["Serena"].target_scope == "pokemon_v_family"
    assert CATEGORIES["Lisia's Appeal"].target_scope == "basic"
    assert "discard_two" in CATEGORIES["Great Catcher"].gates
    assert "own_prizes_gt_opponent" in CATEGORIES["Counter Catcher"].gates
    assert "two_copies_together" in CATEGORIES["Cross Switcher"].gates
    assert "must_switch_own_team_rocket_first" in CATEGORIES["Team Rocket's Giovanni"].gates

    # The 3 obsolete BW prints were originally deterministic but officially
    # errata-corrected into the same 50% coin route as all later prints.
    assert set(s["errata_print_ids"]) == OLD_NO_FLIP_PRINT_IDS
    catchers = [r for r in rows if r.card_name == "Pokémon Catcher"]
    assert len(catchers) == 11
    assert all("Flip a coin" in r.effective_text for r in catchers)
    assert all(
        "Flip a coin" not in r.raw_text and r.effective_text == CORRECTED_POKEMON_CATCHER_EFFECT
        for r in catchers if r.errata_applied
    )
    assert all(
        "Flip a coin" in r.raw_text and not r.errata_applied
        for r in catchers if not r.errata_applied
    )

    # Source-category sanity: this survey tracks exact printed Trainer
    # sources and does not call every occurrence of 'switch' a gust.
    other_count = Counter(r.profile.family for r in rows if r not in targeted)
    assert other_count == {
        "opponent_chooses_promotion": 9,
        "opponent_hand_to_bench_then_active": 3,
        "no_opponent_switch": 5,
        "non_pokemon_zone_swap": 1,
    }
    print("PASS: 75 legal print records, 22 human-reviewed names")
    print("57 direct player-selected target records across 16 names")
    print("Non-targeted category counts:", dict(sorted(other_count.items())))
    print("Target scopes:", s["target_scopes"])
    print("3 original deterministic text records normalized to 50% coin errata")


if __name__ == "__main__":
    main()
