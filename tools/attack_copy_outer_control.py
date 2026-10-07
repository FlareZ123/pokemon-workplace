"""Classify and evaluate control flow before an attack-copy body executes.

The card pool contains copy attacks whose surrounding text changes whether the
copy body is reached. Those conditions are not one mechanical class:

- declaration gates can make the outer attack unavailable;
- body gates let the attack be used but can resolve without executing a copied
  body;
- stochastic body gates need an explicit random outcome before execution can
  continue.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Literal


ControlStage = Literal["declaration", "body"]
ControlKind = Literal["coin_heads", "actor_hand_empty", "opponent_prizes_exact"]
ControlOutcome = Literal[
    "proceed",
    "declaration_illegal",
    "resolve_without_copy",
    "random_outcome_required",
]


@dataclass(frozen=True)
class CopyOuterControl:
    stage: ControlStage
    kind: ControlKind
    exact_value: int | None = None

    def __post_init__(self) -> None:
        if self.kind == "opponent_prizes_exact":
            if self.stage != "declaration" or self.exact_value is None:
                raise ValueError(
                    "exact Prize control must be a valued declaration gate"
                )
        elif self.exact_value is not None:
            raise ValueError("only exact Prize control carries an exact value")


_PRIZE_GATE = re.compile(
    r"^You can use this attack only if your opponent has exactly "
    r"(\\d+) Prize cards remaining\\.",
    re.IGNORECASE,
)


def classify_outer_control(text: str) -> CopyOuterControl | None:
    """Classify audited control text around an attack-copy clause."""

    normalized = re.sub(r"\\s+", " ", text).strip()
    lowered = normalized.casefold()
    if "as this attack" not in lowered:
        return None

    prize = _PRIZE_GATE.match(normalized)
    if prize is not None:
        return CopyOuterControl(
            stage="declaration",
            kind="opponent_prizes_exact",
            exact_value=int(prize.group(1)),
        )

    if normalized.startswith("Flip a coin. If heads,"):
        return CopyOuterControl(stage="body", kind="coin_heads")

    if normalized.startswith("If you have no cards in your hand,"):
        return CopyOuterControl(stage="body", kind="actor_hand_empty")

    return None


def evaluate_outer_control(
    control: CopyOuterControl | None,
    *,
    actor_hand_size: int | None = None,
    opponent_prizes_remaining: int | None = None,
    coin_heads: bool | None = None,
) -> ControlOutcome:
    """Evaluate one classified control without mutating game state."""

    if control is None:
        return "proceed"

    if control.kind == "opponent_prizes_exact":
        if opponent_prizes_remaining is None:
            raise ValueError("opponent Prize count is required")
        if opponent_prizes_remaining < 0:
            raise ValueError("opponent Prize count cannot be negative")
        return (
            "proceed"
            if opponent_prizes_remaining == control.exact_value
            else "declaration_illegal"
        )

    if control.kind == "actor_hand_empty":
        if actor_hand_size is None:
            raise ValueError("actor hand size is required")
        if actor_hand_size < 0:
            raise ValueError("actor hand size cannot be negative")
        return "proceed" if actor_hand_size == 0 else "resolve_without_copy"

    if control.kind == "coin_heads":
        if coin_heads is None:
            return "random_outcome_required"
        return "proceed" if coin_heads else "resolve_without_copy"

    raise AssertionError(control.kind)
