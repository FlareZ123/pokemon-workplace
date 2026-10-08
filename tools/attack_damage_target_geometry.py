"""Card-grounded target geometry for literal attack-text damage clauses.

Conservative full-text matching: lexical coverage is not executable coverage.
The module never silently certifies extra attack text or conditional prefixes.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import re
from typing import Mapping

from board_position_state import BoardState

from simple_attack_board_semantics import legal_cards


_BENCH_REMINDER = " (Don't apply Weakness and Resistance for Benched Pokémon.)"
_CLAUSE = re.compile(
    r"^(?:This attack (?P<also>also )?does|Does) "
    r"(?P<damage>\d+) damage to (?P<target>.+)\.$"
)
_NUMBER_TARGET = re.compile(
    r"(?P<count>[1-6]) of your opponent's (?P<bench>Benched )?Pokémon"
)
_EACH_TARGET = re.compile(
    r"each of your opponent's (?P<bench>Benched )?"
    r"(?P<filter>Basic |Evolution )?Pokémon(?P<ex> ex)?"
)


@dataclass(frozen=True)
class LiteralDamageGeometry:
    card_id: str
    card_name: str
    attack_name: str
    attack_index: int
    printed_active_damage: int
    text_damage: int
    target_scope: str
    target_filter: str | None
    target_count: int | None
    additional_to_printed: bool
    raw_text: str

    @property
    def attack_id(self) -> str:
        return f"{self.card_id}:attack:{self.attack_index}"


def compile_literal_damage_geometry(
    card: dict, attack_index: int
) -> LiteralDamageGeometry | None:
    attack = (card.get("attacks") or ())[attack_index]
    damage_field = (attack.get("damage") or "").strip()
    if damage_field and re.fullmatch(r"\d+", damage_field) is None:
        return None
    text = re.sub(r"\s+", " ", attack.get("text") or "").strip()
    clause = text
    if clause.endswith(_BENCH_REMINDER):
        clause = clause[: -len(_BENCH_REMINDER)]
    match = _CLAUSE.fullmatch(clause)
    if match is None:
        return None

    target = match.group("target")
    number = _NUMBER_TARGET.fullmatch(target)
    each = _EACH_TARGET.fullmatch(target)
    if number is not None:
        scope = "opponent_bench" if number.group("bench") else "opponent_any"
        count = int(number.group("count"))
        target_filter = None
    elif each is not None:
        scope = "opponent_bench" if each.group("bench") else "opponent_all"
        count = None
        target_filter = (
            "ex" if each.group("ex") else
            (each.group("filter") or "").strip() or None
        )
    else:
        return None

    # Explicit 'also' belongs with a nonzero printed Active damage component.
    # Keeping only literal known target shapes prevents premature execution.
    base = int(damage_field) if damage_field else 0
    if match.group("also") and not base:
        return None
    return LiteralDamageGeometry(
        card_id=card["id"],
        card_name=card["name"],
        attack_name=attack.get("name") or "",
        attack_index=attack_index,
        printed_active_damage=base,
        text_damage=int(match.group("damage")),
        target_scope=scope,
        target_filter=target_filter,
        target_count=count,
        additional_to_printed=base > 0,
        raw_text=text,
    )


def catalog(resources_root: Path) -> dict:
    rows = [
        geometry
        for card in legal_cards(resources_root)
        for i, _attack in enumerate(card.get("attacks") or ())
        if (geometry := compile_literal_damage_geometry(card, i)) is not None
    ]
    shapes = Counter(
        (g.target_scope, g.target_filter or "all", str(g.target_count or "each"))
        for g in rows
    )
    return {
        "rows": tuple(rows),
        "total_rows": len(rows),
        "effect_only_rows": sum(not g.additional_to_printed for g in rows),
        "supplemental_rows": sum(g.additional_to_printed for g in rows),
        "shapes": dict(sorted(shapes.items())),
    }


@dataclass(frozen=True)
class TargetDamageInstruction:
    target_id: str
    amount: int
    source: str
    ignore_weakness_resistance: bool


@dataclass(frozen=True)
class LiteralDamageTargetPlan:
    geometry: LiteralDamageGeometry
    selected_text_targets: tuple[str, ...]
    instructions: tuple[TargetDamageInstruction, ...]


def plan_literal_damage_targets(
    geometry: LiteralDamageGeometry,
    board: BoardState,
    *,
    selected_target_ids: tuple[str, ...] = (),
    target_tags_by_id: Mapping[str, frozenset[str]] | None = None,
) -> LiteralDamageTargetPlan:
    """Validate a complete target selection without executing damage.

    The board represents the opponent. Live target-tag membership is supplied
    explicitly for text filters; never infer it from physical instance IDs.
    For a fixed number, choose the number stated or all eligible if fewer
    exist. An 'each' attack necessarily targets every eligible Pokémon.
    """
    if geometry.target_scope in {"opponent_any", "opponent_all"}:
        possible = (board.active_id, *board.bench_ids)
    elif geometry.target_scope == "opponent_bench":
        possible = board.bench_ids
    else:
        raise ValueError("unrecognized target scope")

    if geometry.target_filter is None:
        eligible = possible
    else:
        if target_tags_by_id is None or any(
            target not in target_tags_by_id for target in possible
        ):
            raise ValueError("target subtype eligibility is not fully known")
        eligible = tuple(
            target for target in possible
            if geometry.target_filter in target_tags_by_id[target]
        )

    if geometry.target_count is None:
        if selected_target_ids:
            raise ValueError("'each' damage does not permit a subset")
        targets = tuple(eligible)
    else:
        required = min(geometry.target_count, len(eligible))
        if len(selected_target_ids) != required:
            raise ValueError("chosen target count disagrees with eligibility")
        if len(set(selected_target_ids)) != len(selected_target_ids):
            raise ValueError("chosen damage targets must be distinct")
        if any(target not in eligible for target in selected_target_ids):
            raise ValueError("chosen target is ineligible")
        targets = selected_target_ids

    instructions: list[TargetDamageInstruction] = []
    if geometry.printed_active_damage:
        instructions.append(
            TargetDamageInstruction(
                board.active_id,
                geometry.printed_active_damage,
                "printed",
                False,
            )
        )
    instructions.extend(
        TargetDamageInstruction(
            target,
            geometry.text_damage,
            "attack_text",
            target != board.active_id,
        )
        for target in targets
    )
    return LiteralDamageTargetPlan(
        geometry,
        targets,
        tuple(instructions),
    )
