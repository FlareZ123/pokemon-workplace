"""Reproduce KO redirection routing-signature coverage."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from knockout_redirection_taxonomy import (  # noqa: E402
    ALL_TO_LOST,
    ATTACHED_ENERGY_TO_HAND,
    POKEMON_TO_LOST,
    SELF_TO_HAND,
    build_taxonomy,
)


def main() -> None:
    result = build_taxonomy(ROOT / "resources")

    assert result["redirection_cards"] > 0
    assert result["unmatched"] == []

    signatures = set(result["routing_signature_counts"])
    assert signatures == {
        SELF_TO_HAND,
        ALL_TO_LOST,
        POKEMON_TO_LOST,
        ATTACHED_ENERGY_TO_HAND,
    }

    huntail = result["cards_by_signature"][ATTACHED_ENERGY_TO_HAND]
    assert "sv10-55" in huntail

    lost_city = result["cards_by_signature"][POKEMON_TO_LOST]
    assert "swsh11-161" in lost_city

    tyranitar = result["cards_by_signature"][ALL_TO_LOST]
    assert "sm8-121" in tyranitar

    aegislash = result["cards_by_signature"][SELF_TO_HAND]
    assert "sm11-95" in aegislash

    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
