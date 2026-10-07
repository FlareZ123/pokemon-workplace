"""Count-preserving zone state for repeated gameplay-equivalent card copies.

A single mapping from card name to one zone cannot represent ordinary deck states
where several copies of the same card occupy different zones. This module keeps
copies aggregated while they are exchangeable: one card-class key maps to a
count in each zone.

Use a card-class key at the semantic resolution required by the question, such
as an exact print ID or conservative gameplay variant. Board topology, attached
cards, or copy-specific history can require a later materialization step with
explicit object/instance identity.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import comb
from typing import Mapping


@dataclass(frozen=True)
class ZoneCountState:
    """Immutable sparse counts keyed by (card_class, zone)."""

    counts: tuple[tuple[str, str, int], ...] = ()

    def __post_init__(self) -> None:
        seen: set[tuple[str, str]] = set()
        for card_class, zone, count in self.counts:
            if not card_class:
                raise ValueError("card_class must be non-empty")
            if not zone:
                raise ValueError("zone must be non-empty")
            if count <= 0:
                raise ValueError("sparse zone counts must be positive")

            key = (card_class, zone)
            if key in seen:
                raise ValueError(f"duplicate zone-count key: {key!r}")
            seen.add(key)

        if self.counts != tuple(sorted(self.counts)):
            raise ValueError("zone counts must be stored in canonical sorted order")

    @classmethod
    def from_mapping(
        cls,
        counts: Mapping[tuple[str, str], int],
    ) -> "ZoneCountState":
        return cls(
            tuple(
                sorted(
                    (card_class, zone, count)
                    for (card_class, zone), count in counts.items()
                    if count > 0
                )
            )
        )

    def count(self, card_class: str, zone: str) -> int:
        for current_class, current_zone, count in self.counts:
            if current_class == card_class and current_zone == zone:
                return count
        return 0

    def total(self, card_class: str) -> int:
        return sum(
            count
            for current_class, _zone, count in self.counts
            if current_class == card_class
        )

    def zone_counts(self, card_class: str) -> tuple[tuple[str, int], ...]:
        return tuple(
            (zone, count)
            for current_class, zone, count in self.counts
            if current_class == card_class
        )

    def move(
        self,
        card_class: str,
        source_zone: str,
        destination_zone: str,
        *,
        amount: int = 1,
    ) -> "ZoneCountState":
        if amount <= 0:
            raise ValueError("amount must be positive")
        if source_zone == destination_zone:
            return self

        source_count = self.count(card_class, source_zone)
        if source_count < amount:
            raise ValueError(
                f"cannot move {amount} {card_class!r} from {source_zone!r}; "
                f"only {source_count} available"
            )

        counts = {
            (current_class, zone): count
            for current_class, zone, count in self.counts
        }
        source_key = (card_class, source_zone)
        destination_key = (card_class, destination_zone)

        remaining = source_count - amount
        if remaining:
            counts[source_key] = remaining
        else:
            counts.pop(source_key)

        counts[destination_key] = counts.get(destination_key, 0) + amount
        return ZoneCountState.from_mapping(counts)


def exchangeable_distribution_count(copy_count: int, zone_count: int) -> int:
    """Number of zone-count vectors for exchangeable copies.

    This is the stars-and-bars count C(copy_count + zone_count - 1,
    zone_count - 1).
    """

    if copy_count < 0:
        raise ValueError("copy_count must be non-negative")
    if zone_count <= 0:
        raise ValueError("zone_count must be positive")
    return comb(copy_count + zone_count - 1, zone_count - 1)


def single_zone_map_capacity(zone_count: int) -> int:
    """Number of states a single card_class -> zone value can distinguish."""

    if zone_count <= 0:
        raise ValueError("zone_count must be positive")
    return zone_count
