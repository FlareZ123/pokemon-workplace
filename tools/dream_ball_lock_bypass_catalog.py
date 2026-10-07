"""Cross-reference Dream Ball-compatible Evolution Abilities with lock effects.

This module joins the conservative Evolution-Ability geometry catalog to the
repository's lock-effect catalog at exact print ID + Ability name. It identifies
candidate locks Dream Ball can put onto the Bench while preserving lock
activation prerequisites such as Active position, Tool attachment, or Stadium.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from dream_ball_evolution_ability_catalog import (
    EvolutionAbilityCandidate,
    build_dream_ball_evolution_ability_catalog,
)
from lock_effect_catalog import build_catalog


@dataclass(frozen=True)
class DreamBallLockCandidate:
    card_id: str
    card_name: str
    evolves_from: str | None
    ability_name: str
    dream_ball_geometry: str
    dream_ball_geometry_compatible: bool
    lock_dimensions: tuple[str, ...]
    lock_activation: str
    target_scope: str
    stochastic: bool

    @property
    def bench_position_compatible(self) -> bool:
        return self.dream_ball_geometry_compatible and self.lock_activation not in {
            "active",
        }

    @property
    def extra_activation_prerequisite(self) -> str | None:
        if self.lock_activation in {"tool_attached", "stadium_required"}:
            return self.lock_activation
        if self.lock_activation == "active":
            return self.lock_activation
        return None


def build_dream_ball_lock_candidates(
    resources_root: Path = Path("resources"),
) -> tuple[DreamBallLockCandidate, ...]:
    """Join exact legal Evolution Ability rows to exact legal lock effects."""

    abilities = build_dream_ball_evolution_ability_catalog(resources_root)
    ability_by_key: dict[tuple[str, str], EvolutionAbilityCandidate] = {
        (row.card_id, row.ability_name): row
        for row in abilities
    }

    candidates: list[DreamBallLockCandidate] = []
    seen: set[tuple[str, str, tuple[str, ...], str, str]] = set()

    catalog = build_catalog(resources_root)
    for effect in catalog["effects"]:
        if effect["source_kind"] != "ability":
            continue
        ability_name = effect["effect_name"]
        dimensions = tuple(effect["dimensions"])
        activation = effect["activation"]
        target_scope = effect["target_scope"]

        for card_id in effect["print_ids"]:
            ability = ability_by_key.get((card_id, ability_name))
            if ability is None:
                continue

            key = (
                card_id,
                ability_name,
                dimensions,
                activation,
                target_scope,
            )
            if key in seen:
                continue
            seen.add(key)
            candidates.append(
                DreamBallLockCandidate(
                    card_id=card_id,
                    card_name=ability.card_name,
                    evolves_from=ability.evolves_from,
                    ability_name=ability_name,
                    dream_ball_geometry=ability.geometry,
                    dream_ball_geometry_compatible=(
                        ability.dream_ball_geometry_compatible
                    ),
                    lock_dimensions=dimensions,
                    lock_activation=activation,
                    target_scope=target_scope,
                    stochastic=bool(effect["stochastic"]),
                )
            )

    return tuple(
        sorted(
            candidates,
            key=lambda row: (
                row.card_id,
                row.ability_name,
                row.lock_dimensions,
                row.lock_activation,
            ),
        )
    )


def summarize_candidates(
    rows: tuple[DreamBallLockCandidate, ...],
) -> dict[str, object]:
    compatible = tuple(
        row for row in rows if row.dream_ball_geometry_compatible
    )
    bench_position = tuple(
        row for row in compatible if row.bench_position_compatible
    )
    no_extra_activation = tuple(
        row
        for row in bench_position
        if row.extra_activation_prerequisite is None
    )

    return {
        "evolution_lock_rows": len(rows),
        "evolution_lock_prints": len({row.card_id for row in rows}),
        "dream_ball_geometry_compatible_rows": len(compatible),
        "dream_ball_geometry_compatible_prints": len(
            {row.card_id for row in compatible}
        ),
        "bench_position_compatible_rows": len(bench_position),
        "no_recognized_extra_activation_prerequisite_rows": len(
            no_extra_activation
        ),
        "lock_activation": dict(
            sorted(Counter(row.lock_activation for row in compatible).items())
        ),
        "lock_dimensions": dict(
            sorted(
                Counter(
                    dimension
                    for row in compatible
                    for dimension in row.lock_dimensions
                ).items()
            )
        ),
        "target_scope": dict(
            sorted(Counter(row.target_scope for row in compatible).items())
        ),
    }
