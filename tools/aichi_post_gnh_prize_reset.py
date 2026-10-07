from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
import random

# Published Aichi 2026 runner-up list. Four first-turn-neutral Supporter slots are
# tagged so 1..4 can be reinterpreted as Prize-reset Item techs without changing
# any represented first-turn connector or setup count.
DECK_COUNTS = {
    "Pidgey": 2,
    "Pidgeotto": 2,
    "Pidgeot ex": 2,
    "Oddish": 2,
    "Gloom": 2,
    "Vileplume": 2,
    "Vileplume-GX": 1,
    "Lillipup": 2,
    "Herdier": 2,
    "Stoutland": 1,
    "Bunnelby": 2,
    "Fan Rotom": 1,
    "Relicanth": 1,
    "Mr. Mime": 1,
    "Girafarig": 1,
    "Budew": 1,
    "Jirachi": 1,
    "Guzma & Hala": 4,
    "Guzma": 2,
    "TechSlot1": 1,  # Team Yell's Cheer
    "TechSlot2": 1,  # Karen
    "TechSlot3": 1,  # Plumeria
    "TechSlot4": 1,  # Cassius
    "Gladion": 1,
    "Faba": 1,
    "Lusamine": 1,
    "Bellelba & Brycen-Man": 1,
    "Peonia": 1,
    "Tag Call": 4,
    "Stealthy Hood": 3,
    "Technical Machine: Evolution": 2,
    "Counter Gain": 1,
    "Artazon": 2,
    "Grand Tree": 1,
    "Capture Energy": 2,
    "Jet Energy": 2,
    "Memory Energy": 1,
    "Grass Energy": 1,
}

BASICS = {
    "Pidgey", "Oddish", "Lillipup", "Bunnelby", "Fan Rotom",
    "Relicanth", "Mr. Mime", "Girafarig", "Budew", "Jirachi",
}

ENDPOINTS = {
    "double_tm": (),
    "pidgeot_stage2": ("Pidgey",),
    "stoutland_stage2": ("Lillipup",),
    "dual_stage2": ("Pidgey", "Lillipup"),
    "item_lock": ("Oddish",),
    "item_plus_pidgeot": ("Oddish", "Pidgey"),
    "item_plus_stoutland": ("Oddish", "Lillipup"),
}

STAGES = {
    "double_tm": (),
    "pidgeot_stage2": ("Pidgeotto", "Pidgeot ex"),
    "stoutland_stage2": ("Herdier", "Stoutland"),
    "dual_stage2": ("Pidgeotto", "Pidgeot ex", "Herdier", "Stoutland"),
    "item_lock": ("Gloom", "Vileplume"),
    "item_plus_pidgeot": ("Gloom", "Vileplume", "Pidgeotto", "Pidgeot ex"),
    "item_plus_stoutland": ("Gloom", "Vileplume", "Herdier", "Stoutland"),
}

TECH_SLOTS = tuple(f"TechSlot{i}" for i in range(1, 5))
DECK = tuple(card for card, copies in DECK_COUNTS.items() for _ in range(copies))
assert len(DECK) == 60


@dataclass(frozen=True)
class Prepared:
    hand: Counter[str]
    remaining: Counter[sty]
    active: str
    prizes: tuple[str, ...]
    gnh_access: bool


