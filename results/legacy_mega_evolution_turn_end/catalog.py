"""Reproduce the legal Expanded legacy Mega/Spirit Link name coverage."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from legacy_mega_spirit_link_catalog import audit_legacy_mega_spirit_links

UNCOVERED = (
    "M Absol-EX",
    "M Blaziken-EX",
    "M Diancie-EX",
    "M Heracross-EX",
    "M Kangaskhan-EX",
    "M Metagross-EX",
    "M Swampert-EX",
)


def main() -> None:
    coverage = audit_legacy_mega_spirit_links(ROOT / "resources")
    assert coverage.total_legacy_prints == 92
    assert len(coverage.legacy_prints_by_name) == 41
    assert coverage.total_link_prints == 35
    assert len(coverage.spirit_link_prints_by_target) == 34
    assert coverage.uncovered_names == UNCOVERED
    links = dict(coverage.spirit_link_prints_by_target)
    assert "xy12-75" in links["M Charizard-EX"]
    assert "xy5-132" in links["Primal Kyogre-EX"]
    assert "me55c-106m" in dict(coverage.legacy_prints_by_name)["M Gardevoir-EX"]
    assert "me1-3" not in {
        print_id for _, ids in coverage.legacy_prints_by_name
        for print_id in ids
    }
    assert all(
        target in dict(coverage.legacy_prints_by_name)
        for target, _ in coverage.spirit_link_prints_by_target
    )

    print("legacy_mega_spirit_link_catalog regression: PASS")
    print(
        coverage.total_legacy_prints, "legal legacy Mega/Primal prints;",
        len(coverage.legacy_prints_by_name), "named targets"
    )
    print(
        coverage.total_link_prints, "legal matching Spirit Link prints;",
        len(coverage.spirit_link_prints_by_target), "named targets"
    )
    print("No matching Spirit Link:", ", ".join(coverage.uncovered_names))


if __name__ == "__main__":
    main()
