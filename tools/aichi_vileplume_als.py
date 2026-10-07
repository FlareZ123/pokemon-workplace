"""Model the Guzma & Hala Bunnelby Evolution ALS in the 2026 Aichi runner-up list.

Scope:
- paper Expanded;
- first turn going second;
- accepted seven-card opening conditioned on at least one ordinary Basic;
- six Prize cards;
- one draw for turn;
- the published Tag Call / Guzma & Hala / Jet Energy / TM: Evolution route;
- optional Jirachi Stellar Wish if Jirachi was the starting Active;
- endpoint-aware allocation of Artazon between Fan Rotom and direct Basic access.

The model intentionally measures the Guzma & Hala mediated route rather than every
possible natural-draw route to the same board.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from math import comb, sqrt
import random


DECK_COUNTS: dict[str, int] = {
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
    "Cassius": 1,
    "Karen": 1,
    "Plumeria": 1,
    "Gladion": 1,
    "Faba": 1,
    "Lusamine": 1,
    "Bellelba & Brycen-Man": 1,
    "Peonia": 1,
    "Team Yell's Cheer": 1,
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
    "Pidgey",
    "Oddish",
    "Lillipup",
    "Bunnelby",
    "Fan Rotom",
    "Relicanth",
    "Mr. Mime",
    "Girafarig",
    "Budew",
    "Jirachi",
}
FAN_TARGETS = {"Bunnelby", "Pidgey", "Lillipup"}
ENDPOINTS = (
    "double_tm",
    "pidgeot_stage2",
    "stoutland_stage2",
    "dual_stage2",
    "item_lock",
    "item_plus_pidgeot",
    "item_plus_stoutland",
)

DECK: tuple[str, ...] = tuple(
    card
    for card, copies in DECK_COUNTS.items()
    for _ in range(copies)
)

if len(DECK) != 60:
    raise AssertionError(len(DECK))


@dataclass(frozen=True)
class TrialState:
    hand: Counter[str]
    deck: Counter[str]
    active: str
    mulligans: int
    stellar_hit: bool
    gnh_access: bool


@dataclass(frozen=True)
class SimulationResult:
    trials: int
    successes: dict[str, int]
    mean_mulligans: float

    def probability(self, key: str) -> float:
        return self.successes.get(key, 0) / self.trials

    def normal_95_half_width(self, key: str) -> float:
        p = self.probability(key)
        return 1.96 * sqrt(p * (1.0 - p) / self.trials)


def exact_opening_acceptance() -> float:
    """Probability that a random seven-card hand has at least one ordinary Basic."""
    forced_basics = sum(DECK_COUNTS[name] for name in BASICS)
    return 1.0 - comb(60 - forced_basics, 7) / comb(60, 7)


def exact_expected_mulligans() -> float:
    accepted = exact_opening_acceptance()
    return (1.0 - accepted) / accepted


def _accepted_state(rng: random.Random, *, use_stellar: bool = True) -> TrialState:
    mulligans = 0
    while True:
        order = rng.sample(range(60), 60)
        opening = [DECK[index] for index in order[:7]]
        if any(card in BASICS for card in opening):
            break
        mulligans += 1

    prizes = [DECK[index] for index in order[7:13]]
    draw = DECK[order[13]]
    top_five = [DECK[index] for index in order[14:19]]

    opening_basics = [card for card in opening if card in BASICS]
    if use_stellar and "Jirachi" in opening_basics:
        active = "Jirachi"
    else:
        non_bunnelby = [card for card in opening_basics if card != "Bunnelby"]
        active = non_bunnelby[0] if non_bunnelby else "Bunnelby"

    hand = Counter(opening + [draw])
    hand[active] -= 1
    if hand[active] == 0:
        del hand[active]

    remaining = Counter(DECK)
    for card in opening + prizes + [draw]:
        remaining[card] -= 1

    stellar_hit = False
    if use_stellar and active == "Jirachi":
        pick = None
        if "Guzma & Hala" in top_five:
            pick = "Guzma & Hala"
        elif "Tag Call" in top_five:
            pick = "Tag Call"
        if pick is not None:
            hand[pick] += 1
            remaining[pick] -= 1
            stellar_hit = True

    gnh_access = False
    if hand["Guzma & Hala"] > 0:
        gnh_access = True
    elif hand["Tag Call"] > 0 and remaining["Guzma & Hala"] > 0:
        hand["Tag Call"] -= 1
        if hand["Tag Call"] == 0:
            del hand["Tag Call"]
        remaining["Guzma & Hala"] -= 1
        hand["Guzma & Hala"] += 1
        gnh_access = True

    if gnh_access:
        hand["Guzma & Hala"] -= 1
        if hand["Guzma & Hala"] == 0:
            del hand["Guzma & Hala"]

    return TrialState(
        hand=hand,
        deck=remaining,
        active=active,
        mulligans=mulligans,
        stellar_hit=stellar_hit,
        gnh_access=gnh_access,
    )


def _gnh_search_core(
    hand: Counter[str],
    remaining: Counter[str],
) -> tuple[Counter[str], Counter[str], bool]:
    """Search TM: Evolution and Jet Energy if necessary and available."""
    hand = hand.copy()
    remaining = remaining.copy()
    for name in ("Technical Machine: Evolution", "Jet Energy"):
        if hand[name] == 0:
            if remaining[name] == 0:
                return hand, remaining, False
            remaining[name] -= 1
            hand[name] += 1
    return hand, remaining, True


def _basic_endpoint_possible(
    hand: Counter[str],
    remaining: Counter[str],
    active: str,
    required_evolution_basics: tuple[str, ...],
    *,
    use_fan: bool,
    use_artazon: bool,
    greedy_fan: bool,
) -> bool:
    """Test Basic setup while allocating the single Artazon use.

    If Bunnelby is already Active, Jet Energy can be attached to that Bunnelby:
    its switch effect does not trigger, but it still provides Colorless Energy.
    Otherwise Bunnelby must be Benched before Jet is attached; Jet then promotes
    it and moves the prior Active to the Bench, where that Pokémon can satisfy an
    Evolution target.
    """
    needs = Counter(required_evolution_basics)
    needs["Bunnelby"] += 1

    direct = Counter(hand)
    direct[active] += 1

    direct_fan = use_fan and (hand["Fan Rotom"] > 0 or active == "Fan Rotom")
    artazon_available = use_artazon and (
        hand["Artazon"] > 0 or remaining["Artazon"] > 0
    )

    actions: list[str | None] = [None]
    if artazon_available:
        relevant = set(needs)
        if use_fan:
            relevant.add("Fan Rotom")
        actions.extend(
            card
            for card in relevant
            if remaining[card] > 0
        )

    if greedy_fan and use_fan and not direct_fan and artazon_available:
        if remaining["Fan Rotom"] > 0:
            actions = ["Fan Rotom"]

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


def evaluate_state(
    state: TrialState,
    *,
    use_fan: bool = True,
    use_artazon: bool = True,
    greedy_fan: bool = False,
) -> dict[str, bool]:
    out = {"gnh_access": state.gnh_access, "stellar_hit": state.stellar_hit}
    out.update({key: False for key in ENDPOINTS})
    if not state.gnh_access:
        return out

    hand, remaining, core_resources = _gnh_search_core(state.hand, state.deck)
    if not core_resources:
        return out

    basic = lambda required: _basic_endpoint_possible(
        hand,
        remaining,
        state.active,
        required,
        use_fan=use_fan,
        use_artazon=use_artazon,
        greedy_fan=greedy_fan,
    )

    core = basic(())
    pidgey = basic(("Pidgey",))
    lillipup = basic(("Lillipup",))
    oddish = basic(("Oddish",))
    dual = basic(("Pidgey", "Lillipup"))
    oddish_pidgey = basic(("Oddish", "Pidgey"))
    oddish_lillipup = basic(("Oddish", "Lillipup"))

    pidgeot_chain = remaining["Pidgeotto"] > 0 and remaining["Pidgeot ex"] > 0
    stoutland_chain = remaining["Herdier"] > 0 and remaining["Stoutland"] > 0
    vileplume_chain = remaining["Gloom"] > 0 and remaining["Vileplume"] > 0

    out["double_tm"] = core
    out["pidgeot_stage2"] = pidgey and pidgeot_chain
    out["stoutland_stage2"] = lillipup and stoutland_chain
    out["dual_stage2"] = dual and pidgeot_chain and stoutland_chain
    out["item_lock"] = oddish and vileplume_chain
    out["item_plus_pidgeot"] = (
        oddish_pidgey and vileplume_chain and pidgeot_chain
    )
    out["item_plus_stoutland"] = (
        oddish_lillipup and vileplume_chain and stoutland_chain
    )
    return out


def simulate(
    trials: int,
    *,
    seed: int = 20261007,
    use_stellar: bool = True,
    use_fan: bool = True,
    use_artazon: bool = True,
    greedy_fan: bool = False,
) -> SimulationResult:
    rng = random.Random(seed)
    successes: Counter[str] = Counter()
    mulligans = 0

    for _ in range(trials):
        state = _accepted_state(rng, use_stellar=use_stellar)
        mulligans += state.mulligans
        result = evaluate_state(
            state,
            use_fan=use_fan,
            use_artazon=use_artazon,
            greedy_fan=greedy_fan,
        )
        for key, value in result.items():
            if value:
                successes[key] += 1

    return SimulationResult(
        trials=trials,
        successes=dict(successes),
        mean_mulligans=mulligans / trials,
    )


def paired_greedy_optimal(
    trials: int,
    *,
    seed: int = 20261007,
) -> tuple[SimulationResult, SimulationResult]:
    """Evaluate greedy and endpoint-aware Artazon routing on identical states."""
    rng = random.Random(seed)
    greedy: Counter[str] = Counter()
    optimal: Counter[str] = Counter()
    mulligans = 0

    for _ in range(trials):
        state = _accepted_state(rng, use_stellar=True)
        mulligans += state.mulligans
        greedy_state = evaluate_state(state, greedy_fan=True)
        optimal_state = evaluate_state(state, greedy_fan=False)

        for key, value in greedy_state.items():
            if value:
                greedy[key] += 1
        for key, value in optimal_state.items():
            if value:
                optimal[key] += 1

        for key in ENDPOINTS:
            if greedy_state[key] and not optimal_state[key]:
                raise AssertionError(("greedy exceeded optimal", key))

    mean = mulligans / trials
    return (
        SimulationResult(trials, dict(greedy), mean),
        SimulationResult(trials, dict(optimal), mean),
    )



RELEVANT_STELLAR = {
    "Guzma & Hala",
    "Tag Call",
    "Technical Machine: Evolution",
    "Artazon",
}


def _raw_accepted_state(
    rng: random.Random,
) -> tuple[Counter[str], Counter[str], str, tuple[str, ...], int]:
    """Return an accepted first-turn state before using Stellar Wish."""
    mulligans = 0
    while True:
        order = rng.sample(range(60), 60)
        opening = [DECK[index] for index in order[:7]]
        if any(card in BASICS for card in opening):
            break
        mulligans += 1

    prizes = [DECK[index] for index in order[7:13]]
    draw = DECK[order[13]]
    top_five = tuple(DECK[index] for index in order[14:19])

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
    for card in opening + prizes + [draw]:
        remaining[card] -= 1

    return hand, remaining, active, top_five, mulligans


def _basic_possible_with_artazon_state(
    hand: Counter[str],
    remaining: Counter[str],
    active: str,
    required_evolution_basics: tuple[str, ...],
    *,
    artazon_available: bool,
) -> bool:
    """Evaluate endpoint Basics with a caller-supplied Artazon availability."""
    needs = Counter(required_evolution_basics)
    needs["Bunnelby"] += 1

    direct = Counter(hand)
    if active != "Bunnelby":
        direct[active] += 1

    direct_fan = hand["Fan Rotom"] > 0 or active == "Fan Rotom"
    actions: list[str | None] = [None]
    if artazon_available:
        relevant = set(needs)
        relevant.add("Fan Rotom")
        actions.extend(
            card
            for card in relevant
            if remaining[card] > 0
        )

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
                if (
                    missing
                    and remaining[card] >= missing
                    and artazon_fetch != card
                ):
                    fan_fetches.extend([card] * missing)
            if len(fan_fetches) <= 3:
                for card in fan_fetches:
                    have[card] += 1

        if all(have[card] >= copies for card, copies in needs.items()):
            return True

    return False


def _resource_route_possible(
    hand: Counter[str],
    remaining: Counter[str],
    active: str,
    required_evolution_basics: tuple[str, ...],
) -> tuple[bool, str | None]:
    """Check natural resources first, then an exact-discard G&H route."""
    if (
        hand["Technical Machine: Evolution"] > 0
        and hand["Jet Energy"] > 0
        and _basic_possible_with_artazon_state(
            hand,
            remaining,
            active,
            required_evolution_basics,
            artazon_available=hand["Artazon"] > 0,
        )
    ):
        return True, "natural"

    work_hand = hand.copy()
    work_deck = remaining.copy()
    if work_hand["Guzma & Hala"] > 0:
        pass
    elif (
        work_hand["Tag Call"] > 0
        and work_deck["Guzma & Hala"] > 0
    ):
        work_hand["Tag Call"] -= 1
        if work_hand["Tag Call"] == 0:
            del work_hand["Tag Call"]
        work_deck["Guzma & Hala"] -= 1
        work_hand["Guzma & Hala"] += 1
    else:
        return False, None

    work_hand["Guzma & Hala"] -= 1
    if work_hand["Guzma & Hala"] == 0:
        del work_hand["Guzma & Hala"]

    physical_cards: list[str] = []
    for card, copies in work_hand.items():
        physical_cards.extend([card] * copies)

    discard_pairs = {
        tuple(sorted((physical_cards[left], physical_cards[right])))
        for left in range(len(physical_cards))
        for right in range(left + 1, len(physical_cards))
    }

    for first, second in discard_pairs:
        candidate_hand = work_hand.copy()
        candidate_hand[first] -= 1
        if candidate_hand[first] == 0:
            del candidate_hand[first]
        candidate_hand[second] -= 1
        if candidate_hand[second] == 0:
            del candidate_hand[second]

        candidate_deck = work_deck.copy()
        searchable = True
        for card in ("Technical Machine: Evolution", "Jet Energy"):
            if candidate_hand[card] == 0:
                if candidate_deck[card] == 0:
                    searchable = False
                    break
                candidate_deck[card] -= 1
                candidate_hand[card] += 1

        if not searchable:
            continue

        artazon_available = (
            candidate_hand["Artazon"] > 0
            or candidate_deck["Artazon"] > 0
        )
        if _basic_possible_with_artazon_state(
            candidate_hand,
            candidate_deck,
            active,
            required_evolution_basics,
            artazon_available=artazon_available,
        ):
            return True, "gnh"

    return False, None


ANY_ROUTE_ENDPOINTS: dict[str, tuple[str, ...]] = {
    "core": (),
    "pidgeot": ("Pidgey",),
    "stoutland": ("Lillipup",),
    "dual": ("Pidgey", "Lillipup"),
    "item": ("Oddish",),
    "item_pidgeot": ("Oddish", "Pidgey"),
    "item_stoutland": ("Oddish", "Lillipup"),
}


def _stage_targets_remain(
    remaining: Counter[str],
    endpoint: str,
) -> bool:
    requirements = {
        "core": (),
        "pidgeot": ("Pidgeotto", "Pidgeot ex"),
        "stoutland": ("Herdier", "Stoutland"),
        "dual": ("Pidgeotto", "Pidgeot ex", "Herdier", "Stoutland"),
        "item": ("Gloom", "Vileplume"),
        "item_pidgeot": (
            "Gloom",
            "Vileplume",
            "Pidgeotto",
            "Pidgeot ex",
        ),
        "item_stoutland": (
            "Gloom",
            "Vileplume",
            "Herdier",
            "Stoutland",
        ),
    }
    return all(remaining[card] > 0 for card in requirements[endpoint])


def evaluate_any_route_state(
    hand: Counter[str],
    remaining: Counter[str],
    active: str,
    top_five: tuple[str, ...],
) -> dict[str, bool]:
    """Optimize the relevant Stellar Wish choice for each endpoint."""
    choices: list[str | None] = [None]
    if active == "Jirachi":
        choices.extend(sorted(set(top_five) & RELEVANT_STELLAR))

    success = {endpoint: False for endpoint in ANY_ROUTE_ENDPOINTS}

    for pick in choices:
        candidate_hand = hand.copy()
        candidate_deck = remaining.copy()
        if pick is not None:
            candidate_hand[pick] += 1
            candidate_deck[pick] -= 1

        for endpoint, required in ANY_ROUTE_ENDPOINTS.items():
            if success[endpoint]:
                continue
            if not _stage_targets_remain(candidate_deck, endpoint):
                continue
            possible, _ = _resource_route_possible(
                candidate_hand,
                candidate_deck,
                active,
                required,
            )
            if possible:
                success[endpoint] = True

    return success


def simulate_any_route(
    trials: int,
    *,
    seed: int = 20261007,
) -> SimulationResult:
    """Measure the same endpoints allowing natural and G&H-mediated routes."""
    rng = random.Random(seed)
    successes: Counter[str] = Counter()
    mulligans = 0

    for _ in range(trials):
        hand, remaining, active, top_five, failed = _raw_accepted_state(rng)
        mulligans += failed
        state = evaluate_any_route_state(
            hand,
            remaining,
            active,
            top_five,
        )
        for key, value in state.items():
            if value:
                successes[key] += 1

    return SimulationResult(
        trials=trials,
        successes=dict(successes),
        mean_mulligans=mulligans / trials,
    )

def pct(value: float) -> str:
    return f"{100.0 * value:.3f}%"


def main() -> None:
    trials = 200_000
    greedy, optimal = paired_greedy_optimal(trials)
    print(f"trials={trials}, seed=20261007")
    print(f"exact expected mulligans={exact_expected_mulligans():.6f}")
    print(f"simulated mean mulligans={optimal.mean_mulligans:.6f}")
    print("metric | greedy | endpoint-aware | delta")
    for key in ("gnh_access",) + ENDPOINTS:
        left = greedy.probability(key)
        right = optimal.probability(key)
        print(
            f"{key:22s} | {pct(left):>8s} | "
            f"{pct(right):>14s} | {pct(right-left):>8s}"
        )


if __name__ == "__main__":
    main()
