"""Aichi first-turn Ticket package access through late Stellar Wish.

This composes the established Aichi G&H planner with a legal *unused* Jirachi
Stellar Wish, only when original first-window Jirachi search did not already
find G&H or Tag Call. Post-G&H Item access is additional to opening+one-draw.
A successful Trainer selection from the top 5 is followed by a full reshuffle
before the first Ticket; physical-card order remains conserved afterward.
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
from tools.aichi_repeated_ticket_access import (
    PACKAGES, deck_after_tickets, package_items,
)


def stellar_available(order: list[int], active: str) -> bool:
    """Current original Aichi planner did not use Jirachi's Ability earlier."""
    if active != "Jirachi":
        return False
    top_five = (DECK[i] for i in order[14:19])
    return not any(card in ("Guzma & Hala", "Tag Call") for card in top_five)


def select_post_gnh_stellar(
    hand: Counter[str], assignment: tuple[str, ...],
    top_five: tuple[tuple[int, str], ...],
) -> tuple[int, str] | None:
    """Choose one accessible item that increases immediate reset capacity.

    Return a physical index and its card name. Ties are broken by first
    appearance in the top 5. If no one-card pick makes an additional reset
    executable with the held Tickets/Maps, leave Stellar Wish unused.
    """
    initial_tickets, initial_maps = package_items(hand, assignment)
    max_uses = min(initial_tickets, initial_maps + 1)
    best = None
    for physical_index, card in top_five:
        if card not in TECH_SLOTS:
            continue
        slot_number = TECH_SLOTS.index(card)
        if slot_number >= len(assignment):
            continue
        role = assignment[slot_number]
        if role not in ("T", "M"):
            continue
        t = initial_tickets + int(role == "T")
        m = initial_maps + int(role == "M")
        after_uses = min(t, m + 1)
        if after_uses > max_uses:
            max_uses = after_uses
            best = (physical_index, card)
    return best


@dataclass
class Summary:
    raw: int
    accepted: int
    core: int
    late_stellar_eligible: int
    baseline: Counter[str]
    no_stellar_rescue: Counter[tuple[str, str]]
    late_stellar_rescue: Counter[tuple[str, str]]
    late_stellar_helps: Counter[tuple[str, str]]
    late_stellar_hurts: Counter[tuple[str, str]]
    selected: Counter[str]
    first_item_access_gain: Counter[str]
    second_item_access_gain: Counter[str]


