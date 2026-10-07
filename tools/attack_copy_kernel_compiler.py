"""Lower card-grounded attack-copy contracts into executable kernel definitions."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from attack_copy_contracts import build as build_contracts
from attack_copy_kernel import AttackDef, CopySelector
from simple_attack_board_semantics import legal_cards


@dataclass(frozen=True)
class CompiledCopyAttack:
    card_id: str
    card_name: str
    attack_index: int
    source_class: str
    definition: AttackDef


def _base_selector(source_class: str) -> CopySelector:
    if source_class == "own_discard_dragon":
        return CopySelector("own_discard", required_type="Dragon")
    if source_class == "own_bench_fusion_strike":
        return CopySelector("own_bench", required_subtype="Fusion Strike")
    if source_class == "own_bench_named_n":
        return CopySelector("own_bench", required_name_prefix="N's ")
    if source_class == "own_bench_any":
        return CopySelector("own_bench")
    if source_class == "self_previous_evolution":
        return CopySelector("self_previous_evolution")
    if source_class == "own_deck_top_card":
        return CopySelector("own_deck_top")
    if source_class == "opponent_deck_top10":
        return CopySelector("opponent_revealed")
    if source_class == "opponent_hand":
        return CopySelector("opponent_hand")
    if source_class == "opponent_last_attack":
        return CopySelector("opponent_last_attack")
    if source_class == "opponent_active_tera":
        return CopySelector("opponent_active", required_subtype="Tera")
    if source_class == "opponent_active_non_gx":
        return CopySelector("opponent_active", require_non_gx=True)
    if source_class == "opponent_active_any":
        return CopySelector("opponent_active")
    if source_class == "opponent_in_play":
        return CopySelector("opponent_in_play")
    if source_class == "opponent_chooses_in_play":
        return CopySelector("opponent_in_play", chooser="opponent")
    if source_class == "opponent_any_pokemon":
        return CopySelector("opponent_in_play")
    raise ValueError(f"unsupported copy source class: {source_class}")


def _apply_contract(
    base: CopySelector,
    contract: dict,
) -> CopySelector:
    from dataclasses import replace

    selector = replace(
        base,
        require_non_gx=(
            base.require_non_gx
            or contract["direct_non_gx_filter"]
        ),
        optional_selection=contract["optional_selection"],
    )
    semantics = set(contract["non_tail_semantics"])
    if "selected_energy_gate" in semantics:
        selector = replace(selector, require_selected_energy=True)
    if "selected_source_zone_commit" in semantics:
        selector = replace(selector, move_selected_source_to="discard")
    if "preselection_source_zone_commit" in semantics:
        selector = replace(selector, precommit_source_to="discard")
    return selector


def compile_copy_attacks(resources_root: Path) -> tuple[CompiledCopyAttack, ...]:
    contracts = build_contracts(resources_root)["contracts"]
    contract_by_key = {
        (row["attack_name"], tuple(row["print_ids"])): row
        for row in contracts
    }

    contract_for_print: dict[tuple[str, str, str], dict] = {}
    for row in contracts:
        for print_id in row["print_ids"]:
            contract_for_print[(print_id, row["attack_name"], row.get("trailing_semantics", ""))] = row

    output: list[CompiledCopyAttack] = []
    for card in legal_cards(resources_root):
        for attack_index, attack in enumerate(card.get("attacks") or ()):
            text = attack.get("text") or ""
            if "as this attack" not in text.casefold():
                continue
            matches = [
                row
                for row in contracts
                if card["id"] in row["print_ids"]
                and row["attack_name"] == (attack.get("name") or "")
            ]
            if len(matches) != 1:
                raise ValueError(
                    f"expected one copy contract for {card['id']} "
                    f"{attack.get('name')!r}; found {len(matches)}"
                )
            contract = matches[0]
            source_classes = tuple(contract["source_classes"])
            if len(source_classes) != 1:
                raise ValueError(
                    f"copy print has ambiguous source classes: {source_classes}"
                )
            source_class = source_classes[0]
            selector = _apply_contract(
                _base_selector(source_class),
                contract,
            )

            semantics = set(contract["non_tail_semantics"])
            pre_event = None
            post_event = None
            if source_class == "opponent_deck_top10":
                pre_event = "reveal_top_10"
            if "post_copy_continuation" in semantics:
                post_event = "shuffle_revealed"

            definition = AttackDef(
                attack_id=f"{card['id']}:attack:{attack_index}",
                name=attack.get("name") or "",
                is_gx=(attack.get("name") or "").endswith("-GX"),
                copy_selector=selector,
                pre_event=pre_event,
                post_event=post_event,
                energy_cost=tuple(attack.get("cost") or ()),
            )
            output.append(
                CompiledCopyAttack(
                    card_id=card["id"],
                    card_name=card["name"],
                    attack_index=attack_index,
                    source_class=source_class,
                    definition=definition,
                )
            )

    return tuple(output)
