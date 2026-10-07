"""Represent jointly feasible discard sets as a uniform hypergraph."""

from dataclasses import dataclass
from itertools import combinations


@dataclass(frozen=True)
class DiscardFamily:
    cards: tuple[str, ...]
    edges: frozenset[frozenset[str]]

    @property
    def cost(self) -> int:
        return len(next(iter(self.edges)))

    def participation(self) -> dict[str, float]:
        total = len(self.edges)
        return {
            card: sum(card in edge for edge in self.edges) / total
            for card in self.cards
        }

    def forced_cards(self) -> frozenset[str]:
        return frozenset.intersection(*self.edges)

    def payable(self, protected: frozenset[str]) -> bool:
        return any(edge.isdisjoint(protected) for edge in self.edges)

    def robustness(self, protected_count: int) -> tuple[int, int, float]:
        states = list(combinations(self.cards, protected_count))
        viable = sum(
            self.payable(frozenset(chosen))
            for chosen in states
        )
        return viable, len(states), viable / len(states)

    def minimum_protection_cut(self) -> int:
        for size in range(len(self.cards) + 1):
            for chosen in combinations(self.cards, size):
                if not self.payable(frozenset(chosen)):
                    return size
        return len(self.cards)


def cycle_family() -> DiscardFamily:
    return DiscardFamily(
        tuple("ABCDEF"),
        frozenset(
            frozenset(pair)
            for pair in ("AB", "BC", "CD", "DE", "EF", "FA")
        ),
    )


def triangle_family() -> DiscardFamily:
    return DiscardFamily(
        tuple("ABCDEF"),
        frozenset(
            frozenset(pair)
            for pair in ("AB", "BC", "CA", "DE", "EF", "FD")
        ),
    )


def main() -> None:
    cycle = cycle_family()
    triangles = triangle_family()

    assert cycle.cost == triangles.cost == 2
    assert len(cycle.edges) == len(triangles.edges) == 6
    assert cycle.participation() == triangles.participation()
    assert set(cycle.participation().values()) == {1 / 3}
    assert cycle.forced_cards() == triangles.forced_cards() == frozenset()
    assert cycle.minimum_protection_cut() == 3
    assert triangles.minimum_protection_cut() == 4

    protected = frozenset({"A", "C", "E"})
    assert not cycle.payable(protected)
    assert triangles.payable(protected)
    assert cycle.robustness(3) == (18, 20, 0.9)
    assert triangles.robustness(3) == (20, 20, 1.0)

    print("participation", cycle.participation())
    print("cycle cut", cycle.minimum_protection_cut())
    print("triangles cut", triangles.minimum_protection_cut())
    print("cycle robustness at 3", cycle.robustness(3))
    print("triangles robustness at 3", triangles.robustness(3))


if __name__ == "__main__":
    main()
