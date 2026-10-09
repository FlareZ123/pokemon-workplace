"""Aichi Guzma & Hala payment versus late Jirachi Ticket/Map access.

Counts held Item resources only. Post-G&H Stellar Wish sees an exchangeable
random five-card sample because G&H shuffles the deck. Discard selection is
endpoint-conditioned and hindsight-optimal, hence an upper bound before K1.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from math import comb
import random

from tools.aichi_gnh_discard_frontier import paid_gnh_states
from tools.aichi_jirachi_ticket_search import (
    prepare_with_deferred_stellar, stellar_available,
)
from tools.aichi_post_gnh_prize_reset import (
    DECK, ENDPOINTS, TECH_SLOTS, endpoint_success, prepare, protect_gnh_outputs,
)
from tools.aichi_repeated_ticket_access import PACKAGES, package_items

OBJECTIVES = ("dual_stage2", "item_lock", "item_plus_pidgeot")
WINDOWS = ("first", "second")


def sample_hit_probability(deck_size: int, targets: int, sample_size: int = 5) -> float:
    """Hypergeometric probability of at least one sought Trainer in the top 5."""
    assert 0 <= targets <= deck_size
    n = min(deck_size, sample_size)
    if not targets or not n:
        return 0.0
    return 1.0 - comb(deck_size - targets, n) / comb(deck_size, n) if deck_size - targets >= n else 1.0


def accessible_probability(
    hand: Counter[str], deck: Counter[str],
    assignment: tuple[str, ...], eligible: bool, window: str,
) -> float:
    """Optimal probability of enough held Tickets/Maps after one Stellar Wish."""
    tickets, maps = package_items(hand, assignment)
    if window == "first":
        if tickets >= 1:
            return 1.0
        target_roles = frozenset(("T",))
    elif window == "second":
        if tickets >= 2 and maps >= 1:
            return 1.0
        if tickets == 1 and maps >= 1:
            target_roles = frozenset(("T",))
        elif tickets >= 2 and maps == 0:
            target_roles = frozenset(("M",))
        else:
            return 0.0
    else:
        raise ValueError(window)
    if not eligible:
        return 0.0
    count = sum(deck[TECH_SLOTS[i]] for i, role in enumerate(assignment)
                if role in target_roles)
    return sample_hit_probability(sum(deck.values()), count)


@dataclass
class Summary:
    raw: int = 0
    accepted: int = 0
    core: int = 0
    eligible: int = 0
    offered: Counter[str] = field(default_factory=Counter)
    paid_endpoint: Counter[str] = field(default_factory=Counter)
    total: Counter[tuple[str, str, str, str]] = field(default_factory=Counter)
    larger_paid_late: Counter[tuple[str, str, str]] = field(default_factory=Counter)


def simulate(raw_trials: int = 30_000, seed: int = 20261009,
             *, defer_redundant_stellar: bool = True) -> Summary:
    rng = random.Random(seed)
    s = Summary(raw=raw_trials)
    for _ in range(raw_trials):
        order = rng.sample(range(len(DECK)), len(DECK))
        if defer_redundant_stellar:
            state, deferred = prepare_with_deferred_stellar(order)
        else:
            state, deferred = prepare(order), False
        if state is None:
            continue
        s.accepted += 1
        protected = protect_gnh_outputs(state)
        if protected is None:
            continue
        s.core += 1
        eligible = deferred or stellar_available(order, state.active)
        s.eligible += int(eligible)
        before_hand, before_deck = protected
        paid = paid_gnh_states(state)
        for objective in OBJECTIVES:
            if not endpoint_success(objective, before_hand, before_deck, state.active):
                continue
            s.offered[objective] += 1
            valid = tuple(p for p in paid
                          if endpoint_success(objective, p.hand, p.remaining, state.active))
            s.paid_endpoint[objective] += int(bool(valid))
            for package, assignment in PACKAGES.items():
                for window in WINDOWS:
                    nominal_natural = accessible_probability(
                        before_hand, before_deck, assignment, False, window)
                    nominal_late = accessible_probability(
                        before_hand, before_deck, assignment, eligible, window)
                    paid_natural = max((
                        accessible_probability(p.hand, p.remaining, assignment, False, window)
                        for p in valid), default=0.0)
                    paid_late = max((
                        accessible_probability(p.hand, p.remaining, assignment, eligible, window)
                        for p in valid), default=0.0)
                    key = (objective, package, window)
                    s.total[(*key, "nominal_natural")] += nominal_natural
                    s.total[(*key, "nominal_late")] += nominal_late
                    s.total[(*key, "paid_natural")] += paid_natural
                    s.total[(*key, "paid_late")] += paid_late
                    if paid_late > nominal_late + 1e-12:
                        s.larger_paid_late[key] += 1
                    assert paid_natural <= nominal_natural + 1e-12
                    assert paid_late + 1e-12 >= paid_natural
    return s


def output(s: Summary) -> str:
    lines = [
        f"raw={s.raw} accepted={s.accepted} core={s.core} eligible_late={s.eligible}",
        "endpoint | optimistic ready | feasible after payment",
    ]
    for ep in OBJECTIVES:
        lines.append(f"{ep} | {s.offered[ep]} | {s.paid_endpoint[ep]}")
    lines.append(
        "endpoint | package | reset | nominal natural | paid natural | "
        "nominal late | paid late | states paid-late > nominal-late "
        "(all percentages of accepted openings)"
    )
    for ep in OBJECTIVES:
        for package in PACKAGES:
            for window in WINDOWS:
                key = (ep, package, window)
                vals = [100 * s.total[(*key, label)] / s.accepted for label in
                        ("nominal_natural", "paid_natural", "nominal_late", "paid_late")]
                if package != "baseline":
                    lines.append(f"{ep} | {package} | {window} | " +
                                 " | ".join(f"{v:.6f}%" for v in vals) +
                                 f" | {s.larger_paid_late[key]}")
    return "\n".join(lines)


if __name__ == "__main__":
    print(output(simulate()))
