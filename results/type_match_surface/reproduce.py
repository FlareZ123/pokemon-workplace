from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from type_match_surface import build_type_match_surface  # noqa: E402


def main() -> None:
    result = build_type_match_surface(ROOT / "resources")
    print(result)


if __name__ == "__main__":
    main()
