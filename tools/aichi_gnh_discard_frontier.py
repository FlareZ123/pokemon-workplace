"""Legal optional discard-payment frontier for Guzma & Hala in Aichi setup.

The original Aichi first-turn model materializes G&H's TM: Evolution and
Jet Energy without checking its two-card optional discard. This module
enumerates all legal discard pairs *before* searching, and then asks whether
specific first-turn setup goals and held Ticket/Map access survive.

The endpoint-conditioned existence test is an optimistic upper bound: the
simulator can choose a pair after seeing a modeled state, whereas the actual
player may not yet have learned Prize composition before this payment.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from itertools import combinations_with_replacement
import random

from tools.aichi_post_gnh_prize_reset import (
    DECK, ENDPOINTS, Prepared, endpoint_success,
    prepare, protect_gnh_outputs,
)
from tools.aichi_repeated_ticket_access import PACKAGES, package_items


REQUIRED_OUTPUTS = ("Technical Machine: Evolution", "Jet Energy")


@dataclass(frozen=True)
class PaidState:
    hand: Counter[str]
    remaining: Counter[str]
    paid_with: tuple[str, str] | None


def _get_gnh_outputs(
    hand: Counter[str], remaining: Counter[str], payment: tuple[str, str] | None,
) -> PaidState | None:
    """After optional payment, legally take the necessary Tool/Energy outputs."""
    held = hand.copy()
    deck = remaining.copy()
    if payment is not None:
        for card in payment:
            held[card] -= 1
            if held[card] == 0:
                del held[card]

    for card in REQUIRED_OUTPUTS:
        if not held[card]:
            if payment is None or not deck[card]:
                return None
            deck[card] -= 1
            if deck[card] == 0:
                del deck[card]
            held[card] += 1

    # G&H Stadium search is independent of its optional two-card discard.
    if held["Artazon"] == 0 and deck["Artazon"] > 0:
        deck["Artazon"] -= 1
        if deck["Artazon"] == 0:
            del deck["Artazon"]
        held["Artazon"] += 1
    return PaidState(held, deck, payment)


def paid_gnh_states(state: Prepared, protected_names: frozenset[str] = frozenset()) -> list[PaidState]:
    """Enumerate physically legal full-output paths for the available G&H.

    Payment is required only when the necessary Tool or Special Energy is not
    already in hand. Discard candidates are exactly the other cards present
    after G&H itself was played and any Tag Call action in the original setup.
    """
    if not state.gnh_access:
        return []

    if all(state.hand[card] > 0 for card in REQUIRED_OUTPUTS):
        preserved = _get_gnh_outputs(state.hand, state.remaining, None)
        return [preserved] if preserved is not None else []

    choices = sorted(name for name, count in state.hand.items() if count > 0)
    options = []
    for a, b in combinations_with_replacement(choices, 2):
        if (a in protected_names or b in protected_names) or (a == b and state.hand[a] < 2):
            continue
        candidate = _get_gnh_outputs(state.hand, state.remaining, (a, b))
        if candidate is not None:
            options.append(candidate)
    return options


@dataclass
class Summary:
    raw: int
    accepted: int
    core_offered: int
    payment_feasible: int
    original_baseline: Counter[str]
    paid_baseline: Counter[str]
    nominal_first: Counter[str]
    nominal_second: Counter[str]
    paid_first: Counter[str]
    paid_second: Counter[str]
    original_dual_and_first: Counter[str]
    paid_dual_and_first: Counter[str]
    original_dual_and_second: Counter[str]
    paid_dual_and_second: Counter[str]


def simulate(raw_trials: int = 200_000, seed: int = 20261008) -> Summary:
    rng = random.Random(seed)
    accepted = core_offered = payment_feasible = 0
    baseline: Counter[str] = Counter()
    paid_baseline: Counter[str] = Counter()
    nominal_first: Counter[str] = Counter()
    nominal_second: Counter[str] = Counter()
    paid_first: Counter[str] = Counter()
    paid_second: Counter[str] = Counter()
    orig_dual_first: Counter[str] = Counter()
    paid_dual_first: Counter[str] = Counter()
    orig_dual_second: Counter[str] = Counter()
    paid_dual_second: Counter[str] = Counter()

    for _ in range(raw_trials):
        order = rng.sample(range(len(DECK)), len(DECK))
        state = prepare(order)
        if state is None:
            continue
        accepted += 1
        optimistic = protect_gnh_outputs(state)
        if optimistic is None:
            continue
        core_offered += 1
        baseline_hand, baseline_deck = optimistic
        original = {endpoint: endpoint_success(endpoint, baseline_hand,
                       baseline_deck, state.active) for endpoint in ENDPOINTS}
        baseline.update(endpoint for endpoint, success in original.items() if success)

        paths = paid_gnh_states(state)
        if paths:
            payment_feasible += 1
        paid_goal = {
            endpoint: any(
                endpoint_success(endpoint, p.hand, p.remaining, state.active)
                for p in paths
            )
            for endpoint in ENDPOINTS if original[endpoint]
        }
        paid_baseline.update(
            endpoint for endpoint in ENDPOINTS if paid_goal.get(endpoint, False)
        )
        paid_dual_paths = [
            p for p in paths if original["dual_stage2"] and
            endpoint_success("dual_stage2", p.hand, p.remaining, state.active)
        ]

        for package, assignment in PACKAGES.items():
            t, m = package_items(state.hand, assignment)
            nominal_first[package] += int(t >= 1)
            nominal_second[package] += int(t >= 2 and m >= 1)

            first_possible = any(package_items(p.hand, assignment)[0] >= 1
                                 for p in paths)
            second_possible = any(
                (lambda counts: counts[0] >= 2 and counts[1] >= 1)(
                    package_items(p.hand, assignment)
                ) for p in paths
            )
            paid_first[package] += int(first_possible)
            paid_second[package] += int(second_possible)

            orig_dual_first[package] += int(original["dual_stage2"] and t >= 1)
            orig_dual_second[package] += int(
                original["dual_stage2"] and t >= 2 and m >= 1
            )
            paid_dual_first[package] += int(
                any(package_items(p.hand, assignment)[0] >= 1
                    for p in paid_dual_paths)
            )
            paid_dual_second[package] += int(
                any(package_items(p.hand, assignment)[0] >= 2
                    and package_items(p.hand, assignment)[1] >= 1
                    for p in paid_dual_paths)
            )

    return Summary(
        raw_trials, accepted, core_offered, payment_feasible,
        baseline, paid_baseline, nominal_first, nominal_second,
        paid_first, paid_second, orig_dual_first, paid_dual_first,
        orig_dual_second, paid_dual_second,
    )


def output(s: Summary) -> str:
    n = s.accepted
    lines = [
        f"raw={s.raw} accepted={s.accepted} core_offered={s.core_offered} "
        f"some legal G&H payment={s.payment_feasible}",
        "endpoint | original optimistic baseline% | payment-aware existence upper-bound%",
    ]
    for endpoint in ENDPOINTS:
        lines.append(f"{endpoint} | {100*s.original_baseline[endpoint]/n:.5f} | "
                     f"{100*s.paid_baseline[endpoint]/n:.5f}")
    lines.append("package | first Ticket nominal/payment-feasible% | "
                 "second reset nominal/payment-feasible% | "
                 "dual endpoint+first nominal/payment-feasible% | "
                 "dual endpoint+second nominal/payment-feasible%")
    for package in PACKAGES:
        lines.append(f"{package} | "
                     f"{100*s.nominal_first[package]/n:.5f}/"
                     f"{100*s.paid_first[package]/n:.5f} | "
                     f"{100*s.nominal_second[package]/n:.5f}/"
                     f"{100*s.paid_second[package]/n:.5f} | "
                     f"{100*s.original_dual_and_first[package]/n:.5f}/"
                     f"{100*s.paid_dual_and_first[package]/n:.5f} | "
                     f"{100*s.original_dual_and_second[package]/n:.5f}/"
                     f"{100*s.paid_dual_and_second[package]/n:.5f}")
    return "\n".join(lines)


if __name__ == "__main__":
    print(output(simulate()))
