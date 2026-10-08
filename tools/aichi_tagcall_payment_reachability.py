"""Tag Call as a pre-G&H discard-fuel connector in Aichi Vileplume.

Tag Call can fetch up to two TAG TEAM cards. After obtaining the G&H intended
for the turn, another naturally held Tag Call may fetch two *additional*
Guzma & Hala copies and convert those into legal discard-payment cards.

This is modeled as an optional legal Item action BEFORE playing G&H, even
though the original Aichi preparer abstracts the G&H Supporter as consumed.
The retained hand/deck counters encode the resulting zones. A Tag Call play
also reveals the full deck, potentially upgrading Prize knowledge from K0
to K1 before G&H's optional two-card payment.

Protected-card sensitivity is a named, illustrative constraint, not a claim
that any such card is always undiscardable.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import random

from tools.aichi_post_gnh_prize_reset import (
    DECK, ENDPOINTS, Prepared, endpoint_success, prepare, protect_gnh_outputs,
)
from tools.aichi_gnh_discard_frontier import PaidState, paid_gnh_states
from tools.aichi_repeated_ticket_access import PACKAGES, package_items
from tools.aichi_post_gnh_prize_reset import TECH_SLOTS


PROTECTED_SINGLETON_SUPPORTERS = frozenset({
    "Gladion", "Faba", "Lusamine", "Peonia", "Bellelba & Brycen-Man",
})


def additional_tag_call(state: Prepared) -> Prepared | None:
    """Spend one held Tag Call to fetch up to two remaining G&H copies.

    The Supporter originally played stays consumed; these are *additional*
    copies, chosen as payment payloads. This is a candidate action only:
    playing no extra Tag Call remains separately available.
    """
    if not state.gnh_access or state.hand["Tag Call"] < 1:
        return None
    take = min(2, state.remaining["Guzma & Hala"])
    if not take:
        return None
    hand = state.hand.copy()
    deck = state.remaining.copy()
    hand["Tag Call"] -= 1
    if hand["Tag Call"] == 0:
        del hand["Tag Call"]
    hand["Guzma & Hala"] += take
    deck["Guzma & Hala"] -= take
    if deck["Guzma & Hala"] == 0:
        del deck["Guzma & Hala"]
    return Prepared(hand, deck, state.active, state.prizes, True)


def protected_names_for_package(package: str) -> frozenset[str]:
    assignment = PACKAGES[package]
    actual_items = {
        TECH_SLOTS[i] for i, role in enumerate(assignment) if role in ("T", "M")
    }
    return PROTECTED_SINGLETON_SUPPORTERS.union(actual_items)


def property_values(paths: list[PaidState], package: str, active: str):
    assignment = PACKAGES[package]
    first = second = dual = dual_first = dual_second = False
    for p in paths:
        t, m = package_items(p.hand, assignment)
        first |= t >= 1
        second |= t >= 2 and m >= 1
        endpoint = endpoint_success("dual_stage2", p.hand, p.remaining, active)
        dual |= endpoint
        dual_first |= endpoint and t >= 1
        dual_second |= endpoint and t >= 2 and m >= 1
    return (bool(paths), first, second, dual, dual_first, dual_second)


@dataclass
class Summary:
    raw: int
    accepted: int
    core: int
    extra_tagcall_available: int
    # Metric key (package, dimension): dimension 0=payment possible,
    # 1=first reset access, 2=second reset access,
    # 3=dual endpoint, 4=dual+first, 5=dual+second.
    ordinary: Counter[tuple[str, int]]
    enhanced: Counter[tuple[str, int]]
    gained: Counter[tuple[str, int]]


DIMENSIONS = (
    "can_pay_G&H",
    "first_Ticket_preserved",
    "second_informed_reset_preserved",
    "dual_Stage2_endpoint",
    "dual_Stage2_plus_first",
    "dual_Stage2_plus_second",
)


def simulate(raw_trials: int = 100_000, seed: int = 20261008) -> Summary:
    rng = random.Random(seed)
    accepted = core = tag_available = 0
    ordinary: Counter[tuple[str, int]] = Counter()
    enhanced: Counter[tuple[str, int]] = Counter()
    gained: Counter[tuple[str, int]] = Counter()

    for _ in range(raw_trials):
        order = rng.sample(range(len(DECK)), len(DECK))
        state = prepare(order)
        if state is None:
            continue
        accepted += 1
        if protect_gnh_outputs(state) is None:
            continue
        core += 1
        boosted = additional_tag_call(state)
        tag_available += int(boosted is not None)

        for package in PACKAGES:
            protected = protected_names_for_package(package)
            natural = paid_gnh_states(state, protected)
            augmented = natural + (
                paid_gnh_states(boosted, protected) if boosted is not None else []
            )
            old_values = property_values(natural, package, state.active)
            new_values = property_values(augmented, package, state.active)
            for i, (old, new) in enumerate(zip(old_values, new_values)):
                ordinary[(package, i)] += int(old)
                enhanced[(package, i)] += int(new)
                gained[(package, i)] += int(new and not old)

    return Summary(raw_trials, accepted, core, tag_available,
                   ordinary, enhanced, gained)


def output(s: Summary) -> str:
    n = s.accepted
    lines = [
        f"raw={s.raw}, accepted={n}, G&H core={s.core}, "
        f"additional Tag Call available with G&H in deck={s.extra_tagcall_available}",
        "Protected names: five singleton disruption/recovery Supporters plus each "
        "package's held Ticket/Map Item slots. First-turn sensitivity assumption.",
        "package | preserve Item payment baseline/TagCall-aided (% accepted) | "
        "dual endpoint and Item baseline/TagCall-aided (% accepted) | "
        "incremental gained accepted starts",
    ]
    for package in PACKAGES:
        one = (s.ordinary[(package, 1)], s.enhanced[(package, 1)])
        dual_one = (s.ordinary[(package, 4)], s.enhanced[(package, 4)])
        lines.append(
            f"{package} | {100*one[0]/n:.5f}/{100*one[1]/n:.5f} | "
            f"{100*dual_one[0]/n:.5f}/{100*dual_one[1]/n:.5f} | "
            f"{s.gained[(package, 4)]}"
        )
    lines.append("two Ticket + one Map package, every measured dimension:")
    package = "two_tickets_one_map"
    for i, label in enumerate(DIMENSIONS):
        lines.append(
            f"{label} | {100*s.ordinary[(package, i)]/n:.7f}% -> "
            f"{100*s.enhanced[(package, i)]/n:.7f}% "
            f"(+{100*s.gained[(package, i)]/n:.7f}pp)"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    print(output(simulate()))
