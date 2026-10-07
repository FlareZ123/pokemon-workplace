"""Exact setup access for Japanese-only draw-engine cards in Aichi Iron Thorns lists."""

from __future__ import annotations

import json
from dataclasses import dataclass
from math import comb
from typing import Any

from tools.aichi_setup_inference import (
    KAZUMA_IRON_NONBASIC_COUNTS,
    KOHEI_IRON_NONBASIC_COUNTS,
    RYOYA_IRON_NONBASIC_COUNTS,
)

DECK_SIZE = 60
OPENING_HAND_SIZE = 7
PRIZE_COUNT = 6
TAG_CALL = "Tag Call"
GUZMA_HALA = "Guzma & Hala"
PALACE_BOOK = "Palace Book"
PALACE_BELT = "Palace Belt"
PLAYERS_CEREMONY = "Player's Ceremony"


@dataclass(frozen=True)
class RegionalEngineSpec:
    name: str
    forced_basics: int
    tag_call: int
    guzma_hala: int
    palace_book: int
    palace_belt: int
    players_ceremony: int

    @classmethod
    def from_nonbasic_counts(
        cls,
        name: str,
        counts: dict[str, int],
    ) -> "RegionalEngineSpec":
        forced_basics = DECK_SIZE - sum(counts.values())
        if forced_basics <= 0:
            raise ValueError("deck must leave room for at least one Basic Pokemon")
        return cls(
            name=name,
            forced_basics=forced_basics,
            tag_call=counts.get(TAG_CALL, 0),
            guzma_hala=counts.get(GUZMA_HALA, 0),
            palace_book=counts.get(PALACE_BOOK, 0),
            palace_belt=counts.get(PALACE_BELT, 0),
            players_ceremony=counts.get(PLAYERS_CEREMONY, 0),
        )

    @property
    def regional_copies(self) -> int:
        return self.palace_book + self.palace_belt + self.players_ceremony


def _draw_compositions(draw_count: int, populations: tuple[int, ...]):
    current = [0] * len(populations)

    def visit(index: int, remaining: int):
        if index == len(populations) - 1:
            if 0 <= remaining <= populations[index]:
                current[index] = remaining
                yield tuple(current)
            return

        remaining_capacity = sum(populations[index + 1 :])
        lower = max(0, remaining - remaining_capacity)
        upper = min(populations[index], remaining)
        for selected in range(lower, upper + 1):
            current[index] = selected
            yield from visit(index + 1, remaining - selected)

    yield from visit(0, draw_count)


def _combination_weight(
    selected: tuple[int, ...],
    populations: tuple[int, ...],
) -> int:
    weight = 1
    for count, population in zip(selected, populations):
        weight *= comb(population, count)
    return weight


def _ratio(numerator: int, denominator: int) -> dict[str, int | float]:
    if denominator <= 0:
        raise ValueError("probability denominator must be positive")
    return {
        "numerator": numerator,
        "denominator": denominator,
        "probability": numerator / denominator,
    }


def _evaluate_window(
    spec: RegionalEngineSpec,
    *,
    include_normal_draw: bool,
) -> dict[str, Any]:
    # Categories:
    # 0 Basic Pokemon, 1 Tag Call, 2 Guzma & Hala, 3 Palace Book,
    # 4 Palace Belt, 5 Player's Ceremony, 6 all other cards.
    populations = (
        spec.forced_basics,
        spec.tag_call,
        spec.guzma_hala,
        spec.palace_book,
        spec.palace_belt,
        spec.players_ceremony,
        DECK_SIZE
        - spec.forced_basics
        - spec.tag_call
        - spec.guzma_hala
        - spec.palace_book
        - spec.palace_belt
        - spec.players_ceremony,
    )
    if min(populations) < 0 or sum(populations) != DECK_SIZE:
        raise ValueError(f"invalid population partition for {spec.name}: {populations}")

    accepted_hand_combinations = 0
    metric_weight = {
        "direct_or_tag_call_guzma_hala_access": 0,
        "palace_book_in_hand": 0,
        "players_ceremony_ready": 0,
        "palace_belt_ready": 0,
        "belt_plus_ceremony_ready": 0,
        "end_turn_draw_ready": 0,
        "any_regional_piece_in_hand": 0,
    }

    for hand in _draw_compositions(OPENING_HAND_SIZE, populations):
        if hand[0] == 0:
            continue
        hand_weight = _combination_weight(hand, populations)
        accepted_hand_combinations += hand_weight
        after_hand = tuple(
            population - selected
            for population, selected in zip(populations, hand)
        )

        for prizes in _draw_compositions(PRIZE_COUNT, after_hand):
            prize_weight = _combination_weight(prizes, after_hand)
            deck = [
                population - in_hand - prized
                for population, in_hand, prized in zip(populations, hand, prizes)
            ]

            if include_normal_draw:
                draw_options = (
                    (index, remaining)
                    for index, remaining in enumerate(deck)
                    if remaining > 0
                )
                draw_denominator = sum(deck)
            else:
                draw_options = ((None, 1),)
                draw_denominator = 1

            for draw_index, draw_weight in draw_options:
                current_hand = list(hand)
                current_deck = list(deck)
                if draw_index is not None:
                    current_hand[draw_index] += 1
                    current_deck[draw_index] -= 1

                guzma_hala_access = (
                    current_hand[2] > 0
                    or (current_hand[1] > 0 and current_deck[2] > 0)
                )
                palace_book_in_hand = current_hand[3] > 0
                ceremony_ready = (
                    current_hand[5] > 0
                    or (guzma_hala_access and current_deck[5] > 0)
                )
                belt_ready = (
                    spec.palace_belt > 0
                    and (
                        current_hand[4] > 0
                        or (guzma_hala_access and current_deck[4] > 0)
                    )
                )
                dual_ready = (
                    spec.palace_belt > 0
                    and belt_ready
                    and ceremony_ready
                )
                end_turn_draw_ready = palace_book_in_hand or ceremony_ready
                any_regional_piece_in_hand = (
                    current_hand[3] + current_hand[4] + current_hand[5] > 0
                )

                state_weight = hand_weight * prize_weight * draw_weight
                flags = {
                    "direct_or_tag_call_guzma_hala_access": guzma_hala_access,
                    "palace_book_in_hand": palace_book_in_hand,
                    "players_ceremony_ready": ceremony_ready,
                    "palace_belt_ready": belt_ready,
                    "belt_plus_ceremony_ready": dual_ready,
                    "end_turn_draw_ready": end_turn_draw_ready,
                    "any_regional_piece_in_hand": any_regional_piece_in_hand,
                }
                for key, active in flags.items():
                    if active:
                        metric_weight[key] += state_weight

    prize_combinations = comb(DECK_SIZE - OPENING_HAND_SIZE, PRIZE_COUNT)
    draw_denominator = (
        DECK_SIZE - OPENING_HAND_SIZE - PRIZE_COUNT
        if include_normal_draw
        else 1
    )
    denominator = (
        accepted_hand_combinations
        * prize_combinations
        * draw_denominator
    )

    return {
        "include_normal_draw": include_normal_draw,
        "metrics": {
            key: _ratio(weight, denominator)
            for key, weight in metric_weight.items()
        },
    }


