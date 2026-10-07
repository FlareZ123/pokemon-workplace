from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from tools.build_expanded_legality_baseline import classify_effective_legality, load_json


def parse_release_date(value: str) -> date:
    return date.fromisoformat(value.replace("/", "-"))


def audit(resources_root: Path, *, as_of: date | None = None) -> dict[str, Any]:
    as_of = as_of or date.today()
    sets = load_json(resources_root / "sets" / "en.json")
    set_by_id = {entry["id"]: entry for entry in sets}
    expanded_sets = {
        entry["id"]
        for entry in sets
        if (entry.get("legalities") or {}).get("expanded") == "Legal"
    }

    rows: list[dict[str, Any]] = []
    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        if path.stem not in expanded_sets:
            continue
        set_meta = set_by_id[path.stem]
        release_date = parse_release_date(set_meta["releaseDate"])
        nominal_two_week_date = release_date + timedelta(days=14)
        for raw in load_json(path):
            status, source = classify_effective_legality(raw)
            if status != "Legal" or source != "set_fallback":
                continue
            rows.append(
                {
                    "id": raw["id"],
                    "name": raw["name"],
                    "set_id": path.stem,
                    "set_name": set_meta["name"],
                    "release_date": release_date.isoformat(),
                    "nominal_two_week_date": nominal_two_week_date.isoformat(),
                    "past_nominal_two_week_date": as_of >= nominal_two_week_date,
                    "unlimited_status": (raw.get("legalities") or {}).get("unlimited"),
                    "rule_count": len(raw.get("rules") or ()),
                }
            )

    by_set = Counter(row["set_id"] for row in rows)
    return {
        "as_of": as_of.isoformat(),
        "fallback_print_count": len(rows),
        "fallback_sets": [
            {
                "set_id": set_id,
                "set_name": set_by_id[set_id]["name"],
                "release_date": parse_release_date(set_by_id[set_id]["releaseDate"]).isoformat(),
                "nominal_two_week_date": (
                    parse_release_date(set_by_id[set_id]["releaseDate"]) + timedelta(days=14)
                ).isoformat(),
                "print_count": count,
            }
            for set_id, count in sorted(by_set.items())
        ],
        "all_past_nominal_two_week_date": all(row["past_nominal_two_week_date"] for row in rows),
        "rows": rows,
        "caution": (
            "releaseDate + 14 days is an audit aid, not a universal tournament-legality oracle. "
            "Official product and promo legality schedules, staggered releases, bans, and card-specific "
            "restrictions can override or refine set metadata."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit set-level Expanded legality fallbacks.")
    parser.add_argument("--resources-root", type=Path, default=Path("resources"))
    parser.add_argument("--as-of", type=date.fromisoformat)
    args = parser.parse_args()
    print(json.dumps(audit(args.resources_root, as_of=args.as_of), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
