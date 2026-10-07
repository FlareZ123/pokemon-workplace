"""Static composition analysis for Expanded attack-copy effects.

This module builds an intentionally permissive compatibility graph from the
attack-copy catalog, then adds a small correlation-aware check for nested paths
that reuse singleton state variables such as the opponent Active slot or the
opponent's last declared attack.
"""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Any

from attack_copy_catalog import OFFICIAL_BAN_OVERLAY, build as build_copy_catalog, load_json


def legal_cards(resources_root: Path) -> list[dict[str, Any]]:
    sets = load_json(resources_root / "sets" / "en.json")
    expanded_sets = {
        entry["id"]
        for entry in sets
        if (entry.get("legalities") or {}).get("expanded") == "Legal"
    }
    rows: list[dict[str, Any]] = []
    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        if path.stem not in expanded_sets:
            continue
        for card in load_json(path):
            if card["id"] in OFFICIAL_BAN_OVERLAY:
                continue
            if (card.get("legalities") or {}).get("expanded") == "Banned":
                continue
            rows.append(card)
    return rows


def has_rule_box(card: dict[str, Any]) -> bool:
    return bool(card.get("rules"))


def _ordinary_source_matches(source_class: str, card: dict[str, Any]) -> bool:
    if source_class in {
        "opponent_active_any",
        "opponent_active_non_gx",
        "opponent_any_pokemon",
        "opponent_chooses_in_play",
        "opponent_deck_top10",
        "opponent_hand",
        "opponent_in_play",
        "opponent_last_attack",
        "own_bench_any",
    }:
        return True
    if source_class == "own_bench_fusion_strike":
        return "Fusion Strike" in (card.get("subtypes") or [])
    if source_class == "own_bench_named_n":
        return (card.get("name") or "").startswith("N's ")
    if source_class == "own_discard_dragon":
        return "Dragon" in (card.get("types") or [])
    if source_class == "opponent_active_tera":
        return "Tera" in (card.get("subtypes") or [])
    if source_class == "own_deck_top_card":
        return not has_rule_box(card)
    if source_class == "self_previous_evolution":
        return False
    raise ValueError(f"Unknown source class: {source_class}")


def _previous_evolution_names(
    card: dict[str, Any],
    cards_by_name: dict[str, list[dict[str, Any]]],
) -> set[str]:
    seen: set[str] = set()
    frontier = [card.get("evolvesFrom")]
    while frontier:
        name = frontier.pop()
        if not name or name in seen:
            continue
        seen.add(name)
        for previous in cards_by_name.get(name, []):
            frontier.append(previous.get("evolvesFrom"))
    return seen


def signature_can_select_card(
    signature: dict[str, Any],
    target_card: dict[str, Any],
    *,
    by_id: dict[str, dict[str, Any]],
    cards_by_name: dict[str, list[dict[str, Any]]],
) -> bool:
    for source_class in signature["source_classes"]:
        if source_class != "self_previous_evolution":
            if _ordinary_source_matches(source_class, target_card):
                return True
            continue
        for source_id in signature["print_ids"]:
            source_card = by_id[source_id]
            if target_card.get("name") in _previous_evolution_names(source_card, cards_by_name):
                return True
    return False


def copy_edge_possible(
    source_signature: dict[str, Any],
    target_signature: dict[str, Any],
    *,
    by_id: dict[str, dict[str, Any]],
    cards_by_name: dict[str, list[dict[str, Any]]],
) -> bool:
    if source_signature["direct_non_gx_filter"] and target_signature["attack_name"].endswith("-GX"):
        return False
    return any(
        signature_can_select_card(
            source_signature,
            by_id[target_id],
            by_id=by_id,
            cards_by_name=cards_by_name,
        )
        for target_id in target_signature["print_ids"]
    )


def gx_attack_rows(cards: list[dict[str, Any]]) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    return [
        (card, attack)
        for card in cards
        for attack in (card.get("attacks") or [])
        if (attack.get("name") or "").endswith("-GX")
    ]


def direct_gx_endpoints(
    signature: dict[str, Any],
    gx_rows: list[tuple[dict[str, Any], dict[str, Any]]],
    *,
    by_id: dict[str, dict[str, Any]],
    cards_by_name: dict[str, list[dict[str, Any]]],
) -> set[tuple[str, str]]:
    if signature["direct_non_gx_filter"]:
        return set()
    return {
        (attack["name"], attack.get("text") or "")
        for card, attack in gx_rows
        if signature_can_select_card(
            signature,
            card,
            by_id=by_id,
            cards_by_name=cards_by_name,
        )
    }


