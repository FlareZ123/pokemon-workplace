from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.energy_identity_semantics import build


def main() -> None:
    result = build(ROOT / "resources")
    refs = result["basic_named_references"]
    assert refs["print_text_instances"] == 344
    assert refs["distinct_texts"] == 152
    assert refs["by_source_kind"] == {
        "ability": 144,
        "attack": 156,
        "rule": 44,
    }
    assert refs["by_basic_energy_name"] == {
        "Darkness": 18,
        "Fighting": 53,
        "Fire": 78,
        "Grass": 49,
        "Lightning": 68,
        "Metal": 18,
        "Psychic": 40,
        "Water": 43,
    }

    overrides = result["type_override_effects"]
    assert overrides["print_instances"] == 4
    assert overrides["distinct_signatures"] == 3

    multiplicity = result["basic_named_multiplicity_effects"]
    assert multiplicity["print_instances"] == 6
    assert multiplicity["distinct_signatures"] == 5

    regression = result["semantic_regressions"]
    assert regression["basic_grass_under_energy_burn_and_wild_growth"] == {
        "matches_basic_grass_name": True,
        "matches_basic_fire_name": False,
        "can_pay_fire": True,
        "can_pay_grass": False,
        "energy_units": 2,
    }
    assert regression["double_dragon"] == {
        "matches_basic_psychic_name": False,
        "can_pay_psychic": True,
        "energy_units": 2,
    }

    print({
        "basic_named_references": refs,
        "type_override_count": overrides["distinct_signatures"],
        "multiplicity_count": multiplicity["distinct_signatures"],
        "semantic_regressions": regression,
    })


if __name__ == "__main__":
    main()