def prepare(order: list[int]) -> Prepared | None:
    opening = [DECK[i] for i in order[:7]]
    if not any(card in BASICS for card in opening):
        return None
    prizes = tuple(DECK[i] for i in order[7:13])
    draw = DECK[order[13]]
    top_five = tuple(DECK[i] for i in order[14:19])

    opening_basics = [card for card in opening if card in BASICS]
    if "Jirachi" in opening_basics:
        active = "Jirachi"
    else:
        non_bunnelby = [card for card in opening_basics if card != "Bunnelby"]
        active = non_bunnelby[0] if non_bunnelby else "Bunnelby"

    hand = Counter(opening + [draw])
    hand[active] -= 1
    if hand[active] == 0:
        del hand[active]

    remaining = Counter(DECK)
    for card in opening + list(prizes) + [draw]:
        remaining[card] -= 1
        if remaining[card] == 0:
            del remaining[card]

    # Match the established named-route Stellar Wish policy.
    if active == "Jirachi":
        pick = None
        if "Guzma & Hala" in top_five:
            pick = "Guzma & Hala"
        elif "Tag Call" in top_five:
            pick = "Tag Call"
        if pick is not None:
            hand[pick] += 1
            remaining[pick] -= 1
            if remaining[pick] == 0:
                del remaining[pick]

    gnh_access = False
    if hand["Guzma & Hala"] > 0:
        gnh_access = True
    elif hand["Tag Call"] > 0 and remaining["Guzma & Hala"] > 0:
        hand["Tag Call"] -= 1
        if hand["Tag Call"] == 0:
            del hand["Tag Call"]
        remaining["Guzma & Hala"] -= 1
        if remaining["Guzma & Hala"] == 0:
            del remaining["Guzma & Hala"]
        hand["Guzma & Hala"] += 1
        gnh_access = True

    if gnh_access:
        hand["Guzma & Hala"] -= 1
        if hand["Guzma & Hala"] == 0:
            del hand["Guzma & Hala"]

    return Prepared(hand, remaining, active, prizes, gnh_access)


def protect_gnh_outputs(state: Prepared) -> tuple[Counter[str], Counter[str]] | None:
    if not state.gnh_access:
        return None
    hand = state.hand.copy()
    remaining = state.remaining.copy()

    # Post-G&H reset means the Tool, Special Energy, and Stadium output can be
    # materialized first and cannot be newly Prized by the reset.
    for card in ("Technical Machine: Evolution", "Jet Energy"):
        if hand[card] == 0:
            if remaining[card] == 0:
                return None
            remaining[card] -= 1
            if remaining[card] == 0:
                del remaining[card]
            hand[card] += 1
    if hand["Artazon"] == 0 and remaining["Artazon"] > 0:
        remaining["Artazon"] -= 1
        if remaining["Artazon"] == 0:
            del remaining["Artazon"]
        hand["Artazon"] += 1
    return hand, remaining


def basic_possible(hand: Counter[str], remaining: Counter[str], active: str, required: tuple[str, ...]) -> bool:
    needs = Counter(required)
    needs["Bunnelby"] += 1
    direct = Counter(hand)
    direct[active] += 1

    direct_fan = hand["Fan Rotom"] > 0 or active == "Fan Rotom"
    actions: list[str | None] = [None]
    if hand["Artazon"] > 0:
        relevant = set(needs)
        relevant.add("Fan Rotom")
        actions.extend(card for card in relevant if remaining[card] > 0)

    for artazon_fetch in actions:
        have = direct.copy()
        fan_available = direct_fan
        if artazon_fetch == "Fan Rotom":
            fan_available = True
        elif artazon_fetch is not None:
            have[artazon_fetch] += 1

        if fan_available:
            fan_fetches: list[str] = []
            for card in ("Bunnelby", "Pidgey", "Lillipup"):
                missing = max(0, needs[card] - have[card])
                if missing and remaining[card] >= missing and artazon_fetch != card:
                    fan_fetches.extend([card] * missing)
            if len(fan_fetches) <= 3:
                for card in fan_fetches:
                    have[card] += 1

        if all(have[card] >= copies for card, copies in needs.items()):
            return True
    return False


def endpoint_success(endpoint: str, hand: Counter[str], remaining: Counter[str], active: str) -> bool:
    if not basic_possible(hand, remaining, active, ENDPOINTS[endpoint]):
        return False
    return all(remaining[card] > 0 for card in STAGES[endpoint])


def expand(counter: Counter[str]) -> list[str]:
    return [card for card, copies in counter.items() for _ in range(copies)]


def reset_deck(kind: str, remaining: Counter[str], old_prizes: tuple[str, ...], rng: random.Random) -> Counter[str]:
    current = expand(remaining)
    prize_count = len(old_prizes)
    if kind == "ticket":
        indices = rng.sample(range(len(current)), prize_count)
        new_prizes = Counter(current[i] for i in indices)
        out = remaining.copy()
        out.subtract(new_prizes)
        out += Counter(old_prizes)
        return +out
    if kind == "rotom":
        pool = current + list(old_prizes)
        indices = rng.sample(range(len(pool)), prize_count)
        new_prizes = Counter( pool[i] for i in indices )
        out = Counter(pool)
        out.subtract(new_prizes)
        return +out
    raise ValueError(kind)