def _singleton_binding(source_class: str) -> str | None:
    if source_class in {"opponent_active_any", "opponent_active_non_gx", "opponent_active_tera"}:
        return "opponent_active_card"
    if source_class == "opponent_last_attack":
        return "opponent_last_attack"
    return None


def _same_card_gx_endpoints(
    middle_signature: dict[str, Any],
    *,
    by_id: dict[str, dict[str, Any]],
) -> set[tuple[str, str]]:
    endpoints: set[tuple[str, str]] = set()
    for print_id in middle_signature["print_ids"]:
        card = by_id[print_id]
        for attack in card.get("attacks") or []:
            if (attack.get("name") or "").endswith("-GX"):
                endpoints.add((attack["name"], attack.get("text") or ""))
    return endpoints


def correlation_aware_two_hop_gx_endpoints(
    outer: dict[str, Any],
    middle: dict[str, Any],
    *,
    by_id: dict[str, dict[str, Any]],
    cards_by_name: dict[str, list[dict[str, Any]]],
    gx_rows: list[tuple[dict[str, Any], dict[str, Any]]],
) -> set[tuple[str, str]]:
    if not copy_edge_possible(outer, middle, by_id=by_id, cards_by_name=cards_by_name):
        return set()
    if middle["attack_name"].endswith("-GX"):
        return set()

    ordinary = direct_gx_endpoints(
        middle,
        gx_rows,
        by_id=by_id,
        cards_by_name=cards_by_name,
    )
    if not ordinary:
        return set()

    outer_bindings = {_singleton_binding(source) for source in outer["source_classes"]}
    inner_bindings = {_singleton_binding(source) for source in middle["source_classes"]}
    shared = (outer_bindings & inner_bindings) - {None}
    if not shared:
        return ordinary

    if "opponent_last_attack" in shared:
        return set()
    if "opponent_active_card" in shared:
        return _same_card_gx_endpoints(middle, by_id=by_id)
    return ordinary


def strongly_connected_components(node_count: int, edges: set[tuple[int, int]]) -> list[list[int]]:
    adjacency: dict[int, list[int]] = defaultdict(list)
    for source, target in edges:
        adjacency[source].append(target)

    index = 0
    stack: list[int] = []
    on_stack: set[int] = set()
    indices: dict[int, int] = {}
    lowlink: dict[int, int] = {}
    components: list[list[int]] = []

    def visit(node: int) -> None:
        nonlocal index
        indices[node] = index
        lowlink[node] = index
        index += 1
        stack.append(node)
        on_stack.add(node)

        for target in adjacency[node]:
            if target not in indices:
                visit(target)
                lowlink[node] = min(lowlink[node], lowlink[target])
            elif target in on_stack:
                lowlink[node] = min(lowlink[node], indices[target])

        if lowlink[node] != indices[node]:
            return
        component: list[int] = []
        while True:
            target = stack.pop()
            on_stack.remove(target)
            component.append(target)
            if target == node:
                break
        components.append(sorted(component))

    for node in range(node_count):
        if node not in indices:
            visit(node)
    return sorted(components, key=lambda rows: (-len(rows), rows))


