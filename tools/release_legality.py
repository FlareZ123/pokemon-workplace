from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Literal

from tools.build_expanded_legality_baseline import (
    classify_effective_legality,
    gameplay_fingerprint,
    load_json,
)

ReleaseStatus = Literal["waiting_period", "ordinary_release_eligible", "no_audited_anchor"]


@dataclass(frozen=True)
class ProductReleaseAnchor:
    key: str
    expansion_name: str
    set_ids: tuple[str, ...]
    anchor_date: date
    anchor_kind: str
    wait_days: int
    source_urls: tuple[str, ...]

    @property
    def ordinary_legal_date(self) -> date:
        return self.anchor_date + timedelta(days=self.wait_days)


PRODUCT_RELEASE_ANCHORS = (
    ProductReleaseAnchor(
        key="30th_celebration_2026",
        expansion_name="30th Celebration",
        set_ids=("me55", "me55c"),
        anchor_date=date(2026, 9, 16),
        anchor_kind="Elite Trainer Box / expansion launch",
        wait_days=14,
        source_urls=(
            "https://community.pokemon.com/en-us/discussion/22216/pokemon-tcg-product-legality-update",
            "https://www.pokemon.com/us/news/the-pokemon-tcg-30th-celebration-expansion-is-available-now",
            "https://www.pokemon.com/us/news/pokemon-tcg-30th-celebration-product-showcase",
        ),
    ),
)

ANCHOR_BY_KEY = {anchor.key: anchor for anchor in PRODUCT_RELEASE_ANCHORS}
ANCHOR_BY_SET = {
    set_id: anchor
    for anchor in PRODUCT_RELEASE_ANCHORS
    for set_id in anchor.set_ids
}


def parse_release_date(value: str) -> date:
    return date.fromisoformat(value.replace("/", "-"))


def release_status(set_id: str, *, as_of: date) -> tuple[ReleaseStatus, date | None]:
    anchor = ANCHOR_BY_SET.get(set_id)
    if anchor is None:
        return "no_audited_anchor", None
    if as_of < anchor.ordinary_legal_date:
        return "waiting_period", anchor.ordinary_legal_date
    return "ordinary_release_eligible", anchor.ordinary_legal_date


def audit_product_anchor(
    resources_root: Path,
    *,
    anchor_key: str,
    as_of: date,
) -> dict[str, Any]:
    anchor = ANCHOR_BY_KEY[anchor_key]
    sets = load_json(resources_root / "sets" / "en.json")
    set_by_id = {row["id"]: row for row in sets}
    expanded_sets = {
        row["id"]
        for row in sets
        if (row.get("legalities") or {}).get("expanded") == "Legal"
    }

    for set_id in anchor.set_ids:
        if set_id not in expanded_sets:
            raise ValueError(f"Audited set is not marked Expanded-legal in snapshot: {set_id}")

    prior_by_fingerprint: dict[str, list[dict[str, str]]] = defaultdict(list)
    conservative_prior_cutoff = anchor.anchor_date - timedelta(days=anchor.wait_days)

    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        set_id = path.stem
        if set_id not in expanded_sets or set_id in anchor.set_ids:
            continue

        release_date = parse_release_date(set_by_id[set_id]["releaseDate"])
        if release_date > conservative_prior_cutoff:
            continue

        for card in load_json(path):
            status, _source = classify_effective_legality(card)
            if status != "Legal":
                continue
            prior_by_fingerprint[gameplay_fingerprint(card)].append(
                {
                    "id": card["id"],
                    "name": card["name"],
                    "set_id": set_id,
                    "release_date": release_date.isoformat(),
                }
            )

    fallback_rows: list[dict[str, str]] = []
    exact_candidates: list[dict[str, Any]] = []

    for set_id in anchor.set_ids:
        for card in load_json(resources_root / "cards" / "en" / f"{set_id}.json"):
            effective_status, legality_source = classify_effective_legality(card)
            if effective_status == "Legal" and legality_source == "set_fallback":
                fallback_rows.append(
                    {"id": card["id"], "name": card["name"], "set_id": set_id}
                )

            if effective_status != "Legal":
                continue

            matches = prior_by_fingerprint.get(gameplay_fingerprint(card), ())
            if matches:
                exact_candidates.append(
                    {
                        "id": card["id"],
                        "name": card["name"],
                        "set_id": set_id,
                        "prior_matches": list(matches),
                    }
                )

    fallback_by_set = Counter(row["set_id"] for row in fallback_rows)
    candidate_by_set = Counter(row["set_id"] for row in exact_candidates)
    set_status = {
        set_id: {
            "status": release_status(set_id, as_of=as_of)[0],
            "ordinary_legal_date": anchor.ordinary_legal_date.isoformat(),
        }
        for set_id in sorted(anchor.set_ids)
    }

    return {
        "as_of": as_of.isoformat(),
        "anchor": {
            "key": anchor.key,
            "expansion_name": anchor.expansion_name,
            "set_ids": list(anchor.set_ids),
            "anchor_date": anchor.anchor_date.isoformat(),
            "anchor_kind": anchor.anchor_kind,
            "wait_days": anchor.wait_days,
            "ordinary_legal_date": anchor.ordinary_legal_date.isoformat(),
            "source_urls": list(anchor.source_urls),
        },
        "set_status": set_status,
        "fallback_print_count": len(fallback_rows),
        "fallback_by_set": dict(sorted(fallback_by_set.items())),
        "all_fallback_prints_ordinary_release_eligible": all(
            release_status(row["set_id"], as_of=as_of)[0] == "ordinary_release_eligible"
            for row in fallback_rows
        ),
        "exact_prior_fingerprint_candidate_count": len(exact_candidates),
        "exact_prior_fingerprint_candidates_by_set": dict(sorted(candidate_by_set.items())),
        "exact_prior_fingerprint_candidates": exact_candidates,
        "caution": (
            "Ordinary product-date eligibility and functional-reprint evidence are separate from bans, "
            "card-specific tournament restrictions, regional availability, and official semantic equivalence. "
            "Exact gameplay fingerprints are a conservative candidate generator, not an official reprint ruling."
        ),
    }


def audit_30th_celebration(resources_root: Path, *, as_of: date) -> dict[str, Any]:
    return audit_product_anchor(
        resources_root,
        anchor_key="30th_celebration_2026",
        as_of=as_of,
    )