def min_accessible_slot(hand: Counter[str]) -> int | None:
    for i, slot in enumerate(TECH_SLOTS, start=1):
        if hand[slot] > 0:
            return i
    return None


@dataclass
class Summary:
    raw_trials: int
    accepted: int
    gnh_core_ready: int
    baseline: Counter[str]
    access: Counter[int]
    fail_access: dict[tuple[str, int], int]
    rescue: dict[tuple[str, str, int], int]


def simulate(raw_trials: int = 100_000, seed: int = 20261007) -> Summary:
    rng = random.Random(seed)
    ticket_rng = random.Random(seed ^ 0x71C0E7)
    rotom_rng = random.Random(seed ^ 0xB070D3)

    accepted = 0
    gnh_core_ready = 0
    baseline: Counter[str] = Counter()
    access: Counter[int] = Counter()
    fail_access: dict[tuple[str, int], int] = defaultdict(int)
    rescue: dict[tuple[str, str, int], int] = defaultdict(int)

    for _ in range(raw_trials):
        order = rng.sample(range(60), 60)
        state = prepare(order)
        if state is None:
            continue
        accepted += 1
        protected = protect_gnh_outputs(state)
        if protected is None:
            continue
        gnh_core_ready += 1
        hand, remaining = protected

        baseline_state = {
            endpoint: endpoint_success(endpoint, hand, remaining, state.active)
            for endpoint in ENDPOINTS
        }
        for endpoint, ok in baseline_state.items():
            baseline[endpoint] += int(ok)

        first_slot = min_accessible_slot(hand)
        if first_slot is None:
            continue
        for copies in range(first_slot, 5):
            access[copies] += 1

        post_ticket = reset_deck("ticket", remaining, state.prizes, ticket_rng)
        post_rotom = reset_deck("rotom", remaining, state.prizes, rotom_rng)

        for endpoint, ok in baseline_state.items():
            if ok:
                continue
            ticket_ok = endpoint_success(endpoint, hand, post_ticket, state.active)
            rotom_ok = endpoint_success(endpoint, hand, post_rotom, state.active)
            for copies in range(first_slot, 5):
                fail_access[(endpoint, copies)] += 1
                rescue[("ticket", endpoint, copies)] += int(ticket_ok)
                rescue[("rotom", endpoint, copies)] += int(rotom_ok)

    return Summary(raw_trials, accepted, gnh_core_ready, baseline, access, dict(fail_access), dict(rescue))


def pct(n: float, d: float) -> float:
    return 100.0 * n / d if d else 0.0


def main() -> None:
    s = simulate()
    print(f"raw_trials={s.raw_trials}")
    print(f"accepted={s.accepted} ({pct(s.accepted, s.raw_trials):.6f}%)")
    print(f"gnh_core_ready={s.gnh_core_ready} ({pct(s.gnh_core_ready, s.accepted):.6f}% of accepted)")
    print("baseline endpoint rates among accepted:")
    for endpoint in ENDPOINTS:
        print(f"  {endpoint}: {pct(s.baseline[endpoint], s.accepted):.6f}%")
    print("\ncopy curves: access and informed one-reset lift in percentage points")
    for copies in range(1, 5):
        print(f"copies={copies} access={pct(s.access[copies], s.accepted):.6f}% accepted, {pct(s.access[copies], s.gnh_core_ready):.6f}% core-ready")
        for endpoint in ENDPOINTS:
            fail = s.fail_access[(endpoint, copies)]
            t = s.rescue[("ticket", endpoint, copies)]
            r = s.rescue[("rotom", endpoint, copies)]
            print(
                f"  {endpoint}: ticket_lift={pct(t, s.accepted):.6f}pp "
                f"rotom_lift={pct(r, s.accepted):.6f}pp "
                f"ticket_conversion={pct(t, fail):.6f}%"
                f"rotom_conversion={pct(r, fail):.6f}%"
            )


if __name__ == "__main__":
    main()
