from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from type_match_surface import build_type_match_surface  # noqa: E402


def main() -> None:
    result = build_type_match_surface(ROOT / "resources")
    assert result["profile_count"] == 12504
    assert result["distinct_attacker_type_sets"] == 21
    assert result["multi_type_profile_count"] == 16
    assert result["multi_weakness_profile_count"] == 2
    assert result["multi_resistance_profile_count"] == 0
    assert result["ambiguous_weakness_cases"] == []
    assert result["ambiguous_resistance_cases"] == []
    print(result)


if __name__ == "__main__":
    main()
