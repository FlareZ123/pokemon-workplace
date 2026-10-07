from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.attack_discard_dependency_grammar import build  # noqa: E402


def signatures_with_name(group: dict, attack_name: str) -> list[dict]:
    return [row for row in group["signatures"] if row["attack_name"] == attack_name]


def main() -> None:
    result = build(ROOT / "resources")
    mandatory = result["groups"]["mandatory_discard"]
    optional = result["groups"]["optional_discard"]

    assert mandatory["print_instances"] == 1346
    assert mandatory["distinct_signatures"] == 757
    assert mandatory["marker_counts"] == {
        "discarded_in_this_way": 75,
        "if_you_do": 27,
        "if_you_dont": 2,
        "none": 651,
        "then": 8,
    }
    assert mandatory["combination_counts"] == {
        "discarded_in_this_way": 69,
        "discarded_in_this_way+then": 5,
        "if_you_do": 26,
        "if_you_do+discarded_in_this_way": 1,
        "if_you_dont": 2,
        "none": 651,
        "then": 3,
    }

    assert optional["print_instances"] == 174
    assert optional["distinct_signatures"] == 84
    assert optional["marker_counts"] == {
        "discarded_in_this_way": 19,
        "if_you_do": 45,
        "none": 21,
        "then": 2,
    }
    assert optional["combination_counts"] == {
        "discarded_in_this_way": 16,
        "if_you_do": 42,
        "if_you_do+discarded_in_this_way": 3,
        "none": 21,
        "then": 2,
    }

    crimson = signatures_with_name(mandatory, "Crimson Blaster")
    assert len(crimson) == 1
    assert crimson[0]["markers"] == ["none"]

    grounding = signatures_with_name(mandatory, "Intentional Grounding")
    assert len(grounding) == 1
    assert grounding[0]["markers"] == ["if_you_dont"]

    spiral = signatures_with_name(mandatory, "Spiral Jet")
    assert len(spiral) == 1
    assert spiral[0]["markers"] == ["if_you_dont"]

    print({
        "mandatory": {
            "print_instances": mandatory["print_instances"],
            "distinct_signatures": mandatory["distinct_signatures"],
            "marker_counts": mandatory["marker_counts"],
        },
        "optional": {
            "print_instances": optional["print_instances"],
            "distinct_signatures": optional["distinct_signatures"],
            "marker_counts": optional["marker_counts"],
        },
    })


if __name__ == "__main__":
    main()
