"""Compile typed execution contracts for Expanded attack-copy signatures."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

from attack_copy_catalog import build as build_catalog
from attack_copy_execution_phases import build as build_phases


def build(resources_root: Path) -> dict[str, Any]:
    catalog = build_catalog(resources_root)
    phases = build_phases(resources_root)
    phase_by_key = {
        (row["attack_name"], row["attack_text"]): row
        for row in phases["signatures"]
    }

    contracts: list[dict[str, Any]] = []
    for signature in catalog["signatures"]:
        key = (signature["attack_name"], signature["text"])
        phase = phase_by_key[key]
        flags = {
            "selected_energy_gate": (
                phase["selected_attack_energy_gate_position"] is not None
            ),
            "selected_source_zone_commit": (
                phase["source_lifetime_pattern"]
                == "selected_source_discarded_from_opponent_hand_before_body"
            ),
            "preselection_source_zone_commit": (
                phase["source_lifetime_pattern"]
                == "top_card_discarded_before_eligibility_and_body"
            ),
            "post_copy_continuation": (
                phase["trailing_semantics"] == "post_copy_cleanup"
            ),
            "outer_gx_usage_rule": (
                phase["trailing_semantics"] == "gx_usage_rule"
            ),
        }
        non_tail = [name for name, enabled in flags.items() if enabled]
        contracts.append(
            {
                "attack_name": signature["attack_name"],
                "card_names": signature["card_names"],
                "print_ids": signature["print_ids"],
                "source_classes": signature["source_classes"],
                "direct_non_gx_filter": signature["direct_non_gx_filter"],
                "optional_selection": signature["optional_selection"],
                "structural_same_attack_reentry": (
                    signature["structural_same_attack_reentry"]
                ),
                "selected_attack_energy_gate_position": (
                    phase["selected_attack_energy_gate_position"]
                ),
                "source_lifetime_pattern": phase["source_lifetime_pattern"],
                "trailing_semantics": phase["trailing_semantics"],
                "non_tail_semantics": non_tail,
                "simple_tail_copy_under_current_classifier": not non_tail,
            }
        )

    contracts.sort(key=lambda row: (row["attack_name"], row["print_ids"]))
    complex_rows = [
        row for row in contracts
        if not row["simple_tail_copy_under_current_classifier"]
    ]
    source_counts = Counter(
        source
        for row in contracts
        for source in row["source_classes"]
    )
    complexity_counts = Counter(
        flag
        for row in contracts
        for flag in row["non_tail_semantics"]
    )

    return {
        "scope": catalog["scope"],
        "signature_count": len(contracts),
        "simple_tail_copy_signature_count": len(contracts) - len(complex_rows),
        "non_tail_signature_count": len(complex_rows),
        "non_tail_attack_names": [row["attack_name"] for row in complex_rows],
        "non_tail_semantics_counts": dict(sorted(complexity_counts.items())),
        "source_class_counts": dict(sorted(source_counts.items())),
        "contracts": contracts,
        "interpretation": [
            "All copy effects require a source-selection contract, but only the signatures marked non-tail require one of the currently recognized extra execution phases.",
            "A simple-tail classification is local to the current parser and does not mean the attack is strategically simple or free of dynamic state constraints.",
            "Static pairwise compatibility should retain these contract fields so later execution does not silently drop Energy gates, source commits, continuations, or the outer GX resource.",
        ],
    }


def atomic_write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, indent=2, ensure_ascii=False) + "\n"
    lock_path = path.with_suffix(path.suffix + ".lock")
    with lock_path.open("a+b") as lock_file:
        if os.name == "nt":
            import msvcrt

            if lock_file.tell() == 0:
                lock_file.write(b"0")
                lock_file.flush()
                lock_file.seek(0)
            msvcrt.locking(lock_file.fileno(), msvcrt.LK_LOCK, 1)
        else:
            import fcntl

            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)

        tmp_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=path.parent,
                delete=False,
            ) as tmp_file:
                tmp_file.write(payload)
                tmp_file.flush()
                os.fsync(tmp_file.fileno())
                tmp_path = Path(tmp_file.name)
            os.replace(tmp_path, path)
        finally:
            if tmp_path is not None and tmp_path.exists():
                tmp_path.unlink()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compile execution contracts for Expanded attack-copy effects."
    )
    parser.add_argument("--resources-root", type=Path, default=Path("resources"))
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/attack_copy_contracts/contracts.json"),
    )
    args = parser.parse_args()
    result = build(args.resources_root)
    atomic_write_json(args.output, result)
    print(
        json.dumps(
            {
                "signature_count": result["signature_count"],
                "simple_tail_copy_signature_count": (
                    result["simple_tail_copy_signature_count"]
                ),
                "non_tail_signature_count": result["non_tail_signature_count"],
                "non_tail_attack_names": result["non_tail_attack_names"],
                "non_tail_semantics_counts": result["non_tail_semantics_counts"],
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
