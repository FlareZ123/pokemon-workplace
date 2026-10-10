"""Verify five effect-catalog legality adapters against the shared policy."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from build_expanded_legality_baseline import classify_effective_legality, load_json
from attack_copy_catalog import build as attack_copy_build, effective_legal
from lock_effect_catalog import _is_legal as lock_is_legal, build_catalog as locks
from combat_lock_catalog import _is_legal as combat_is_legal, build_catalog as combat
from bench_release_catalog import scan_bench_release_catalog
from multi_output_search_catalog import _legal_expanded_trainers, catalog_multi_output_trainers

RESOURCES = ROOT / "resources"
PROMOS = {
    "swshp-SWSH132", "swshp-SWSH135", "swshp-SWSH136",
    "swshp-SWSH137", "swshp-SWSH138", "swshp-SWSH144", "xy12-112",
}


def main() -> None:
    promos = [
        card
        for stem in ("swshp", "xy12")
        for card in load_json(RESOURCES / "cards" / "en" / f"{stem}.json")
        if card["id"] in PROMOS
    ]
    assert {card["id"] for card in promos} == PROMOS
    for card in promos:
        assert classify_effective_legality(card) == ("Banned", "card_text_tournament_ban")
        assert not effective_legal(card)
        assert not lock_is_legal(card)
        assert not combat_is_legal(card)

    attacks = attack_copy_build(RESOURCES)
    assert attacks["scope"]["legal_prints_scanned"] == 14829
    assert attacks["counts"]["copy_attack_prints"] == 64
    for row in attacks["signatures"]:
        assert PROMOS.isdisjoint(row["print_ids"])

    status_rows = (
        locks(RESOURCES)["effects"],
        combat(RESOURCES)["effects"],
    )
    for rows in status_rows:
        for row in rows:
            assert PROMOS.isdisjoint(row["print_ids"])

    bench = scan_bench_release_catalog(RESOURCES)
    assert bench["print_count"] == 50
    assert PROMOS.isdisjoint(row["id"] for row in bench["prints"])

    trainers = _legal_expanded_trainers(RESOURCES)
    assert len(trainers) == 2119
    assert PROMOS.isdisjoint(row["id"] for row in trainers)
    search = catalog_multi_output_trainers(RESOURCES)
    assert PROMOS.isdisjoint(row["id"] for row in search["rows"])
    print("PASS: full tournament-ban precedence across five effect catalogs")


if __name__ == "__main__":
    main()
