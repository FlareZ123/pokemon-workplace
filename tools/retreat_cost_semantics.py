"""Retreat Cost modifier algebra and conservative fixed-delta text parsing."""

from __future__ import annotations

from dataclasses import dataclass
import re


_FIXED_DELTA = re.compile(
    r"Retreat Cost[^.]{0,160}?\bis "
    r"((?:Colorless)+) (more|less)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True, order=True)
class RetreatCostModifier:
    effect_id: str
    delta: int = 0
    no_retreat_cost: bool = False

    def __post_init__(self) -> None:
        if not self.effect_id:
            raise ValueError("effect_id must be non-empty")
        if self.no_retreat_cost and self.delta:
            raise ValueError("no-Retreat-Cost modifiers cannot also carry delta")


@dataclass(frozen=True)
class FixedDeltaParse:
    modifiers: tuple[RetreatCostModifier, ...]
    variable_matches: tuple[str, ...]


def effective_retreat_cost(
    base_cost: int,
    modifiers: tuple[RetreatCostModifier, ...] = (),
) -> int:
    """Apply D-11/D-12 stacking and D-13 no-cost priority."""

    if base_cost < 0:
        raise ValueError("base_cost must be non-negative")

    if any(modifier.no_retreat_cost for modifier in modifiers):
        return 0

    return max(0, base_cost + sum(modifier.delta for modifier in modifiers))


def parse_fixed_retreat_cost_deltas(
    effect_id: str,
    text: str,
) -> FixedDeltaParse:
    """Compile literal fixed Retreat Cost increases/reductions from one text.

    Variable forms such as "1 less for each Beldum" are reported separately
    rather than collapsed into a fixed modifier.
    """

    normalized = " ".join(text.split())
    modifiers: list[RetreatCostModifier] = []
    variable: list[str] = []

    for index, match in enumerate(_FIXED_DELTA.finditer(normalized)):
        tail = normalized[match.end():match.end() + 80].lower()
        magnitude = match.group(1).count("Colorless")
        direction = match.group(2).lower()

        if "for each" in tail:
            variable.append(match.group(0))
            continue

        delta = magnitude if direction == "more" else -magnitude
        modifiers.append(
            RetreatCostModifier(
                effect_id=f"{effect_id}#{index}",
                delta=delta,
            )
        )

    return FixedDeltaParse(
        modifiers=tuple(modifiers),
        variable_matches=tuple(variable),
    )


def no_retreat_cost(effect_id: str) -> RetreatCostModifier:
    """Construct an already-applicable D-13 no-Retreat-Cost modifier."""

    return RetreatCostModifier(effect_id=effect_id, no_retreat_cost=True)
