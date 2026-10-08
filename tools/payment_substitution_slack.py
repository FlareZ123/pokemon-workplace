"""Closed-form payment pressure when a weaker connector can fund a stronger one."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PaymentSubstitutionSlack:
    """Critical-payment pressure for two action orders.

    A is a weaker connector with discard cost a.
    B is a stronger connector with discard cost b and can directly satisfy the
    local endpoint. A is a legal payment card for B.

    s counts external cards that are safe to discard under every hidden world
    relevant to the local endpoint.
    """

    weaker_cost: int
    stronger_cost: int
    safe_external: int

    def __post_init__(self) -> None:
        if min(self.weaker_cost, self.stronger_cost, self.safe_external) < 0:
            raise ValueError("costs and safe_external must be non-negative")

    @property
    def sequential_critical_pressure(self) -> int:
        """Minimum critical cards consumed by A then B before new card inflow."""
        return max(
            0,
            self.weaker_cost + self.stronger_cost - self.safe_external,
        )

    @property
    def stronger_first_critical_pressure(self) -> int:
        """Minimum critical cards consumed when B uses A as one payment."""
        connector_payment = int(self.stronger_cost > 0)
        return max(
            0,
            self.stronger_cost
            - self.safe_external
            - connector_payment,
        )

    @property
    def critical_pressure_reduction(self) -> int:
        return (
            self.sequential_critical_pressure
            - self.stronger_first_critical_pressure
        )

    @property
    def safe_external_threshold_sequential(self) -> int:
        """External safe cards needed to preserve every critical card."""
        return self.weaker_cost + self.stronger_cost

    @property
    def safe_external_threshold_stronger_first(self) -> int:
        """External safe cards needed when A itself can pay B."""
        return max(0, self.stronger_cost - 1)

    @property
    def threshold_reduction(self) -> int:
        return (
            self.safe_external_threshold_sequential
            - self.safe_external_threshold_stronger_first
        )


def harto_quick_ball_ultra_ball_table() -> tuple[tuple[int, int, int], ...]:
    """Return (safe external, QB-first q, stronger-first q) for Harto costs."""
    rows = []
    for safe_external in range(5):
        model = PaymentSubstitutionSlack(
            weaker_cost=1,
            stronger_cost=2,
            safe_external=safe_external,
        )
        rows.append(
            (
                safe_external,
                model.sequential_critical_pressure,
                model.stronger_first_critical_pressure,
            )
        )
    return tuple(rows)


if __name__ == "__main__":
    for row in harto_quick_ball_ultra_ball_table():
        print(row)
