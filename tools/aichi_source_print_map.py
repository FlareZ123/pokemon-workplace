"""Audit exact Limitless card links against the bundled English print archive.

The resulting English catalog IDs identify the source site's DISPLAY print links,
not the real Japanese player's physical cards. Basic Energy surrogates are explicit.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
from pathlib import Path
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from aichi_top32_source import save_atomic_locked

PROMO_SETS = {"SMP": "smp", "XYP": "xyp", "BWP": "bwp"}
PROMO_PREFIX = {"SMP": "SM", "XYP": "XY", "BWP": "BW"}
NAME_ALIASES = {
    "Battle Compressor": "Battle Compressor Team Flare Gear",
    "Robo Substitute": "Robo Substitute Team Flare Gear",
    "Target Whistle": "Target Whistle Team Flare Gear",
    "Unit Energy LPM": "Unit Energy LightningPsychicMetal",
}
BASELINE_ROW_COUNTS = {
    "exact_english_catalog": 945,
    "basic_energy_surrogate": 35,
    "japanese_only": 9,
}


def read_catalog(resources: Path) -> tuple[dict, dict]:
    """Load the source bundle's catalog without treating set codes as unique."""
    all_sets = json.loads((resources / "sets" / "en.json").read_text(encoding="utf-8"))
    code_to_sets: dict[str, list[str]] = collections.defaultdict(list)
    for card_set in all_sets:
        if card_set.get("ptcgoCode"):
            code_to_sets[card_set["ptcgoCode"]].append(card_set["id"])
    for code, set_id in PROMO_SETS.items():
        code_to_sets[code].append(set_id)
    card_sets = {}
    for set_id in {sid for group in code_to_sets.values() for sid in group}:
        card_sets[set_id] = json.loads(
            (resources / "cards" / "en" / f"{set_id}.json").read_text(encoding="utf-8")
        )
    return dict(code_to_sets), card_sets


def audit_source(
    html: str,
    report: dict,
    code_to_sets: dict,
    card_sets: dict,
) -> dict:
    """Return a catalog-annotated report after strict source/link reconciliation."""
    actual_hash = hashlib.sha256(html.encode("utf-8")).hexdigest()
    if report["source_html_sha256"] != actual_hash:
        raise ValueError("HTML content does not match source report SHA-256")

    soup = BeautifulSoup(html, "html.parser")
    nodes = soup.select("div.decklist-card")
    rows = [(d, category, r)
            for d in report["decks"]
            for category in ("pokemon", "trainer", "energy")
            for r in d[category]]
    if len(rows) != len(nodes):
        raise ValueError(f"Displayed card rows {len(nodes)} versus parsed rows {len(rows)}")

    basic_energy = {
        card["name"]: card
        for card in card_sets["bw1"]
        if card.get("supertype") == "Energy"
        and "Basic" in card.get("subtypes", [])
    }
    statuses = collections.Counter()
    physical = collections.Counter()
    source_names = collections.Counter()

    for i, ((deck, category, row), node) in enumerate(zip(rows, nodes)):
        anchors = node.select('a[href^="/cards/"]')
        if len(anchors) != 1:
            raise ValueError(f"Rank {deck['placing']} row {i}: expected one primary card anchor")
        anchor = anchors[0]
        label = anchor.get_text(" ", strip=True)
        count, name = row["count"], row["name"]
        if label not in {f"{count} {name}", f"{count} {name} ♢",
                         f"{count} {name} unreleased"}:
            raise ValueError(f"Rank {deck['placing']} row {i}: source label mismatch {label!r}")
        href = anchor["href"]
        segments = urlparse(href).path.split("/")
        if len(segments) < 4 or segments[1] != "cards":
            raise ValueError(f"Rank {deck['placing']} row {i}: malformed card link {href}")
        row["source_display_label"] = label
        row["source_print_href"] = href
        row["catalog_card_id"] = None

        if segments[2] == "jp":
            if len(segments) != 5 or not label.endswith(" unreleased"):
                raise ValueError(f"Rank {deck['placing']} row {i}: unexpected JP print reference")
            row["catalog_mapping_status"] = "japanese_only"
            row["source_card_code"] = segments[3]
            row["source_card_number"] = segments[4]
        else:
            code, number = segments[2:4]
            if len(segments) != 4:
                raise ValueError(f"Rank {deck['placing']} row {i}: unexpected print URL")
            row["source_card_code"] = code
            row["source_card_number"] = number

            if code == "MEE":
                if category != "energy" or name not in basic_energy:
                    raise ValueError(f"Rank {deck['placing']} row {i}: nonbasic MEE substitute")
                card = basic_energy[name]
                row["catalog_mapping_status"] = "basic_energy_surrogate"
                row["catalog_card_id"] = card["id"]
                row["catalog_card_name"] = card["name"]
            else:
                possible = {
                    number,
                    PROMO_PREFIX.get(code, "") + number,
                }
                cards = [
                    c for sid in code_to_sets.get(code, [])
                    for c in card_sets[sid]
                    if c["number"] in possible
                ]
                if len(cards) != 1:
                    raise ValueError(
                        f"Rank {deck['placing']} row {i}: {code}/{number} has {len(cards)} English candidates"
                    )
                card = cards[0]
                archive_name = NAME_ALIASES.get(name, name)
                if label.endswith(" ♢"):
                    archive_name += " ◇"
                if archive_name != card["name"]:
                    raise ValueError(
                        f"Rank {deck['placing']} row {i}: label {name!r} != "
                        f"catalog name {card['name']!r}"
                    )
                required_type = {"pokemon": "Pokémon", "trainer": "Trainer", "energy": "Energy"}[category]
                if card.get("supertype") != required_type:
                    raise ValueError(
                        f"Rank {deck['placing']} row {i}: catalog supertype mismatch"
                    )
                if card.get("legalities", {}).get("expanded") != "Legal":
                    raise ValueError(
                        f"Rank {deck['placing']} row {i}: catalog Expanded status is not Legal"
                    )
                row["catalog_mapping_status"] = "exact_english_catalog"
                row["catalog_card_id"] = card["id"]
                row["catalog_card_name"] = card["name"]

        status = row["catalog_mapping_status"]
        statuses[status] += 1
        physical[status] += count
        source_names[(deck["placing"], name)] += 1

    if dict(statuses) != BASELINE_ROW_COUNTS:
        raise ValueError(
            f"Changed source print-link distribution: {dict(statuses)}"
        )
    report["print_mapping"] = {
        "source_scope": "Limitless displayed card print links; physical Japanese print choices not established",
        "source_html_sha256": actual_hash,
        "row_status": dict(statuses),
        "physical_copy_status": dict(physical),
        "preserved_card_name_rows": len(rows),
        "repeated_name_row_groups": sum(n > 1 for n in source_names.values()),
        "catalog_print_status": "English Expanded flags from bundled card archive; not an independent region-legal certification",
    }
    report["research_revision"] = os.environ.get("GITHUB_SHA")
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-html", type=Path, required=True)
    parser.add_argument("--source-json", type=Path, required=True)
    parser.add_argument("--resources", type=Path, default=Path("resources"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    html = args.source_html.read_text(encoding="utf-8")
    report = json.loads(args.source_json.read_text(encoding="utf-8"))
    code_to_sets, card_sets = read_catalog(args.resources)
    enriched = audit_source(html, report, code_to_sets, card_sets)
    save_atomic_locked(args.output, json.dumps(enriched, ensure_ascii=False, indent=2) + "\n")
    print("Verified print-link mapping:", enriched["print_mapping"])


if __name__ == "__main__":
    main()
