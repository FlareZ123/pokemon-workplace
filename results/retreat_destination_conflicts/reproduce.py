"""Reproduce retreat Energy destination conflicts and prohibitions."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from retreat_destination_conflicts import (
    analyze_successful_retreat_energy_destination,
)


def main() -> None:
    ordinary = analyze_successful_retreat_energy_destination(
        dashing_pouch_active=False,
        opposing_scoop_up_block_active=False,
        holder_has_damage=False,
        energy_is_prism_star=False,
    )
    assert ordinary.resolved
    assert ordinary.destination_zone == "discard"

    dashing = analyze_successful_retreat_energy_destination(
        dashing_pouch_active=True,
        opposing_scoop_up_block_active=False,
        holder_has_damage=True,
        energy_is_prism_star=False,
    )
    assert dashing.destination_zone == "hand"

    blocked = analyze_successful_retreat_energy_destination(
        dashing_pouch_active=True,
        opposing_scoop_up_block_active=True,
        holder_has_damage=True,
        energy_is_prism_star=False,
    )
    assert blocked.destination_zone == "discard"
    assert blocked.prohibited_zones == ("hand",)

    undamaged = analyze_successful_retreat_energy_destination(
        dashing_pouch_active=True,
        opposing_scoop_up_block_active=True,
        holder_has_damage=False,
        energy_is_prism_star=False,
    )
    assert undamaged.destination_zone == "hand"

    prism = analyze_successful_retreat_energy_destination(
        dashing_pouch_active=False,
        opposing_scoop_up_block_active=False,
        holder_has_damage=False,
        energy_is_prism_star=True,
    )
    assert prism.destination_zone == "lost_zone"

    dashing_prism = analyze_successful_retreat_energy_destination(
        dashing_pouch_active=True,
        opposing_scoop_up_block_active=False,
        holder_has_damage=True,
        energy_is_prism_star=True,
    )
    assert not dashing_prism.resolved
    assert dashing_prism.requires_authority
    assert tuple(
        row.destination_zone for row in dashing_prism.candidates
    ) == ("hand", "lost_zone")

    blocked_prism = analyze_successful_retreat_energy_destination(
        dashing_pouch_active=True,
        opposing_scoop_up_block_active=True,
        holder_has_damage=True,
        energy_is_prism_star=True,
    )
    assert blocked_prism.resolved
    assert blocked_prism.destination_zone == "lost_zone"
    assert blocked_prism.prohibited_zones == ("hand",)

    print("Retreat destination conflict regressions passed")


if __name__ == "__main__":
    main()
