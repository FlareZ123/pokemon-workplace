"""Ticket/Town Map marginal value in the published 2026 Aichi Vileplume list.

An extension of aichi_post_gnh_prize_reset, with exact post-G&H Ticket
semantics and paired deck orders.  Four previously tagged Supporter tech
slots are reinterpreted as natural-access Item slots.  A Town Map held before
the first reset is used only after a failed reset to reveal new Prizes.
All endpoints are first-turn access objectives, not full game win rates.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from math import sqrt
import random

from tools.aichi_post_gnh_prize_reset import (
    DECK, ENDPOINTS, TECH_SLOTS, endpoint_success, expand,
    prepare, protect_gnh_outputs,
)


PACKAGES: dict[str, tuple[str, ...]] = {
    "baseline": (),
    "one_ticket": ("T",),
    "one_ticket_one_map": ("T", "M"),
    "two_tickets_no_map": ("T", "T"),
    "two_tickets_one_map": ("T", "T", "M"),
    "two_tickets_two_maps": ("T", "T", "M", "M"),
    "three_tickets_one_map": ("T", "T", "T", "M"),
}


def package_items(hand: Counter[str], assignment: tuple[str, ...]) -> tuple[int, int]:
    return (
        sum(hand[TECH_SLOTS[i]] for i, role in enumerate(assignment) if role == "T"),
        sum(hand[TECH_SLOTS[i]] for i, role in enumerate(assignment) if role == "M"),
    )


def deck_after_tickets(
    original_deck: Counter[str], original_prizes: tuple[str, ...],
    shuffled_original_deck: tuple[str, ...], tickets: int,
) -> Counter[str]:
    """Searchable deck after consecutive Tickets, no interleaved shuffles.

    The first, second, ... new Prize blocks are disjoint consecutive groups
    of P cards from the original deck. Previously Prized blocks return beneath
    untouched cards. Their order remains irrelevant to the endpoint predicate.
    """
    prize_size = len(original_prizes)
    if tickets < 1 or tickets * prize_size > len(shuffled_original_deck):
        raise ValueError("each Ticket needs an untouched top-deck Prize block")
    block = shuffled_original_deck[(tickets - 1) * prize_size:tickets * prize_size]
    after = original_deck.copy()
    after.subtract(Counter(block))
    after.update(original_prizes)
    if any(v < 0 for v in after.values()):
        raise ValueError("shuffled deck does not represent the original deck")
    return +after


@dataclass
class Summary:
    raw_trials: int
    accepted: int
    core_ready: int
    baseline: Counter[str]
    access_first: Counter[str]
    access_second: Counter[str]
    rescue: Counter[tuple[str, str]]
    second_reset_rescue: Counter[tuple[str, str]]


def simulate(raw_trials: int = 200_000, seed: int = 20261008) -> Summary:
    rng = random.Random(seed)
    deck_rng = random.Random(seed ^ 0xA1C41)
    accepted = core_ready = 0
    baseline: Counter[str] = Counter()
    access_first: Counter[str] = Counter()
    access_second: Counter[str] = Counter()
    rescue: Counter[tuple[str, str]] = Counter()
    second_rescue: Counter[tuple[str, str]] = Counter()

    for _ in range(raw_trials):
        order = rng.sample(range(len(DECK)), len(DECK))
        state = prepare(order)
        if state is None:
            continue
        accepted += 1
        protected = protect_gnh_outputs(state)
        if protected is None:
            continue
        core_ready += 1
        hand, original_deck = protected
        before = {
            endpoint: endpoint_success(endpoint, hand, original_deck, state.active)
            for endpoint in ENDPOINTS
        }
        for endpoint, success in before.items():
            baseline[endpoint] += int(success)

        resources = {name: package_items(hand, assignment) for name, assignment in PACKAGES.items()}
        for name, (tickets, maps) in resources.items():
            access_first[name] += int(tickets > 0)
            access_second[name] += int(tickets > 1 and maps > 0)

        if all(before.values()) or not any(t > 0 for t, m in resources.values()):
            continue

        shuffled_deck = expand(original_deck)
        deck_rng.shuffle(shuffled_deck)
        random_order = tuple(shuffled_deck)
        after_first = deck_after_tickets(original_deck, state.prizes, random_order, 1)
        first_success = {
            endpoint: endpoint_success(endpoint, hand, after_first, state.active)
            for endpoint in ENDPOINTS if not before[endpoint]
        }

        possible_second = any(t > 1 and m > 0 for t, m in resources.values())
        if possible_second and any(not success for success in first_success.values()):
            after_second = deck_after_tickets(original_deck, state.prizes, random_order, 2)
            second_success = {
                endpoint: endpoint_success(endpoint, hand, after_second, state.active)
                for endpoint in first_success if not first_success[endpoint]
            }
        else:
            second_success = {}

        for name, (tickets, maps) in resources.items():
            if not tickets:
                continue
            for endpoint in first_success:
                if first_success[endpoint]:
                    rescue[(name, endpoint)] += 1
                elif tickets > 1 and maps > 0 and second_success.get(endpoint, False):
                    rescue[(name, endpoint)] += 1
                    second_rescue[(name, endpoint)] += 1

    return Summary(
        raw_trials, accepted, core_ready, baseline,
        access_first, access_second, rescue, second_rescue,
    )


def output(summary: Summary) -> str:
    lines = [
        f"raw={summary.raw_trials}, accepted={summary.accepted}, G&H core ready={summary.core_ready}",
        f"baseline (among accepted): "
        + " ".join(f"{ep}={100*summary.baseline[ep]/summary.accepted:.5f}%" for ep in ENDPOINTS),
        "package | natural first / second reset access among accepted | "
        "dual_stage2 lift (pp; approx 95% CI half-width) | item_lock lift (pp) | "
        "second-reset-only dual-stage2 lift (pp)",
    ]
    for name in PACKAGES:
        n = summary.accepted
        dual = summary.rescue[(name, "dual_stage2")]
        lock = summary.rescue[(name, "item_lock")]
        second = summary.second_reset_rescue[(name, "dual_stage2")]
        p = dual / n
        ci = 100 * 1.96 * sqrt(p * (1-p)/n)
        lines.append(
            f"{name} | {100*summary.access_first[name]/n:.5f}% / "
            f"{100*summary.access_second[name]/n:.5f}% | "
            f"{100*p:.5f} ± {ci:.5f} | "
            f"{100*lock/n:.5f} | {100*second/n:.5f}"
        )
    return "\n".join(lines)


def main() -> None:
    print(output(simulate()))


if __name__ == "__main__":
    main()
