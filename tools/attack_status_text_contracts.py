"""Conservative exact source contracts for attack-inflicted Special Conditions.

A contract identifies text semantics and a coin condition. It does not roll a
coin, assign status to a physical Pokémon, resolve immunity, or schedule the
between-turns Special Condition steps.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import re

from simple_attack_board_semantics import legal_cards


_STATUSES = "Poisoned|Burned|Asleep|Paralyzed|Confused"
_TARGET = "(?:The Defending Pokémon|Your opponent's Active Pokémon)"
_PLAIN = re.compile(
    rf"^(?P<target>{_TARGET}) is now (?P<status>{_STATUSES})\.$"
)
_COIN = re.compile(
    rf"^Flip a coin\. If (?P<result>heads|tails), "
    rf"(?P<target>{_TARGET}) is now (?P<status>{_STATUSES})\.$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class AttackStatusSourceContract:
    print_id: str
    card_name: str
    attack_name: str
    attack_index: int
    raw_damage: str
    raw_text: str
    special_condition: str
    requires_coin_result: str | None
    target_scope: str = "opponent_active"

    @property
    def attack_id(self) -> str:
        return f"{self.print_id}:attack:{self.attack_index}"


def compile_attack_status_source(
    card: dict, attack_index: int,
) -> AttackStatusSourceContract | None:
    attack = (card.get("attacks") or ())[attack_index]
    text = re.sub(r"\s+", " ", attack.get("text") or "").strip()
    ordinary = _PLAIN.fullmatch(text)
    coin = _COIN.fullmatch(text)
    if ordinary is None and coin is None:
        return None
    match = ordinary if ordinary is not None else coin
    assert match is not None
    return AttackStatusSourceContract(
        print_id=card["id"],
        card_name=card["name"],
        attack_name=attack["name"],
        attack_index=attack_index,
        raw_damage=attack.get("damage") or "",
        raw_text=text,
        special_condition=match.group("status").capitalize(),
        requires_coin_result=(
            coin.group("result").lower() if coin is not None else None
        ),
    )


def catalog_attack_status_sources(resources_root: Path) -> dict:
    rows = tuple(
        contract
        for card in legal_cards(resources_root)
        if card.get("supertype") == "Pokémon"
        for i, _attack in enumerate(card.get("attacks") or ())
        if (contract := compile_attack_status_source(card, i)) is not None
    )
    counts = Counter(
        (contract.special_condition, contract.requires_coin_result or "always")
        for contract in rows
    )
    return {
        "rows": rows,
        "total": len(rows),
        "counts": dict(sorted(counts.items())),
        "unconditional": sum(
            contract.requires_coin_result is None for contract in rows
        ),
        "coin_gated": sum(
            contract.requires_coin_result is not None for contract in rows
        ),
    }
