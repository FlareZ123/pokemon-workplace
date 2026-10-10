"""Reprint text audit: verify formatting-only and unresolved printed differences."""
from __future__ import annotations

from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from special_energy_print_fingerprints import (
    scan_special_energy_prints, text_variant_groups,
)


def main() -> None:
    rows = scan_special_energy_prints(ROOT / "resources")
    raw = text_variant_groups(rows, normalized=False)
    normalized = text_variant_groups(rows, normalized=True)

    assert len(rows) == 113
    assert len(raw) == len(normalized) == 74
    assert len([name for name in raw if sum(map(len, raw[name].values())) > 1]) == 26

    raw_changed = {name for name, variants in raw.items() if len(variants) > 1}
    normalized_changed = {name for name, variants in normalized.items() if len(variants) > 1}

    assert raw_changed == {
        "Prism Energy", "Jet Energy", "Luminous Energy", "Reversal Energy",
    }
    assert normalized_changed == {"Prism Energy"}

    # The Prism Energy change rephrases the attached-to-Basic condition.
    # Source-text equality is not proof that every card is interchangeable,
    # and semantic equivalence of this remaining pair is not established
    # by the automatic normalization.
    ids = sorted(row.print_id for row in rows if row.name == "Prism Energy")
    assert ids == ["bw4-93", "me2pt5-216", "zsv10pt5-86"]
    assert len(normalized["Prism Energy"]) == 2

    print("Special Energy reprint text audit: PASS")
    print({
        "print_rows": len(rows),
        "distinct_names": len(raw),
        "reprinted_names": 26,
        "raw_variants": sorted(raw_changed),
        "variants_after_format_normalization": sorted(normalized_changed),
    })


if __name__ == "__main__":
    main()
