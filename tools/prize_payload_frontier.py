"""Exact initial-Prize coverage for Regidrago Dragon attack payloads.

Samples accepted seven-card Basic-containing openings, six Prizes and one
natural turn draw. This models inventory access, not attack execution.
"""
from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from math import comb


@dataclass(frozen=True)
class Payload:
    name: str
    copies: int
    basic: bool


BASELINE = (
    Payload("Dialga-GX", 1, True),
    Payload("Koraidon ex", 1, True),
    Payload("Kyurem", 1, True),
    Payload("Dragapult ex", 1, False),
    Payload("Hisuian Goodra VSTAR", 1, False),
)


def choose(n: int, k: int) -> int:
    return comb(n, k) if 0 <= k <= n else 0


def coverage(
    payloads: tuple[Payload, ...], *, other_basics: int = 12,
    deck_size: int = 60, prize_count: int = 6, opening_size: int = 7,
) -> dict[str, Fraction]:
    """Exact probability conditional on an accepted Basic-containing opener.

    Reverse random dealing order to enumerate Prize compositions first,
    followed by accepted opening hands and the next natural draw. Hisuian
    Heavy Ball has one copy and can exchange for one Prized Basic only.
    Added payload copies replace non-Basic filler and change starter
    density if that payload itself is Basic.
    """
    if not payloads or len({p.name for p in payloads}) != len(payloads):
        raise ValueError("Payload names must be nonempty and distinct")
    if any(p.copies < 1 for p in payloads):
        raise ValueError("Payload copy count must be positive")
    fillers = deck_size - other_basics - 1 - sum(p.copies for p in payloads)
    if fillers < 0 or other_basics < 0:
        raise ValueError("Invalid deck partition")
    remaining = deck_size - prize_count
    post_opening = remaining - opening_size
    if post_opening <= 0:
        raise ValueError("A natural draw must remain")
    groups = [p.copies for p in payloads] + [1, other_basics, fillers]
    starter_total = other_basics + sum(p.copies for p in payloads if p.basic)
    names = [p.name for p in payloads]
    counters = {
        "any_payload_print_prized": 0,
        "all_payload_types_present": 0,
        "full_menu_with_visible_ball": 0,
        "timeless_phantom_with_visible_ball": 0,
        "heavy_ball_seen": 0,
    }
    for p in payloads:
        counters[f"prized_{p.name}"] = 0
        counters[f"covered_{p.name}"] = 0
        counters[f"rescued_{p.name}"] = 0
    denominator = 0

    for first in product(*(range(min(n, prize_count) + 1) for n in groups[:-1])):
        filler_prizes = prize_count - sum(first)
        if not 0 <= filler_prizes <= fillers:
            continue
        prizes = (*first, filler_prizes)
        ways = 1
        for group_size, n_prized in zip(groups, prizes):
            ways *= choose(group_size, n_prized)
        if not ways:
            continue
        starter_prizes = prizes[-2] + sum(
            prizes[i] for i, p in enumerate(payloads) if p.basic
        )
        s = starter_total - starter_prizes
        accepted = choose(remaining, opening_size) - choose(remaining - s, opening_size)
        if not accepted:
            continue
        state_weight = ways * post_opening * accepted
        denominator += state_weight

        ball_seen = 0
        if not prizes[len(payloads)]:
            in_hand = choose(remaining - 1, opening_size - 1) - choose(
                remaining - 1 - s, opening_size - 1
            )
            next_draw = choose(remaining - 1, opening_size) - choose(
                remaining - 1 - s, opening_size
            )
            ball_seen = ways * (post_opening * in_hand + next_draw)
        counters["heavy_ball_seen"] += ball_seen

        missing = [
            i for i, p in enumerate(payloads) if prizes[i] == p.copies
        ]
        missing_basics = [i for i in missing if payloads[i].basic]
        missing_evos = [i for i in missing if not payloads[i].basic]

        if any(prizes[:len(payloads)]):
            counters["any_payload_print_prized"] += state_weight
        if not missing:
            counters["all_payload_types_present"] += state_weight
        if not missing_evos and len(missing_basics) <= 1:
            counters["full_menu_with_visible_ball"] += (
                ball_seen if missing_basics else state_weight
            )

        dialga_index = names.index("Dialga-GX")
        dragapult_index = names.index("Dragapult ex")
        if prizes[dragapult_index] < payloads[dragapult_index].copies:
            counters["timeless_phantom_with_visible_ball"] += (
                state_weight
                if prizes[dialga_index] < payloads[dialga_index].copies
                else ball_seen
            )

        for i, p in enumerate(payloads):
            if prizes[i]:
                counters[f"prized_{p.name}"] += state_weight
            if prizes[i] < p.copies:
                counters[f"covered_{p.name}"] += state_weight
            elif p.basic:
                counters[f"covered_{p.name}"] += ball_seen
                counters[f"rescued_{p.name}"] += ball_seen

    if denominator == 0:
        raise ValueError("No accepted openings")
    return {key: Fraction(value, denominator) for key, value in counters.items()}


def swapped(name: str) -> tuple[Payload, ...]:
    """Replace one unspecified non-Basic filler with a payload copy."""
    if name not in {p.name for p in BASELINE}:
        raise ValueError(name)
    return tuple(
        Payload(p.name, p.copies + int(p.name == name), p.basic)
        for p in BASELINE
    )