def simulate(raw_trials: int = 200_000, seed: int = 20261008) -> Summary:
    starting_rng = random.Random(seed)
    order_rng = random.Random(seed ^ 0xA1C41)
    reshuffle_rng = random.Random(seed ^ 0x571A)
    accepted = core = eligible_count = 0
    baseline: Counter[str] = Counter()
    no_stellar: Counter[tuple[str, str]] = Counter()
    late_stellar: Counter[tuple[str, str]] = Counter()
    helps: Counter[tuple[str, str]] = Counter()
    hurts: Counter[tuple[str, str]] = Counter()
    selected: Counter[str] = Counter()
    access_first: Counter[str] = Counter()
    access_second: Counter[str] = Counter()

    for _ in range(raw_trials):
        order = starting_rng.sample(range(len(DECK)), len(DECK))
        state = prepare(order)
        if state is None:
            continue
        accepted += 1
        protected = protect_gnh_outputs(state)
        if protected is None:
            continue
        core += 1
        hand, remaining = protected
        before = {endpoint: endpoint_success(endpoint, hand, remaining, state.active)
                  for endpoint in ENDPOINTS}
        baseline.update(endpoint for endpoint, success in before.items() if success)
        eligible = stellar_available(order, state.active)
        eligible_count += int(eligible)

        # Materialize an explicitly labeled deck so one chosen top-five card
        # can be removed without ambiguous duplicate-card semantics.
        physical_cards = tuple(enumerate(expand(remaining)))
        physical_order = list(physical_cards)
        order_rng.shuffle(physical_order)
        top_five = tuple(physical_order[:5])

        # Independent random priorities provide a uniform replacement deck
        # order for every selected-card subset after Stellar Wish shuffles.
        rank_ids = list(range(len(physical_cards)))
        reshuffle_rng.shuffle(rank_ids)
        ranks = {physical_cards[index][0]: i for i, index in enumerate(rank_ids)}

        cache: dict[tuple[int | None, int], dict[str, bool]] = {}

        def rescue_at(picked: tuple[int, str] | None, use: int) -> dict[str, bool]:
            key = (None if picked is None else picked[0], use)
            if key in cache:
                return cache[key]
            if picked is None:
                actual_remaining = remaining
                actual_order = tuple(card for _, card in physical_order)
            else:
                physical_index, card = picked
                actual_remaining = remaining.copy()
                actual_remaining[card] -= 1
                if actual_remaining[card] == 0:
                    del actual_remaining[card]
                actual_order = tuple(
                    item for _, item in sorted(
                        (pair for pair in physical_cards if pair[0] != physical_index),
                        key=lambda pair: ranks[pair[0]],
                    )
                )
            after = deck_after_tickets(actual_remaining, state.prizes, actual_order, use)
            cache[key] = {endpoint: endpoint_success(endpoint, hand, after, state.active)
                          for endpoint in ENDPOINTS if not before[endpoint]}
            return cache[key]

        for package, assignment in PACKAGES.items():
            tickets, maps = package_items(hand, assignment)
            pick = select_post_gnh_stellar(hand, assignment, top_five) if eligible else None
            if pick is not None:
                role = assignment[TECH_SLOTS.index(pick[1])]
                modified_tickets = tickets + int(role == "T")
                modified_maps = maps + int(role == "M")
                selected[package] += 1
                access_first[package] += int(tickets == 0 and modified_tickets >= 1)
                access_second[package] += int(
                    (tickets < 2 or maps < 1)
                    and modified_tickets >= 2 and modified_maps >= 1
                )
            else:
                modified_tickets, modified_maps = tickets, maps

            if all(before.values()):
                continue
            old_first = rescue_at(None, 1) if tickets >= 1 else {}
            old_second = rescue_at(None, 2) if tickets >= 2 and maps >= 1 else {}
            new_first = rescue_at(pick, 1) if modified_tickets >= 1 else {}
            new_second = rescue_at(pick, 2) if modified_tickets >= 2 and modified_maps >= 1 else {}

            for endpoint, originally_good in before.items():
                if originally_good:
                    continue
                old_ok = old_first.get(endpoint, False) or (
                    tickets >= 2 and maps >= 1 and old_second.get(endpoint, False)
                )
                new_ok = new_first.get(endpoint, False) or (
                    modified_tickets >= 2 and modified_maps >= 1 and new_second.get(endpoint, False)
                )
                no_stellar[(package, endpoint)] += int(old_ok)
                late_stellar[(package, endpoint)] += int(new_ok)
                helps[(package, endpoint)] += int(new_ok and not old_ok)
                hurts[(package, endpoint)] += int(old_ok and not new_ok)

    return Summary(
        raw_trials, accepted, core, eligible_count, baseline,
        no_stellar, late_stellar, helps, hurts, selected,
        access_first, access_second,
    )


def output(summary: Summary) -> str:
    n = summary.accepted
    lines = [
        f"raw={summary.raw}, accepted={n}, core_ready={summary.core}, "
        f"unused Jirachi after G&H={summary.late_stellar_eligible}",
        "package | extra Stellar selections | new first/second-reset access | "
        "dual Stage-2 rescue without/with late Stellar (pp) | paired net gain (pp) | "
        "paired help / hurt counts",
    ]
    for package in PACKAGES:
        old = summary.no_stellar_rescue[(package, "dual_stage2")]
        new = summary.late_stellar_rescue[(package, "dual_stage2")]
        delta = 100 * (new-old)/n
        lines.append(
            f"{package} | {summary.selected[package]} | "
            f"{summary.first_item_access_gain[package]}/"
            f"{summary.second_item_access_gain[package]} | "
            f"{100*old/n:.6f}/{100*new/n:.6f} | "
            f"{delta:+.6f} | "
            f"{summary.late_stellar_helps[(package, 'dual_stage2')]}/"
            f"{summary.late_stellar_hurts[(package, 'dual_stage2')]}"
        )
    lines.append("all endpoints paired net gain from late Stellar Wish (pp):")
    for endpoint in ENDPOINTS:
        lines.append(endpoint + " | " +
                     " | ".join(f"{100*(summary.late_stellar_rescue[(name, endpoint)] - summary.no_stellar_rescue[(name, endpoint)]) /n:+.6f}"
                                for name in PACKAGES))
    return "\n".join(lines)


if __name__ == "__main__":
    print(output(simulate()))