def build(resources_root: Path) -> dict[str, Any]:
    cards = legal_cards(resources_root)
    by_id = {card["id"]: card for card in cards}
    cards_by_name: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for card in cards:
        cards_by_name[card.get("name") or ""].append(card)

    catalog = build_copy_catalog(resources_root)
    signatures = catalog["signatures"]
    edges = {
        (source_index, target_index)
        for source_index, source in enumerate(signatures)
        for target_index, target in enumerate(signatures)
        if copy_edge_possible(source, target, by_id=by_id, cards_by_name=cards_by_name)
    }
    components = strongly_connected_components(len(signatures), edges)
    gx_rows = gx_attack_rows(cards)
    gx_signatures = {(attack["name"], attack.get("text") or "") for _, attack in gx_rows}

    restricted_rows = []
    for outer_index, outer in enumerate(signatures):
        if not outer["direct_non_gx_filter"]:
            continue
        naive_intermediaries = []
        correlated_intermediaries = []
        correlated_endpoints: set[tuple[str, str]] = set()
        for middle_index, middle in enumerate(signatures):
            if (outer_index, middle_index) not in edges or middle["attack_name"].endswith("-GX"):
                continue
            ordinary = direct_gx_endpoints(
                middle,
                gx_rows,
                by_id=by_id,
                cards_by_name=cards_by_name,
            )
            if not ordinary:
                continue
            label = {
                "attack_name": middle["attack_name"],
                "card_names": middle["card_names"],
                "source_classes": middle["source_classes"],
                "direct_gx_signature_count": len(ordinary),
            }
            naive_intermediaries.append(label)
            correlated = correlation_aware_two_hop_gx_endpoints(
                outer,
                middle,
                by_id=by_id,
                cards_by_name=cards_by_name,
                gx_rows=gx_rows,
            )
            if correlated:
                correlated_intermediaries.append({**label, "correlated_gx_signature_count": len(correlated)})
                correlated_endpoints.update(correlated)

        restricted_rows.append(
            {
                "outer_attack_name": outer["attack_name"],
                "outer_card_names": outer["card_names"],
                "source_classes": outer["source_classes"],
                "naive_gx_bypass_intermediary_count": len(naive_intermediaries),
                "correlation_aware_gx_bypass_intermediary_count": len(correlated_intermediaries),
                "correlation_aware_unique_gx_endpoint_signatures": len(correlated_endpoints),
                "naive_intermediaries": naive_intermediaries,
                "correlation_aware_intermediaries": correlated_intermediaries,
            }
        )

    direct_gx_counts = []
    for signature in signatures:
        endpoints = direct_gx_endpoints(
            signature,
            gx_rows,
            by_id=by_id,
            cards_by_name=cards_by_name,
        )
        if endpoints:
            direct_gx_counts.append(
                {
                    "attack_name": signature["attack_name"],
                    "card_names": signature["card_names"],
                    "source_classes": signature["source_classes"],
                    "gx_endpoint_signature_count": len(endpoints),
                }
            )

    return {
        "scope": catalog["scope"],
        "graph": {
            "node_count": len(signatures),
            "edge_count": len(edges),
            "possible_directed_pairs": len(signatures) ** 2,
            "density_including_self_edges": len(edges) / (len(signatures) ** 2),
            "self_edge_count": sum((node, node) in edges for node in range(len(signatures))),
            "strongly_connected_component_sizes": [len(component) for component in components],
            "largest_scc": [
                {
                    "attack_name": signatures[index]["attack_name"],
                    "card_names": signatures[index]["card_names"],
                }
                for index in components[0]
            ],
        },
        "gx_endpoint_pool": {
            "gx_attack_print_rows": len(gx_rows),
            "unique_gx_attack_signatures": len(gx_signatures),
            "unique_gx_pokemon_names": len({card["name"] for card, _ in gx_rows}),
        },
        "copy_signatures_with_direct_gx_access": direct_gx_counts,
        "non_gx_gate_composition": restricted_rows,
        "interpretation": [
            "The pairwise graph is intentionally existential: each edge only means some legal state can satisfy that one copy selection.",
            "Pairwise edges are not automatically composable because adjacent edges can bind to the same state variable.",
            "The correlation-aware two-hop check currently handles repeated opponent Active and opponent-last-attack singleton bindings; it is not a complete constraint solver.",
            "GX endpoint reachability means the attack body can be selected under the modeled filters, not that every copied attack will have useful damage or effects in that state.",
        ],
    }


def atomic_write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, indent=2, ensure_ascii=False) + "\n"
    lock_path = path.with_suffix(path.suffix + ".lock")
    with lock_path.open("a+b") as lock_file:
        if os.name == "nt":
            import msvcrt
            msvcrt.locking(lock_file.fileno(), msvcrt.LK_LOCK, 1)
        else:
            import fcntl
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)

        tmp_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as tmp_file:
                tmp_file.write(payload)
                tmp_file.flush()
                os.fsync(tmp_file.fileno())
                tmp_path = Path(tmp_file.name)
            os.replace(tmp_path, path)
        finally:
            if tmp_path is not None and tmp_path.exists():
                tmp_path.unlink()


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze composability of Expanded attack-copy effects.")
    parser.add_argument("--resources-root", type=Path, default=Path("resources"))
    parser.add_argument("--output", type=Path, default=Path("results/attack_copy_semantics/composition.json"))
    args = parser.parse_args()
    result = build(args.resources_root)
    atomic_write_json(args.output, result)
    print(json.dumps({"graph": result["graph"], "gx_endpoint_pool": result["gx_endpoint_pool"]}, indent=2, ensure_ascii=False))
    print(json.dumps(result["non_gx_gate_composition"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
