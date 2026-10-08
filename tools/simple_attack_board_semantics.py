"""Conservative card-data compiler for simple attack board semantics.

The compiler exposes independent, audited semantic dimensions rather than
claiming to understand arbitrary attack text:

- plain numeric printed damage plus effect-only blank damage fields;
- seven exact damage-counter wording templates;
- unconditional "Take another turn after this one" directives.

Unknown text remains unknown. Downstream executors may compose only the
dimensions they explicitly support.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Iterable

from attack_copy_kernel import AttackDef, TurnBoundaryEffect
from attack_copy_physical_ko_bridge import PhysicalBoardEventProgram
from board_position_state import BoardState
from build_expanded_legality_baseline import classify_effective_legality
from damage_board_bridge import EffectCounterPlacement
from damage_calculation_kernel import AttackDamage, DamageContext


@dataclass(frozen=True)
class CounterEffectContract:
    scope: str
    total_counters: int
    distribution: str

    def __post_init__(self) -> None:
        if self.total_counters <= 0:
            raise ValueError("counter effect must place at least one counter")
        if self.distribution not in {"fixed", "single", "distributed"}:
            raise ValueError("unsupported counter distribution")


@dataclass(frozen=True)
class CompiledAttackBoardSemantics:
    card_id: str
    card_name: str
    attack_index: int
    attack_name: str
    energy_cost: tuple[str, ...]
    fixed_damage: int | None
    counter_effect: CounterEffectContract | None
    has_uncompiled_damage_text: bool
    has_uncompiled_knockout_text: bool
    has_uncompiled_attack_gate: bool
    take_another_turn: bool
    skip_pokemon_checkup: bool
    is_gx_attack: bool
    ignore_weakness: bool
    ignore_resistance: bool
    ignore_weakness_resistance: bool
    ignore_defender_effects: bool
    raw_damage: str
    raw_text: str

    @property
    def attack_id(self) -> str:
        return f"{self.card_id}:attack:{self.attack_index}"

    @property
    def event_label(self) -> str:
        return f"body:{self.card_id}:attack:{self.attack_index}"

    def to_leaf_attack_def(self) -> AttackDef:
        boundary = None
        if self.take_another_turn:
            boundary = TurnBoundaryEffect(
                take_another_turn=True,
                skip_pokemon_checkup=self.skip_pokemon_checkup,
            )
        return AttackDef(
            self.attack_id,
            self.attack_name,
            is_gx=self.is_gx_attack,
            effect_label=self.event_label,
            turn_boundary_effect=boundary,
            energy_cost=self.energy_cost,
        )


_COUNTER_PATTERNS: tuple[tuple[str, str, re.Pattern[str]], ...] = (
    (
        "opponent_active",
        "fixed",
        re.compile(
            r"^Put (\d+) damage counters on your opponent's Active Pokémon\.$",
            re.IGNORECASE,
        ),
    ),
    (
        "opponent_any",
        "single",
        re.compile(
            r"^Put (\d+) damage counters on 1 of your opponent's Pokémon\.$",
            re.IGNORECASE,
        ),
    ),
    (
        "opponent_any",
        "distributed",
        re.compile(
            r"^Put (\d+) damage counters on your opponent's Pokémon in any way you like\.$",
            re.IGNORECASE,
        ),
    ),
    (
        "opponent_bench",
        "single",
        re.compile(
            r"^Put (\d+) damage counters on 1 of your opponent's Benched Pokémon\.$",
            re.IGNORECASE,
        ),
    ),
    (
        "opponent_bench",
        "distributed",
        re.compile(
            r"^Put (\d+) damage counters on your opponent's Benched Pokémon in any way you like\.$",
            re.IGNORECASE,
        ),
    ),
    (
        "own_any",
        "single",
        re.compile(
            r"^Put (\d+) damage counters on 1 of your Pokémon\.$",
            re.IGNORECASE,
        ),
    ),
    (
        "self",
        "fixed",
        re.compile(
            r"^Put (\d+) damage counters on this Pokémon\.$",
            re.IGNORECASE,
        ),
    ),
)


_UNCOMPILED_DAMAGE_PHRASE = re.compile(
    r"\b(?:do(?:es)?|deal(?:s)?|take(?:s)?)\b[^.!?]{0,90}\bdamage\b"
    r"|\b(?:put|place|move)\b[^.!?]{0,90}\bdamage counters?\b",
    re.IGNORECASE,
)


def _compile_counter_effect(text: str) -> CounterEffectContract | None:
    normalized = re.sub(r"\s+", " ", text).strip()
    for scope, distribution, pattern in _COUNTER_PATTERNS:
        match = pattern.fullmatch(normalized)
        if match is not None:
            return CounterEffectContract(
                scope=scope,
                total_counters=int(match.group(1)),
                distribution=distribution,
            )
    return None


def compile_attack(
    card: dict,
    attack_index: int,
) -> CompiledAttackBoardSemantics:
    attacks = card.get("attacks") or ()
    attack = attacks[attack_index]
    raw_damage = (attack.get("damage") or "").strip()
    raw_text = re.sub(r"\s+", " ", attack.get("text") or "").strip()

    fixed_damage = (
        0
        if raw_damage == ""
        else int(raw_damage)
        if re.fullmatch(r"\d+", raw_damage)
        else None
    )
    extra_turn = "Take another turn after this one." in raw_text
    skip_checkup = (
        extra_turn
        and (
            "(Skip the between-turns step.)" in raw_text
            or "(Skip Pokémon Checkup.)" in raw_text
        )
    )

    counter_effect = _compile_counter_effect(raw_text)
    has_uncompiled_damage_text = (
        counter_effect is None
        and _UNCOMPILED_DAMAGE_PHRASE.search(raw_text) is not None
    )

    has_uncompiled_knockout_text = (
        re.search(r"\bknock(?:ed)?[\s-]+out\b", raw_text, re.IGNORECASE)
        is not None
    )

    has_uncompiled_attack_gate = (
        re.search(
            r"\b(?:this attack (?:does nothing|doesn't happen|can't be used|cannot be used)"
            r"|you (?:can't|cannot) use this attack)\b",
            raw_text,
            re.IGNORECASE,
        )
        is not None
    )

    lowered_text = raw_text.casefold()
    ignore_both = (
        "damage isn't affected by weakness or resistance" in lowered_text
        or "damage isn't affected by weakness, resistance" in lowered_text
    )
    ignore_weakness = (
        ignore_both or "damage isn't affected by weakness" in lowered_text
    )
    ignore_resistance = (
        ignore_both or "damage isn't affected by resistance" in lowered_text
    )
    ignore_weakness_resistance = ignore_weakness and ignore_resistance
    ignore_defender_effects = (
        "damage isn't affected by" in lowered_text
        and (
            "effects on your opponent's active pokémon" in lowered_text
            or "effects on the defending pokémon" in lowered_text
        )
    )

    return CompiledAttackBoardSemantics(
        card_id=card["id"],
        card_name=card["name"],
        attack_index=attack_index,
        attack_name=attack.get("name") or "",
        energy_cost=tuple(attack.get("cost") or ()),
        fixed_damage=fixed_damage,
        counter_effect=counter_effect,
        has_uncompiled_damage_text=has_uncompiled_damage_text,
        has_uncompiled_knockout_text=has_uncompiled_knockout_text,
        has_uncompiled_attack_gate=has_uncompiled_attack_gate,
        take_another_turn=extra_turn,
        skip_pokemon_checkup=skip_checkup,
        is_gx_attack=(attack.get("name") or "").endswith("-GX"),
        ignore_weakness=ignore_weakness,
        ignore_resistance=ignore_resistance,
        ignore_weakness_resistance=ignore_weakness_resistance,
        ignore_defender_effects=ignore_defender_effects,
        raw_damage=raw_damage,
        raw_text=raw_text,
    )


def compile_card(card: dict) -> tuple[CompiledAttackBoardSemantics, ...]:
    return tuple(
        compile_attack(card, index)
        for index, _attack in enumerate(card.get("attacks") or ())
    )


def legal_cards(resources_root: Path) -> tuple[dict, ...]:
    sets = json.loads(
        (resources_root / "sets" / "en.json").read_text(encoding="utf-8")
    )
    expanded_sets = {
        row["id"]
        for row in sets
        if (row.get("legalities") or {}).get("expanded") == "Legal"
    }
    output: list[dict] = []
    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        if path.stem not in expanded_sets:
            continue
        for card in json.loads(path.read_text(encoding="utf-8")):
            if classify_effective_legality(card)[0] == "Legal":
                output.append(card)
    return tuple(output)


def compile_legal_index(
    resources_root: Path,
) -> dict[str, tuple[CompiledAttackBoardSemantics, ...]]:
    return {
        card["id"]: compile_card(card)
        for card in legal_cards(resources_root)
        if card.get("attacks")
    }


def _validate_opponent_allocation(
    board: BoardState,
    effect: CounterEffectContract,
    allocation: tuple[tuple[str, int], ...],
) -> None:
    if effect.scope not in {"opponent_active", "opponent_any", "opponent_bench"}:
        raise ValueError("effect is not an opponent-targeting counter effect")
    if len({target_id for target_id, _count in allocation}) != len(allocation):
        raise ValueError("counter allocation target IDs must be unique")
    if any(count < 0 for _target_id, count in allocation):
        raise ValueError("counter allocation cannot contain negative counts")
    if sum(count for _target_id, count in allocation) != effect.total_counters:
        raise ValueError("counter allocation must use the exact effect total")

    board_ids = {pokemon.pokemon_id for pokemon in board.pokemon}
    positive_targets = tuple(
        target_id
        for target_id, count in allocation
        if count > 0
    )
    if any(target_id not in board_ids for target_id in positive_targets):
        raise ValueError("counter allocation contains an unknown target")

    if effect.scope == "opponent_active":
        if positive_targets != (board.active_id,):
            raise ValueError("fixed Active counter effect must target the Active")
    elif effect.scope == "opponent_bench":
        bench = set(board.bench_ids)
        if any(target_id not in bench for target_id in positive_targets):
            raise ValueError("Bench counter effect cannot target the Active")

    if effect.distribution in {"fixed", "single"} and len(positive_targets) != 1:
        raise ValueError("counter effect requires exactly one positive target")


def materialize_opponent_board_program(
    semantics: CompiledAttackBoardSemantics,
    board: BoardState,
    *,
    counter_allocation: Iterable[tuple[str, int]] = (),
) -> PhysicalBoardEventProgram:
    """Materialize the supported opponent-facing board semantics.

    This helper supports plain numeric damage and effect-only attacks whose
    damage field is blank. Variable printed damage expressions remain outside
    this execution island.
    """

    if semantics.fixed_damage is None:
        raise ValueError("attack does not have supported fixed numeric damage")
    if semantics.has_uncompiled_damage_text:
        raise ValueError("attack has uncompiled damage text")
    if semantics.has_uncompiled_knockout_text:
        raise ValueError("attack has uncompiled Knock Out text")
    if semantics.has_uncompiled_attack_gate:
        raise ValueError("attack has an uncompiled attack-use gate")

    allocation = tuple(counter_allocation)
    placements: tuple[EffectCounterPlacement, ...] = ()
    if semantics.counter_effect is None:
        if allocation:
            raise ValueError("counter allocation supplied for attack without counter effect")
    else:
        _validate_opponent_allocation(board, semantics.counter_effect, allocation)
        placements = tuple(
            EffectCounterPlacement(target_id, count)
            for target_id, count in allocation
            if count > 0
        )

    return PhysicalBoardEventProgram(
        damage_target_id=board.active_id,
        damage_context=DamageContext(
            attack=AttackDamage(semantics.fixed_damage),
        ),
        counter_placements=placements,
    )
