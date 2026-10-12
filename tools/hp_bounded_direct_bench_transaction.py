"""Card-grounded HP-limited deck-to-Bench Item searches.

Buddy-Buddy Poffin has a typed *printed HP* restriction that cannot be
represented by the generic Basic Pokemon selector alone. This adapter keeps
the restriction at the transaction boundary, validates exact legal print
identity against trusted card metadata, and reuses the existing conserved
Trainer lifecycle and direct-to-Bench materialization.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Mapping, Sequence

from direct_bench_search_execution import (
    DirectBenchPlacement,
    DirectBenchTarget,
    direct_bench_target_from_metadata,
)
from direct_bench_search_profile_compiler import (
    DirectBenchSearchProfile,
    _legal_expanded_cards,
    _normalized,
)
from direct_bench_trainer_transaction import (
    DirectBenchTrainerExecutionState,
    DirectBenchTrainerTransaction,
    execute_direct_bench_trainer_transaction,
)
from pokemon_board_metadata import PokemonBoardMetadata
from pokemon_card_profile import PokemonCardProfile
from trainer_search_profile_compiler import SearchOutput
from typed_search_target_allocator import DemandChannel, TypedTargetAction


_HP_DIRECT_BENCH_RE = re.compile(
    r"^Search your deck for up to ([1-9][0-9]*) Basic Pok[eé]mon "
    r"with ([1-9][0-9]*) HP or less and put them onto your Bench\. "
    r"Then, shuffle your deck\.$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class HPBoundedDirectBenchProfile:
    """A legal Item print with a separate immutable printed-HP ceiling."""

    direct: DirectBenchSearchProfile
    max_hp: int

    def __post_init__(self) -> None:
        if self.direct.source_kind != "trainer" or self.direct.action_class != "Item":
            raise ValueError("HP-bounded adapter currently supports Item Trainers only")
        if self.max_hp <= 0:
            raise ValueError("max_hp must be positive")


def compile_hp_bounded_direct_bench_profiles(
    resources_root: Path = Path("resources"),
) -> tuple[HPBoundedDirectBenchProfile, ...]:
    """Conservatively compile literal HP-capped Basic-to-Bench Items."""

    found: list[HPBoundedDirectBenchProfile] = []
    for card in _legal_expanded_cards(resources_root):
        if card.get("supertype") != "Trainer":
            continue
        if "Item" not in (card.get("subtypes") or ()):
            continue

        rules = tuple(_normalized(rule) for rule in (card.get("rules") or ()))
        matches = tuple(
            match
            for rule in rules
            if (match := _HP_DIRECT_BENCH_RE.fullmatch(rule)) is not None
        )
        if len(matches) != 1:
            continue
        if any(
            not _HP_DIRECT_BENCH_RE.fullmatch(rule)
            and not rule.casefold().startswith((
                "you may play any number of item cards",
                "you may play as many item cards as you like",
            ))
            for rule in rules
        ):
            continue

        match = matches[0]
        maximum, max_hp = int(match.group(1)), int(match.group(2))
        direct = DirectBenchSearchProfile(
            card_id=card["id"],
            name=card["name"],
            source_kind="trainer",
            action_class="Item",
            source_name=None,
            output=SearchOutput("Basic Pokémon", maximum),
            explicit_up_to=True,
        )
        found.append(HPBoundedDirectBenchProfile(direct, max_hp))

    return tuple(sorted(found, key=lambda row: (row.direct.name, row.direct.card_id)))


def execute_hp_bounded_direct_bench_trainer_transaction(
    state: DirectBenchTrainerExecutionState,
    profile: HPBoundedDirectBenchProfile,
    *,
    action_card_class: str,
    demands: Sequence[DemandChannel],
    targets: Sequence[DirectBenchTarget],
    search_action: TypedTargetAction,
    placements: Sequence[DirectBenchPlacement],
    board_metadata_by_id: Mapping[str, PokemonBoardMetadata],
    card_profiles_by_id: Mapping[str, PokemonCardProfile],
) -> DirectBenchTrainerTransaction:
    """Pay and Bench exact eligible prints in one conserved Item transaction.

    The full declared target universe must consist of eligible prints.
    An optimizer may keep ineligible Pokémon in its wider deck model, but must
    not pass them as Poffin-search candidates into this typed action.
    """

    if action_card_class != profile.direct.card_id:
        raise ValueError("played Item print disagrees with compiled profile")

    for target in targets:
        print_id = target.search_target.card_class
        metadata = board_metadata_by_id.get(print_id)
        card_profile = card_profiles_by_id.get(print_id)
        if metadata is None or card_profile is None:
            raise ValueError(f"no trusted legal Pokemon metadata for {print_id!r}")
        trusted = direct_bench_target_from_metadata(
            metadata,
            copies=target.search_target.group.copies,
        )
        if target != trusted or card_profile.name != metadata.name:
            raise ValueError(f"target metadata disagrees with exact print {print_id!r}")
        if card_profile.hp > profile.max_hp:
            raise ValueError(
                f"{print_id!r} has {card_profile.hp} printed HP, "
                f"exceeding search limit {profile.max_hp}"
            )

    return execute_direct_bench_trainer_transaction(
        state,
        profile.direct,
        action_card_class=action_card_class,
        demands=demands,
        targets=targets,
        search_action=search_action,
        placements=placements,
    )
