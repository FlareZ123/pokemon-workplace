"""Conservative AST/text triage of duplicate Expanded legality gates.

This is a detection tool: flagged modules require review, and absence from the
report is not proof that every downstream card-selection path is correct.
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path
import ast

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
EXCLUSIONS = {"build_expanded_legality_baseline.py", "legality_provenance.py"}


def inspect_source(path: Path) -> dict[str, object]:
    source = path.read_text(encoding="utf-8")
    ast.parse(source, filename=path.name)

    uses_overlay = "OFFICIAL_BAN_OVERLAY" in source
    canonical = "classify_effective_legality" in source
    raw_status = (
        'get("expanded")' in source
        or "get('expanded')" in source
    )
    direct_banned = '"Banned"' in source or "'Banned'" in source
    local_overlay_def = any(
        line.startswith("OFFICIAL_BAN_OVERLAY =") for line in source.splitlines()
    )
    return {
        "module": path.name,
        "overlay_reference": uses_overlay,
        "canonical_reference": canonical,
        "raw_expanded_status": raw_status,
        "banned_literal": direct_banned,
        "defines_overlay": local_overlay_def,
        "candidate_partial_gate": (
            path.name not in EXCLUSIONS
            and not canonical
            and raw_status
            and direct_banned
        ),
    }


def main() -> None:
    records = [
        inspect_source(path)
        for path in sorted(TOOLS.glob("*.py"))
    ]
    reviewed = {
        "setup_eligibility.py",
        "setup_trigger_role_contention.py",
        "bench_resource_catalog.py",
        "attack_copy_catalog.py",
        "lock_effect_catalog.py",
        "combat_lock_catalog.py",
        "bench_release_catalog.py",
        "multi_output_search_catalog.py",
    }
    by_name = {record["module"]: record for record in records}
    assert all(by_name[name]["canonical_reference"] for name in reviewed)
    assert not any(by_name[name]["candidate_partial_gate"] for name in reviewed)

    summary = Counter()
    for row in records:
        for key in (
            "overlay_reference",
            "canonical_reference",
            "raw_expanded_status",
            "defines_overlay",
            "candidate_partial_gate",
        ):
            summary[key] += int(bool(row[key]))

    print("Python tool files scanned:", len(records))
    print("Source property counts:", dict(summary))
    print("Candidate modules with raw Expanded ban checks and no canonical classifier:")
    for row in records:
        if row["candidate_partial_gate"]:
            print(" -", row["module"])
    print("Modules defining their own official ban overlays:")
    for row in records:
        if row["defines_overlay"]:
            print(" -", row["module"])
    print("PASS: eight audited catalogs delegate to canonical eligibility")


if __name__ == "__main__":
    main()
