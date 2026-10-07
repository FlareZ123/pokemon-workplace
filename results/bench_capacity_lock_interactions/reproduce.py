from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from bench_capacity_model import contraction_impact, effective_capacity
from bench_resource_catalog import build


def main() -> None:
    catalog = build(ROOT / "resources")
    capacity = {row["name"]: row for row in catalog["capacity_effects"]}

    assert capacity["Eternatus VMAX"]["effect_type"] == "extension"
    assert capacity["Sudowoodo"]["effect_type"] == "restriction"
    assert capacity["Glimmora ex"]["effect_type"] == "restriction"
    assert capacity["Sky Field"]["effect_type"] == "extension"

    sky_plus_roadblock = effective_capacity(
        extension_caps=(capacity["Sky Field"]["cap"],),
        restriction_caps=(capacity["Sudowoodo"]["cap"],),
    )
    sky_without_roadblock = effective_capacity(
        extension_caps=(capacity["Sky Field"]["cap"],),
    )
    assert sky_plus_roadblock == 4
    assert sky_without_roadblock == 8

    sky_plus_dust_field = effective_capacity(
        extension_caps=(capacity["Sky Field"]["cap"],),
        restriction_caps=(capacity["Glimmora ex"]["cap"],),
    )
    assert sky_plus_dust_field == 3
    assert sky_without_roadblock == 8

    eternatus_enabled = effective_capacity(
        extension_caps=(capacity["Eternatus VMAX"]["cap"],),
    )
    eternatus_suppressed = effective_capacity()
    assert eternatus_enabled == 8
    assert eternatus_suppressed == 5

    assert contraction_impact(8, 5, 0)["forced_discards"] == 3
    assert contraction_impact(8, 4, 0)["forced_discards"] == 4
    assert contraction_impact(8, 3, 0)["forced_discards"] == 5

    print("bench_capacity_lock_interactions: all checks passed")
    print("Sky Field + Roadblock:", sky_plus_roadblock, "-> suppress Roadblock:", sky_without_roadblock)
    print("Sky Field + Dust Field:", sky_plus_dust_field, "-> suppress Dust Field:", sky_without_roadblock)
    print("Eternal Zone:", eternatus_enabled, "-> suppress Eternal Zone:", eternatus_suppressed)


if __name__ == "__main__":
    main()
