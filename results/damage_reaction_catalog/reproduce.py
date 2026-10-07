from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from damage_reaction_catalog import build_damage_reaction_catalog  # noqa: E402


def main() -> None:
    result = build_damage_reaction_catalog(ROOT / "resources")
    print(result)


if __name__ == "__main__":
    main()
