"""Exact hidden-information bias for discard-before-search reacquisition choices.

A discard-gated search can require committing cards before the search reveals the
remaining deck. If no earlier full-deck inspection has occurred, the player can
still be uncertain which replacement copies are Prized.

This module isolates one conservative symmetric case:
- m endpoint-critical card classes are currently available as discard candidates;
- each class has exactly one additional replacement copy in the unknown
  deck-plus-Prize pool;
- exactly d of those m critical classes must be discarded;
- later typed search outputs can restore every discarded class whose replacement
  copy is in the deck.

A K0 policy must choose the d classes without knowing Prize composition.
A K1/oracle policy may choose after exact Prize composition is known.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from math import comb


@dataclass(frozen=True)
class DiscardReacquisitionChoice:
    unknown_pool: int
    prize_count: int
    candidate_classes: int
    forced_critical_discards: int

    def __post_init__(self) -> None:
        if self.unknown_pool <= 0:
            raise ValueError("unknown_pool must be positive")
        if self.prize_count < 0 or self.prize_count > self.unknown_pool:
            raise ValueError("prize_count must be within the unknown pool")
        if self.candidate_classes <= 0:
            raise ValueError("candidate_classes must be positive")
        if self.candidate_classes > self.unknown_pool:
            raise ValueError("candidate_classes cannot exceed unknown_pool")
        if (
            self.forced_critical_discards <= 0
            or self.forced_critical_discards > self.candidate_classes
        ):
            raise ValueError(
                "forced_critical_discards must be between 1 and candidate_classes"
            )

    @property
    def blind_k0_success(self) -> float:
        """Success for any fixed symmetric K0 choice of d critical classes.

        The fixed policy succeeds exactly when none of the d selected replacement
        copies are among the Prize cards.
        """

        d = self.forced_critical_discards
        if self.unknown_pool - d < self.prize_count:
            return 0.0
        return comb(self.unknown_pool - d, self.prize_count) / comb(
            self.unknown_pool,
            self.prize_count,
        )

    @property
    def informed_k1_success(self) -> float:
        """Success when Prize composition is known before choosing discards.

        Let K be the number of candidate replacement copies that are Prized.
        The informed chooser can safely discard d critical classes iff at least d
        candidate replacements remain in deck, equivalently K <= m - d.
        """

        m = self.candidate_classes
        d = self.forced_critical_discards
        denominator = comb(self.unknown_pool, self.prize_count)

        favorable = 0
        for prized_candidates in range(m - d + 1):
            ordinary_prizes = self.prize_count - prized_candidates
            if ordinary_prizes < 0:
                continue
            if ordinary_prizes > self.unknown_pool - m:
                continue
            favorable += comb(m, prized_candidates) * comb(
                self.unknown_pool - m,
                ordinary_prizes,
            )
        return favorable / denominator

    @property
    def information_gap(self) -> float:
        """K1/oracle success minus blind K0 success."""

        return self.informed_k1_success - self.blind_k0_success


def exhaustive_small_model(
    unknown_pool: int,
    prize_count: int,
    candidate_classes: int,
    forced_critical_discards: int,
) -> tuple[float, float]:
    """Enumerate labeled Prize sets and validate the closed-form interpretation."""

    model = DiscardReacquisitionChoice(
        unknown_pool=unknown_pool,
        prize_count=prize_count,
        candidate_classes=candidate_classes,
        forced_critical_discards=forced_critical_discards,
    )

    replacements = tuple(range(candidate_classes))
    fixed_k0_choice = frozenset(replacements[:forced_critical_discards])

    total = 0
    blind_successes = 0
    informed_successes = 0

    for prizes in combinations(range(unknown_pool), prize_count):
        total += 1
        prized = frozenset(prizes)

        if fixed_k0_choice.isdisjoint(prized):
            blind_successes += 1

        available_replacements = sum(
            replacement not in prized
            for replacement in replacements
        )
        if available_replacements >= forced_critical_discards:
            informed_successes += 1

    if total != comb(unknown_pool, prize_count):
        raise AssertionError("exhaustive Prize-state count mismatch")

    return blind_successes / total, informed_successes / total


def main() -> None:
    model = DiscardReacquisitionChoice(
        unknown_pool=52,
        prize_count=6,
        candidate_classes=2,
        forced_critical_discards=1,
    )
    print(f"K0 blind success: {model.blind_k0_success:.9%}")
    print(f"K1 informed success: {model.informed_k1_success:.9%}")
    print(f"hidden-information gap: {model.information_gap:.9%}")


if __name__ == "__main__":
    main()