def analyze_spec(spec: RegionalEngineSpec) -> dict[str, Any]:
    accepted = (
        comb(DECK_SIZE, OPENING_HAND_SIZE)
        - comb(DECK_SIZE - spec.forced_basics, OPENING_HAND_SIZE)
    )
    total = comb(DECK_SIZE, OPENING_HAND_SIZE)
    return {
        "name": spec.name,
        "deck_counts": {
            "forced_basics": spec.forced_basics,
            "tag_call": spec.tag_call,
            "guzma_hala": spec.guzma_hala,
            "palace_book": spec.palace_book,
            "palace_belt": spec.palace_belt,
            "players_ceremony": spec.players_ceremony,
            "regional_draw_engine_copies": spec.regional_copies,
        },
        "accepted_opening_probability": _ratio(accepted, total),
        "after_setup_before_normal_draw": _evaluate_window(
            spec,
            include_normal_draw=False,
        ),
        "after_first_normal_draw": _evaluate_window(
            spec,
            include_normal_draw=True,
        ),
    }


def build_aichi_regional_engine_analysis() -> dict[str, Any]:
    specs = (
        RegionalEngineSpec.from_nonbasic_counts(
            "Kazuma Kashi Iron Thorns",
            KAZUMA_IRON_NONBASIC_COUNTS,
        ),
        RegionalEngineSpec.from_nonbasic_counts(
            "Ryoya Fujii Iron Thorns",
            RYOYA_IRON_NONBASIC_COUNTS,
        ),
        RegionalEngineSpec.from_nonbasic_counts(
            "Kohei Hamamichi Iron Thorns",
            KOHEI_IRON_NONBASIC_COUNTS,
        ),
    )
    return {
        "scope": (
            "Exact published Aichi Iron Thorns list counts already preserved "
            "in tools/aichi_setup_inference.py"
        ),
        "interpretation": {
            "palace_book": "Item draw effect that ends the user's turn",
            "palace_belt": "Tool that increases the normal beginning-of-turn draw while its holder is Active",
            "players_ceremony": "Stadium draw effect that ends the choosing player's turn",
            "guzma_hala": (
                "Local card text searches a Stadium, and after discarding two other cards "
                "can also search a Pokemon Tool and a Special Energy"
            ),
            "tag_call": "Local card text can search Guzma & Hala as a TAG TEAM card",
        },
        "model_limits": (
            "The access model conditions on a legal accepted seven-card opening hand, "
            "then places six Prize cards and optionally takes one normal draw. It does not "
            "credit Trainers' Mail, opponent-mulligan bonus draws, other draw effects, or "
            "recovery. It treats a reachable Guzma & Hala as an available connector and does "
            "not score Supporter contention, the strategic cost of two discards for Palace Belt, "
            "Tool-slot contention, Stadium symmetry, or whether ending the turn is desirable."
        ),
        "lists": [analyze_spec(spec) for spec in specs],
    }


def main() -> None:
    print(json.dumps(build_aichi_regional_engine_analysis(), indent=2))


if __name__ == "__main__":
    main()
