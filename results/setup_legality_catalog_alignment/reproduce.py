"""Verify setup eligibility shares paper Expanded's full print-level exclusion policy."""

from pathlib import Path

from tools.build_expanded_legality_baseline import classify_effective_legality, load_json
from tools.setup_eligibility import build_setup_catalog

ROOT = Path(__file__).resolve().parents[2]
RESOURCES = ROOT / "resources"
TOURNAMENT_EXCLUSIONS = {
    "swshp-SWSH132",
    "swshp-SWSH135",
    "swshp-SWSH136",
    "swshp-SWSH137",
    "swshp-SWSH138",
    "swshp-SWSH144",
    "xy12-112",
}
BANNED_BASIC_IDS = {
    "swshp-SWSH136",
    "swshp-SWSH138",
    "swshp-SWSH144",
    "xy12-112",
}


def main() -> None:
    sets = load_json(RESOURCES / "sets" / "en.json")
    expanded_sets = {
        row["id"] for row in sets
        if (row.get("legalities") or {}).get("expanded") == "Legal"
    }
    cards = [
        card
        for set_id in sorted(expanded_sets)
        for card in load_json(RESOURCES / "cards" / "en" / f"{set_id}.json")
    ]
    tournament_exclusions = {
        card["id"]
        for card in cards
        if any(
            "cannot be used at official tournaments" in rule.lower()
            for rule in (card.get("rules") or [])
        )
    }
    assert tournament_exclusions == TOURNAMENT_EXCLUSIONS

    for card in cards:
        if card["id"] in TOURNAMENT_EXCLUSIONS:
            assert (card.get("legalities") or {}).get("expanded") is None
            assert classify_effective_legality(card) == (
                "Banned", "card_text_tournament_ban"
            )

    legal_cards = [
        card for card in cards if classify_effective_legality(card)[0] == "Legal"
    ]
    legal_basic_ids = {
        card["id"]
        for card in legal_cards
        if card.get("supertype") == "Pokémon"
        and "Basic" in (card.get("subtypes") or [])
    }
    forbidden = {"swsh4-66"}
    expected_forced = legal_basic_ids - forbidden
    catalog = build_setup_catalog(RESOURCES)

    assert len(cards) == 14884
    assert len(legal_cards) == 14829
    assert len(legal_basic_ids) == 7255
    assert catalog.legal_print_count == len(legal_cards)
    assert catalog.legal_basic_print_count == len(legal_basic_ids)
    assert catalog.forced_basic_count() == 7254
    assert catalog.forced_basic_print_ids == expected_forced
    assert not catalog.forced_basic_print_ids & BANNED_BASIC_IDS
    assert [row.card_id for row in catalog.forbidden_basic_exceptions] == [
        "swsh4-66"
    ]
    assert {
        row.card_id for row in catalog.optional_exceptions
    } == {
        "me1-28",
        "sm7-52",
        "smp-SM130",
        "sv4-175",
        "swsh12pt5-44",
        "xy11-96",
    }
    print(
        "PASS: 14,829 legal prints; 7,255 legal Basic prints; "
        "7,254 forced starters; seven banned promos excluded (four Basic)"
    )


if __name__ == "__main__":
    main()
