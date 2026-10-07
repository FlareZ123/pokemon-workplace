from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from attack_copy_composition import build


def row_for(result: dict, attack_name: str) -> dict:
    rows = [row for row in result["non_gx_gate_composition"] if row["outer_attack_name"] == attack_name]
    assert len(rows) == 1
    return rows[0]


def main() -> None:
    result = build(ROOT / "resources")
    graph = result["graph"]
    gx = result["gx_endpoint_pool"]

    assert graph["node_count"] == 30
    assert graph["edge_count"] == 681
    assert graph["possible_directed_pairs"] == 900
    assert graph["self_edge_count"] == 26
    assert graph["strongly_connected_component_sizes"] == [23, 1, 1, 1, 1, 1, 1, 1]

    assert gx["gx_attack_print_rows"] == 606
    assert gx["unique_gx_attack_signatures"] == 193
    assert gx["unique_gx_pokemon_names"] == 171

    direct = {row["attack_name"]: row for row in result["copy_signatures_with_direct_gx_access"]}
    assert direct["Apex Dragon"]["gx_endpoint_signature_count"] == 18
    assert direct["Assist"]["gx_endpoint_signature_count"] == 193

    copycat = row_for(result, "Copycat")
    hypnotic = row_for(result, "Hypnotic Reign")
    shadow = row_for(result, "Shadow Imitation")

    assert (copycat["naive_gx_bypass_intermediary_count"], copycat["correlation_aware_gx_bypass_intermediary_count"]) == (19, 18)
    assert (hypnotic["naive_gx_bypass_intermediary_count"], hypnotic["correlation_aware_gx_bypass_intermediary_count"]) == (19, 19)
    assert (shadow["naive_gx_bypass_intermediary_count"], shadow["correlation_aware_gx_bypass_intermediary_count"]) == (19, 10)

    for row in (copycat, hypnotic, shadow):
        assert row["correlation_aware_unique_gx_endpoint_signatures"] == 193

    copycat_names = [row["attack_name"] for row in copycat["correlation_aware_intermediaries"]]
    shadow_names = [row["attack_name"] for row in shadow["correlation_aware_intermediaries"]]
    assert "Watch and Learn" not in copycat_names
    assert "Apex Dragon" in copycat_names
    assert "Apex Dragon" in shadow_names
    assert "Foul Play" not in shadow_names

    largest_names = {row["attack_name"] for row in graph["largest_scc"]}
    assert "Seek Inspiration" in largest_names
    assert "Copycat" in largest_names
    assert "Shadow Imitation" in largest_names

    print("attack-copy composition regressions passed")
    print({
        "edges": graph["edge_count"],
        "largest_scc": graph["strongly_connected_component_sizes"][0],
        "copycat": copycat["correlation_aware_gx_bypass_intermediary_count"],
        "hypnotic": hypnotic["correlation_aware_gx_bypass_intermediary_count"],
        "shadow": shadow["correlation_aware_gx_bypass_intermediary_count"],
    })


if __name__ == "__main__":
    main()
