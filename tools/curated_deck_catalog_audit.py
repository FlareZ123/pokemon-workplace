"""Audit curated paper Expanded 60-card deck pages against verified source prints.

The source decks were independently validated in competitive_deck_baselines.
This script checks that human-usable markdown copies reproduce exactly those
card quantities and print IDs, including the declared Mew VIP4 swap.
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "results" / "competitive_deck_baselines"
DECKS = ROOT / "results" / "decks"

ROW = re.compile(r"^\|\s*(\d+)\s*\|.*\|\s*`?([a-z][a-z0-9]*-[A-Za-z0-9]+)`?\s*\|\s*$")
BULLET = re.compile(r"^\s*-\s*(\d+)\s+.+\(`([a-z][a-z0-9]*-[A-Za-z0-9]+)`\)\s*$")

BASELINE_SECTIONS = {
    "vileplume": "2026 Aichi Open League runner-up: Vileplume control",
    "shadow_rider": "2026 Aichi champion: Shadow Rider Calyrex",
    "mew": "2026 Aichi fifth place: Mew Genesect",
}
PAGES = {
    "shadow-rider-aichi-2026": "shadow_rider",
    "shadow-rider-calyrex": "shadow_rider",
    "vileplume-control-aichi-2026": "vileplume",
    "vileplume-control": "vileplume",
    "mew-genesect-aichi-2026": "mew",
    "mew-genesect": "mew",
    "mew-genesect-vip4-aichi-counterfactual": "mew_vip4",
    "regidrago-aichi-2026": "regidrago",
    "regidrago-vstar": "regidrago",
    "mega-absol-garbodor": "absol",
}


def parse_print_counts(markdown: str) -> Counter[str]:
    """Extract only quantity-to-print rows and quantity-to-print bullets."""

    counts: Counter[str] = Counter()
    for line in markdown.splitlines():
        match = ROW.match(line) or BULLET.match(line)
        if match:
            quantity, print_id = match.groups()
            counts[print_id] += int(quantity)
    return counts


def source_section(markdown: str, heading: str) -> str:
    """Find one H2 section with no spillover into later H2 headings."""

    marker = f"## {heading}\n"
    if markdown.count(marker) != 1:
        raise AssertionError(f"expected exactly one source heading {heading!r}")
    remainder = markdown.split(marker, 1)[1]
    return remainder.split("\n## ", 1)[0]


def source_json(name: str) -> Counter[str]:
    path = BASELINE / name
    data = json.loads(path.read_text(encoding="utf-8"))
    counts: Counter[str] = Counter()
    for card in data["cards"]:
        counts[card["print_id"]] += card["quantity"]
    return counts


def expected_catalog() -> dict[str, Counter[str]]:
    baseline = (BASELINE / "README.md").read_text(encoding="utf-8")
    expected = {
        key: parse_print_counts(source_section(baseline, heading))
        for key, heading in BASELINE_SECTIONS.items()
    }
    expected["regidrago"] = source_json("regidrago_haruku_2026.json")
    expected["absol"] = source_json("absol_garbodor_kobayashi_2026.json")

    vip4 = expected["mew"].copy()
    vip4["swsh8-225"] += 1
    vip4["me4-82"] -= 1
    expected["mew_vip4"] = vip4

    for family, cards in expected.items():
        if sum(cards.values()) != 60 or min(cards.values()) <= 0:
            raise AssertionError(f"source deck {family} is not a valid 60-card count")
    return expected


def main() -> None:
    expected = expected_catalog()
    for directory, family in PAGES.items():
        path = DECKS / directory / "README.md"
        actual = parse_print_counts(path.read_text(encoding="utf-8"))
        wanted = expected[family]
        differences = {
            print_id: (wanted.get(print_id, 0), actual.get(print_id, 0))
            for print_id in wanted.keys() | actual.keys()
            if wanted.get(print_id, 0) != actual.get(print_id, 0)
        }
        if differences:
            raise AssertionError(f"{directory} diverges from {family}: {differences}")
        assert sum(actual.values()) == 60, directory
        print(f"PASS {directory}: 60 cards, {len(actual)} prints, source={family}")

    print(f"All {len(PAGES)} curated deck pages match verified source inventories.")


if __name__ == "__main__":
    main()
