"""Information-slack boundary for discard-before-search decisions."""

from __future__ import annotations

from dataclasses import dataclass

from k0_discard_reacquisition_bias import DiscardReacquisitionChoice


@dataclass(frozen=True)
class DiscardInformationBoundary:
    """Classify whether hidden replacement information can change a payment.

    always_safe_cards are physical hand cards that can be paid without harming
    the modeled endpoint in any hidden world. critical_candidates are visible
    cards whose discard is acceptable only when a hidden replacement remains
    accessible. Every critical candidate has one replacement in the unknown
    deck-plus-Prize pool.
    """

    unknown_pool: int
    prize_count: int
    discard_cost: int
    always_safe_cards: int
    critical_candidates: int

    def __post_init__(self) -> None:
        if self.unknown_pool <= 0:
            raise ValueError("unknown_pool must be positive")
        if not 0 <= self.prize_count <= self.unknown_pool:
            raise ValueError("invalid prize_count")
        if self.discard_cost < 0:
            raise ValueError("discard_cost must be nonnegative")
        if self.always_safe_cards < 0:
            raise ValueError("always_safe_cards must be nonnegative")
        if self.critical_candidates < 0:
            raise ValueError("critical_candidates must be nonnegative")
        if self.discard_cost > self.always_safe_cards + self.critical_candidates:
            raise ValueError("payment cannot be made from represented cards")

    @property
    def forced_critical_discards(self) -> int:
        return max(0, self.discard_cost - self.always_safe_cards)

    @property
    def information_can_change_choice(self) -> bool:
        q = self.forced_critical_discards
        return 0 < q < self.critical_candidates

    @property
    def blind_success(self) -> float:
        q = self.forced_critical_discards
        if q == 0:
            return 1.0
        model = DiscardReacquisitionChoice(
            unknown_pool=self.unknown_pool,
            prize_count=self.prize_count,
            candidate_classes=self.critical_candidates,
            forced_critical_discards=q,
        )
        return model.blind_k0_success

    @property
    def informed_success(self) -> float:
        q = self.forced_critical_discards
        if q == 0:
            return 1.0
        model = DiscardReacquisitionChoice(
            unknown_pool=self.unknown_pool,
            prize_count=self.prize_count,
            candidate_classes=self.critical_candidates,
            forced_critical_discards=q,
        )
        return model.informed_k1_success

    @property
    def information_gap(self) -> float:
        return self.informed_success - self.blind_success


def aichi_direct_gnh_rich_endpoint() -> DiscardInformationBoundary:
    """Worst immediate payment pressure for the modeled direct G&H endpoints.

    After the first draw, removing the Active and the played Supporter leaves
    six physical hand cards. If paid G&H is needed, at least one of TM:
    Evolution or Jet Energy is missing. The richest modeled endpoint therefore
    needs to preserve at most four visible cards: Bunnelby, two evolution
    Basics, and the one already-present core resource. At least two cards are
    endpoint-safe payment material, exactly covering G&H's cost of two.
    """

    return DiscardInformationBoundary(
        unknown_pool=52,
        prize_count=6,
        discard_cost=2,
        always_safe_cards=2,
        critical_candidates=4,
    )


def secret_box_local_counterexample() -> DiscardInformationBoundary:
    """Boundary matching the earlier local Secret Box two-world witness."""

    return DiscardInformationBoundary(
        unknown_pool=52,
        prize_count=6,
        discard_cost=3,
        always_safe_cards=2,
        critical_candidates=2,
    )


def main() -> None:
    gnh = aichi_direct_gnh_rich_endpoint()
    box = secret_box_local_counterexample()
    print("direct_gnh")
    print(f"  forced_critical={gnh.forced_critical_discards}")
    print(f"  choice_sensitive={gnh.information_can_change_choice}")
    print(f"  gap_pp={gnh.information_gap * 100:.9f}")
    print("secret_box_counterexample")
    print(f"  forced_critical={box.forced_critical_discards}")
    print(f"  choice_sensitive={box.information_can_change_choice}")
    print(f"  blind={box.blind_success:.9%}")
    print(f"  informed={box.informed_success:.9%}")
    print(f"  gap_pp={box.information_gap * 100:.9f}")


if __name__ == "__main__":
    main()
