from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.multi_unit_energy_semantics import build  # noqa: E402


def main() -> None:
    result = build(ROOT / "resources")
    energy = result["multi_unit_energy"]
    discard = result["generic_self_discard_attacks"]

    assert energy["print_instances"] == 30
    assert energy["distinct_names"] == 13
    assert energy["text_signatures"] == 14

    names = {row["card_name"] for row in energy["rows"]}
    assert "Ignition Energy" in names
    assert "Double Dragon Energy" in names
    assert "Triple Acceleration Energy" in names

    ignition = [
        row
        for row in energy["rows"]
        if row["card_name"] == "Ignition Energy"
    ]
    assert len(ignition) == 1
    assert ignition[0]["maximum_units"] == 3

    double_dragon = [
        row
        for row in energy["rows"]
        if row["card_name"] == "Double Dragon Energy"
    ]
    assert len(double_dragon) == 1
    assert double_dragon[0]["maximum_units"] == 2

    assert discard == {
        "print_instances": 615,
        "distinct_signatures": 322,
        "signature_counts_by_required_energy": {
            "1": 130,
            "2": 92,
            "3": 25,
            "all": 75,
        },
        "fixed_two_or_more_signatures": 117,
    }

    print({
        "multi_unit_energy": {
            "print_instances": energy["print_instances"],
            "distinct_names": energy["distinct_names"],
            "text_signatures": energy["text_signatures"],
        },
        "generic_self_discard_attacks": discard,
    })


if __name__ == "__main__":
    main()
