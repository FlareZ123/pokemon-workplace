"""Acquire source-name Aichi Open 2026 decklists with fail-closed validation.

Source names and quantities are not English print IDs or legality certificates.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from pathlib import Path
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup
from filelock import FileLock

SOURCE_URL = "https://limitlesstcg.com/tournaments/566/decklists"
RANK = re.compile(r"^(\d{1,2})(?:st|nd|rd|th)\s+(.\S.*)$")
SECTION = re.compile(r"^(Pok[eé]mon|Trainer|Energy)\s*\((\d+)\)$")
CARD = re.compile(r"^(\d{1,2})\s+(.+)$")


def parse_source(html: str) -> list[dict]:
    """Parse the source's rendered text and verify complete deck totals."""
    soup = BeautifulSoup(html, "html.parser")
    for element in soup(["script", "style", "noscript", "template"]):
        element.decompose()
    lines = [" ".join(value.split()) for value in soup.stripped_strings]
    entries: list[dict] = []
    current = None
    section = None
    awaiting_archetype = False
    for line in lines:
        rank_match = RANK.fullmatch(line)
        if rank_match and "•" not in line:
            if current:
                entries.append(current)
            current = {"placing": int(rank_match.group(1)),
                       "player": rank_match.group(2), "archetype": None,
                       "pokemon": [], "trainer": [], "energy": [],
                       "declared": {}}
            section = None
            awaiting_archetype = True
            continue
        if current is None:
            continue
        section_match = SECTION.fullmatch(line)
        if section_match:
            section = {"Pokémon": "pokemon", "Pokemon": "pokemon",
                       "Trainer": "trainer", "Energy": "energy"}[section_match.group(1)]
            current["declared"][section] = int(section_match.group(2))
            awaiting_archetype = False
            continue
        if awaiting_archetype and line not in {"USD", "EUR"} and not line.startswith("$"):
            if not (line.startswith("Language") or line.startswith("Card versions")):
                current["archetype"] = line
                awaiting_archetype = False
            continue
        if section is None:
            continue
        card_match = CARD.fullmatch(line)
        if card_match:
            qty, name = int(card_match.group(1)), card_match.group(2)
            if 1 <= qty <= 60 and not name.startswith(("$", "USD", "EUR")):
                current[section].append({"count": qty, "name": name})
    if current:
        entries.append(current)

    if not entries:
        raise ValueError("No ranked decks detected; source layout may have changed")
    seen = set()
    for deck in entries:
        position = deck["placing"]
        if position in seen:
            raise ValueError(f"Duplicate placing {position}; inspect the actual tied rankings")
        seen.add(position)
        if not deck["archetype"] or set(deck["declared"]) != {"pokemon", "trainer", "energy"}:
            raise ValueError(f"Missing archetype or category for placement {position}: archetype={deck['archetype']}; categories={list(deck['declared'])}")
        for category, expected in deck["declared"].items():
            actual = sum(card["count"] for card in deck[category])
            if actual != expected:
                raise ValueError(f"Placement {position} {category}: declared {expected}, parsed {actual}")
        if sum(deck["declared"].values()) != 60:
            raise ValueError(f"Placement {position} doesn't contain 60 cards")
    if [deck["placing"] for deck in entries] != sorted(seen):
        raise ValueError("Source placements are not sorted")
    return entries


def fetch_source() -> str:
    request = Request(SOURCE_URL, headers={"User-Agent": "pokemon-workplace-research/1.0 (public tournament data)"})
    with urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8")


def save_atomic_locked(path: Path, data: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with FileLock(str(path) + ".lock", timeout=30):
        temp = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n", dir=path.parent,
                                             prefix="." + path.name + ".", delete=False) as handle:
                temp = Path(handle.name)
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp, path)
        finally:
            if temp is not None and temp.exists():
                temp.unlink()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--html", type=Path, help="Use saved source HTML rather than fetching")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    html = args.html.read_text(encoding="utf-8") if args.html else fetch_source()
    decks = parse_source(html)
    expected = [placing for placing in range(1, 33) if placing != 28]
    observed = [deck["placing"] for deck in decks]
    if observed != expected:
        raise ValueError(f"Unexpected source coverage; expected ranks {expected}, observed {observed}")
    result = {"event": "CL Aichi Open League 2026", "date": "2026-05-10",
              "source": SOURCE_URL, "source_html_sha256": hashlib.sha256(html.encode()).hexdigest(),
              "provenance": "Published source-name rows and quantities, not verified English print IDs",
              "missing_ranked_opponents": [{"placing": 28, "player": "Jo Kato",
                                            "archetype": "Regidrago",
                                            "archetype_source": "https://limitlesstcg.com/decks/260",
                                            "standing_source": "https://limitlesstcg.com/tournaments/566",
                                            "source_deck_status": "not_published"}],
              "decks": decks}
    save_atomic_locked(args.output, json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(f"Verified {len(decks)} published 60-card source decks; source sha256={result['source_html_sha256']}")
    for deck in decks:
        d = deck["declared"]
        print(f"{deck['placing']:2d}. {deck['player']}: {deck['archetype']} "
              f"({d['pokemon']}/{d['trainer']}/{d['energy']})")


if __name__ == "__main__":
    main()
