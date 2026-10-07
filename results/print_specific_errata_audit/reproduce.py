from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.official_print_errata import (
    MATERIAL_OVERLAY_IDS,
    PRINT_SPECIFIC_ERRATA,
    normalize_print_specific_errata,
    summarize_print_specific_errata,
)
from tools.build_expanded_legality_baseline import load_json

RESOURCES = ROOT / "resources"
summary = summarize_print_specific_errata(RESOURCES)
counts = summary["counts"]

assert counts["official_print_specific_prints"] == 41
assert counts["material_database_overlays"] == 24
assert counts["material_expanded_prints"] == 12
assert counts["material_historical_prints"] == 12
assert counts["already_semantically_reflected_or_metadata_only"] == 17
assert counts["raw_legal_gameplay_fingerprints"] == 10416
assert counts["normalized_legal_gameplay_fingerprints"] == 10416
assert counts["raw_exact_reprint_candidates"] == 106
assert counts["normalized_exact_reprint_candidates"] == 106
assert summary["raw_exact_candidate_ids"] == summary["normalized_exact_candidate_ids"]
assert len(MATERIAL_OVERLAY_IDS) == 24
assert len(PRINT_SPECIFIC_ERRATA) == 41

cards = {}
for path in sorted((RESOURCES / "cards" / "en").glob("*.json")):
    for raw in load_json(path):
        cards[raw["id"]] = raw

gengar = normalize_print_specific_errata(cards["dp7-18"])
assert "Attacking Pokémon is Knocked Out" in gengar["abilities"][0]["text"]

blastoise = normalize_print_specific_errata(cards["dp3-2"])
assert "basic Energy cards from your hand" in blastoise["abilities"][0]["text"]
assert "Basic Water Energy" not in blastoise["abilities"][0]["text"]

shield = normalize_print_specific_errata(cards["xy5-143"])
assert shield["rules"][0].startswith("This card can only be attached to Pokémon.")
assert "after applying Weakness and Resistance" in shield["rules"][1]

galvantula = normalize_print_specific_errata(cards["xy11-42"])
assert "2 of your opponent's Benched Pokémon" in galvantula["attacks"][0]["text"]

electrode = normalize_print_specific_errata(cards["xy12-40"])
assert "attach it to one of your Pokémon" in electrode["abilities"][0]["text"]
assert "one of your Lightning Pokémon" not in electrode["abilities"][0]["text"]

venusaur = normalize_print_specific_errata(cards["sm12-1"])
assert "whenever you attach" in venusaur["abilities"][0]["text"]
assert "Once during your turn" not in venusaur["abilities"][0]["text"]

cinderace = normalize_print_specific_errata(cards["swsh1-36"])
assert cinderace["retreatCost"] == ["Colorless"]
assert cinderace["convertedRetreatCost"] == 1

minior = normalize_print_specific_errata(cards["sv4-99"])
assert "whenever you attach" in minior["abilities"][0]["text"]
assert "Once during your turn" not in minior["abilities"][0]["text"]

charizard = normalize_print_specific_errata(cards["bw8-136"])
assert charizard["attacks"][1]["cost"] == ["Fire", "Colorless", "Colorless", "Colorless", "Colorless"]

print("official print-specific errata audit: PASS")
print("official print-specific records:", counts["official_print_specific_prints"])
print("material overlays:", counts["material_database_overlays"])
print("Expanded material overlays:", counts["material_expanded_prints"])
print("historical material overlays:", counts["material_historical_prints"])
print("exact reprint candidates:", counts["normalized_exact_reprint_candidates"])
