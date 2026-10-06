from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.combat_lock_catalog import build_catalog  # noqa: E402


def main() -> None:
    catalog = build_catalog(ROOT / "resources")
    assert catalog["counts"] == {
        "source_prints": 340,
        "source_gameplay_variants": 256,
        "effect_signatures": 243,
        "print_effect_instances": 340,
        "stochastic_signatures": 12,
    }
    assert catalog["dimensions"] == {"attack": 54, "retreat": 189}
    assert catalog["activation"] == {
        "active": 6,
        "attack_applied": 231,
        "bench": 1,
        "one_shot": 1,
        "passive": 3,
        "stadium": 1,
    }
    assert catalog["source_kinds"] == {"ability": 10, "attack": 231, "rule": 2}

    print(json.dumps({
        "counts": catalog["counts"],
        "dimensions": catalog["dimensions"],
        "activation": catalog["activation"],
        "source_kinds": catalog["source_kinds"],
    }, indent=2))


if __name__ == "__main__":
    main()
