"""Catalog BW-onward Items with discard-from-hand plus deck-search text.

This is a card-pool text scan, not a format-legality certification.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
import json
from pathlib import Path
import re


BW_START = date(2011, 4, 25)
PATTERNS = (
    (re.compile(r"discard 3 (?:other )?cards? from your hand", re.I), 3, "any"),
    (re.compile(r"discard 2 (?:other )?cards? from your hand", re.I), 2, "any"),
    (re.compile(r"discard another Item card from your hand", re.I), 1, "item"),
    (re.compile(r"discard another card from your hand", re.I), 1, "any"),
    (re.compile(r"discard a card from your hand", re.I), 1, "any"),
)


@dataclass(frozen=True)
class DiscardSearchItem:
    name: str
    card_id: str
    release_date: date
    discard_cost: int
    payment_kind: str
    conditional_search: bool
    text: str


def _load(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("data", data) if isinstance(data, dict) else data


def _gate(text: str) -> tuple[int, str] | None:
    for pattern, cost, kind in PATTERNS:
        if pattern.search(text):
            return cost, kind
    return None


def scan_discard_search_items(root: Path) -> tuple[DiscardSearchItem, ...]:
    sets = _load(root / "sets" / "en.json")
    dates = {
        entry["id"]: datetime.strptime(
            entry["releaseDate"], "%Y/%m/%d"
        ).date()
        for entry in sets
    }
    latest: dict[str, DiscardSearchItem] = {}

    for path in sorted((root / "cards" / "en").glob("*.json")):
        release = dates.get(path.stem)
        if release is None or release < BW_START:
            continue
        for card in _load(path):
            if card.get("supertype") != "Trainer":
                continue
            if "Item" not in (card.get("subtypes") or []):
                continue
            text = " ".join(card.get("rules") or [])
            if "Search your deck" not in text:
                continue
            gate = _gate(text)
            if gate is None:
                continue
            cost, kind = gate
            item = DiscardSearchItem(
                name=card["name"],
                card_id=card["id"],
                release_date=release,
                discard_cost=cost,
                payment_kind=kind,
                conditional_search="Flip a coin" in text,
                text=text,
            )
            previous = latest.get(item.name)
            if previous is None or (
                item.release_date, item.card_id
            ) > (previous.release_date, previous.card_id):
                latest[item.name] = item

    return tuple(sorted(latest.values(), key=lambda item: item.name))


def distinct_name_payment_pairs(
    items: tuple[DiscardSearchItem, ...],
    *,
    deterministic_only: bool = True,
) -> tuple[tuple[str, str], ...]:
    pool = tuple(
        item
        for item in items
        if not deterministic_only or not item.conditional_search
    )
    return tuple(
        (payment.name, played.name)
        for payment in pool
        for played in pool
        if payment.name != played.name
        and played.payment_kind in {"any", "item"}
    )


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1] / "resources"
    items = scan_discard_search_items(root)
    for item in items:
        print(
            item.name,
            item.card_id,
            item.discard_cost,
            item.payment_kind,
            "conditional" if item.conditional_search else "deterministic",
        )
    print(
        "deterministic distinct-name payment pairs",
        len(distinct_name_payment_pairs(items)),
    )
