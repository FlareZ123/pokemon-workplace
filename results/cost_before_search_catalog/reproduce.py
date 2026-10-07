"""Reproduce the conservative paper-Expanded cost-before-search catalog."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from cost_before_search_catalog import build_catalog


EXPECTED_NAMES = {
    "Adaman",
    "Canari",
    "Computer Search",
    "Cram-o-matic",
    "Crasher Wake",
    "Earthen Vessel",
    "Electromagnetic Radar",
    "Fiery Flint",
    "Larry's Skill",
    "Mysterious Treasure",
    "Peony",
    "Quick Ball",
    "Red's Challenge",
    "Secret Box",
    "Techno Radar",
    "Ultra Ball",
}


def main() -> None:
    result = build_catalog(ROOT / "resources")
    names = {entry["name"] for entry in result["names"]}

    if result["print_count"] != 54:
        raise AssertionError(result["print_count"])
    if result["unique_names"] != 16:
        raise AssertionError(result["unique_names"])
    if result["unique_gameplay_fingerprints"] != 23:
        raise AssertionError(result["unique_gameplay_fingerprints"])
    if names != EXPECTED_NAMES:
        raise AssertionError((sorted(names), sorted(EXPECTED_NAMES)))
    if result["name_counts_by_discard_mode"] != {
        "selective": 11,
        "typed_selective": 3,
        "whole_hand": 2,
    }:
        raise AssertionError(result["name_counts_by_discard_mode"])
    if result["stochastic_names"] != ["Cram-o-matic"]:
        raise AssertionError(result["stochastic_names"])

    print(f"prints={result['print_count']}")
    print(f"unique_names={result['unique_names']}")
    print(f"gameplay_fingerprints={result['unique_gameplay_fingerprints']}")
    print("names=" + ", ".join(sorted(names)))
    print("discard_modes=" + repr(result["name_counts_by_discard_mode"]))
    print("stochastic=Cram-o-matic")
    print("All cost-before-search catalog checks passed.")


if __name__ == "__main__":
    main()
