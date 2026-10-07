"""Exact card-name families for the initial Secret Box payment.

This refines the Aichi Vileplume Secret Box first-turn model without changing
its endpoint or downstream compressed continuation semantics.

For each paired Secret-Box-only success, the pre-Box portion is replayed with
exact card names. Every distinct three-card name multiset that can pay Secret
Box and still reach the published compressed core endpoint is retained.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
from itertools import combinations, product
import random

from aichi_discard_family_robustness import minimum_name_protection_cut
from aichi_secret_box_initial_opaque_frontier import _resolve_box_outputs
from aichi_vileplume_als import DECK_COUNTS
from aichi_vileplume_secret_box import (
    BASE_DECK,
    SECRET_BOX_DECK,
    STELLAR_TRAINERS,
    _compress_deck,
    _compress_hand,
    _core_possible,
    _raw_state,
    _state_succeeds,
)


TOOL_OTHER_NAMES = ("Counter Gain", "Stealthy Hood")
SPECIAL_ENERGY_OTHER_NAMES = ("Capture Energy", "Memory Energy")

SECRET_VARIANT_COUNTS = dict(DECK_COUNTS)
SECRET_VARIANT_COUNTS.pop("Grand Tree")
SECRET_VARIANT_COUNTS["Secret Box"] = 1

SINGLETONS = frozenset(
    name
    for name, copies in SECRET_VARIANT_COUNTS.items()
    if copies == 1
)

Payment = tuple[str, str, str]
CounterKey = tuple[tuple[str, int], ...]


@dataclass(frozen=True)
class PaymentFamilyResult:
    trials: int
    incremental_successes: int
    missing_families: int
    family_size_total: int
    family_size_min: int
    family_size_max: int
    family_size_histogram: tuple[tuple[int, int], ...]
    singleton_floor_histogram: tuple[tuple[int, int], ...]
    singleton_free_states: int
    any_forced_singleton_states: int
    forced_singleton_counts: tuple[tuple[str, int], ...]
    protection_cut_histogram: tuple[tuple[int, int], ...]


def _key(counter: Counter[str]) -> CounterKey:
    return tuple(sorted(
        (name, count)
        for name, count in counter.items()
        if count > 0
    ))


def _counter(key: CounterKey) -> Counter[str]:
    return Counter(dict(key))


def _remove_one(counter: Counter[str], name: str) -> Counter[str]:
    changed = counter.copy()
    changed[name] -= 1
    if changed[name] == 0:
        del changed[name]
    return changed


def _add_one(counter: Counter[str], name: str) -> Counter[str]:
    changed = counter.copy()
    changed[name] += 1
    return changed


def _discard_multisets(
    hand: Counter[str],
    count: int,
) -> tuple[tuple[str, ...], ...]:
    physical: list[str] = []
    for name, copies in hand.items():
        physical.extend([name] * copies)
    return tuple(sorted({
        tuple(sorted(physical[index] for index in chosen))
        for chosen in combinations(range(len(physical)), count)
    }))


def _apply_discard(
    hand: Counter[str],
    payment: tuple[str, ...],
) -> Counter[str]:
    changed = hand.copy()
    for name in payment:
        changed[name] -= 1
        if changed[name] == 0:
            del changed[name]
    return changed


def _available_names(
    deck: Counter[str],
    names: tuple[str, ...],
) -> tuple[str, ...]:
    return tuple(name for name in names if deck[name] > 0)


def _search_one(
    hand: Counter[str],
    deck: Counter[str],
    name: str | None,
) -> tuple[Counter[str], Counter[str]]:
    if name is None:
        return hand, deck
    next_hand = _add_one(hand, name)
    next_deck = _remove_one(deck, name)
    return next_hand, next_deck


def _gnh_tool_choices(
    hand: Counter[str],
    deck: Counter[str],
) -> tuple[str | None, ...]:
    if hand["Technical Machine: Evolution"] == 0 and deck["Technical Machine: Evolution"] > 0:
        return ("Technical Machine: Evolution",)
    others = _available_names(deck, TOOL_OTHER_NAMES)
    if others:
        return others
    if deck["Technical Machine: Evolution"] > 0:
        return ("Technical Machine: Evolution",)
    return (None,)


def _gnh_energy_choices(
    hand: Counter[str],
    deck: Counter[str],
) -> tuple[str | None, ...]:
    if hand["Jet Energy"] == 0 and deck["Jet Energy"] > 0:
        return ("Jet Energy",)
    others = _available_names(deck, SPECIAL_ENERGY_OTHER_NAMES)
    if others:
        return others
    if deck["Jet Energy"] > 0:
        return ("Jet Energy",)
    return (None,)


@lru_cache(maxsize=None)
def _families_before_box(
    hand_key: CounterKey,
    deck_key: CounterKey,
    supporter_used: bool,
    stadium_used: bool,
    fan_used: bool,
    bunnelby_in_play: bool,
    fan_rotom_in_play: bool,
) -> frozenset[Payment]:
    hand = _counter(hand_key)
    deck = _counter(deck_key)

    if (
        bunnelby_in_play
        and hand["Technical Machine: Evolution"] > 0
        and hand["Jet Energy"] > 0
    ):
        return frozenset()

    feasible: set[Payment] = set()

    if hand["Secret Box"] > 0:
        base_hand = _remove_one(hand, "Secret Box")
        for payment in _discard_multisets(base_hand, 3):
            after_discard = _apply_discard(base_hand, payment)
            compressed_hand = _compress_hand(after_discard.elements())
            compressed_deck = _compress_deck(deck.elements())
            zero = (0,) * len(compressed_hand)
            next_hand, next_deck = _resolve_box_outputs(
                compressed_hand,
                compressed_deck,
                zero,
            )
            if _core_possible(
                (
                    next_hand,
                    next_deck,
                    supporter_used,
                    stadium_used,
                    fan_used,
                    bunnelby_in_play,
                    fan_rotom_in_play,
                )
            ):
                feasible.add(payment)

    if not bunnelby_in_play and hand["Bunnelby"] > 0:
        next_hand = _remove_one(hand, "Bunnelby")
        feasible.update(
            _families_before_box(
                _key(next_hand),
                deck_key,
                supporter_used,
                stadium_used,
                fan_used,
                True,
                fan_rotom_in_play,
            )
        )

    if not fan_rotom_in_play and hand["Fan Rotom"] > 0:
        next_hand = _remove_one(hand, "Fan Rotom")
        feasible.update(
            _families_before_box(
                _key(next_hand),
                deck_key,
                supporter_used,
                stadium_used,
                fan_used,
                bunnelby_in_play,
                True,
            )
        )

    if (
        fan_rotom_in_play
        and not fan_used
        and not bunnelby_in_play
        and deck["Bunnelby"] > 0
    ):
        next_hand = _add_one(hand, "Bunnelby")
        next_deck = _remove_one(deck, "Bunnelby")
        feasible.update(
            _families_before_box(
                _key(next_hand),
                _key(next_deck),
                supporter_used,
                stadium_used,
                True,
                bunnelby_in_play,
                fan_rotom_in_play,
            )
        )

    if (
        not stadium_used
        and hand["Artazon"] > 0
        and not bunnelby_in_play
        and hand["Bunnelby"] == 0
        and deck["Bunnelby"] > 0
    ):
        next_hand = _remove_one(hand, "Artazon")
        next_deck = _remove_one(deck, "Bunnelby")
        feasible.update(
            _families_before_box(
                _key(next_hand),
                _key(next_deck),
                supporter_used,
                True,
                fan_used,
                True,
                fan_rotom_in_play,
            )
        )

    if hand["Tag Call"] > 0 and deck["Guzma & Hala"] + deck["Bellelba & Brycen-Man"] > 0:
        next_hand = _remove_one(hand, "Tag Call")
        next_deck = deck.copy()
        slots = 2

        if next_hand["Guzma & Hala"] == 0 and next_deck["Guzma & Hala"] > 0:
            next_hand = _add_one(next_hand, "Guzma & Hala")
            next_deck = _remove_one(next_deck, "Guzma & Hala")
            slots -= 1

        if slots and next_deck["Bellelba & Brycen-Man"] > 0:
            next_hand = _add_one(next_hand, "Bellelba & Brycen-Man")
            next_deck = _remove_one(next_deck, "Bellelba & Brycen-Man")
            slots -= 1

        while slots and next_deck["Guzma & Hala"] > 0:
            next_hand = _add_one(next_hand, "Guzma & Hala")
            next_deck = _remove_one(next_deck, "Guzma & Hala")
            slots -= 1

        feasible.update(
            _families_before_box(
                _key(next_hand),
                _key(next_deck),
                supporter_used,
                stadium_used,
                fan_used,
                bunnelby_in_play,
                fan_rotom_in_play,
            )
        )

    if hand["Guzma & Hala"] > 0 and not supporter_used:
        base_hand = _remove_one(hand, "Guzma & Hala")

        free_hand = base_hand.copy()
        free_deck = deck.copy()
        if free_deck["Artazon"] > 0:
            free_hand, free_deck = _search_one(
                free_hand,
                free_deck,
                "Artazon",
            )
        feasible.update(
            _families_before_box(
                _key(free_hand),
                _key(free_deck),
                True,
                stadium_used,
                fan_used,
                bunnelby_in_play,
                fan_rotom_in_play,
            )
        )

        if (
            (
                base_hand["Technical Machine: Evolution"] == 0
                or base_hand["Jet Energy"] == 0
            )
            and sum(base_hand.values()) >= 2
        ):
            for payment in _discard_multisets(base_hand, 2):
                paid_hand = _apply_discard(base_hand, payment)
                paid_deck = deck.copy()

                if paid_deck["Artazon"] > 0:
                    paid_hand, paid_deck = _search_one(
                        paid_hand,
                        paid_deck,
                        "Artazon",
                    )

                for tool_name, energy_name in product(
                    _gnh_tool_choices(paid_hand, paid_deck),
                    _gnh_energy_choices(paid_hand, paid_deck),
                ):
                    branch_hand = paid_hand.copy()
                    branch_deck = paid_deck.copy()

                    if tool_name is not None:
                        branch_hand, branch_deck = _search_one(
                            branch_hand,
                            branch_deck,
                            tool_name,
                        )
                    if energy_name is not None:
                        branch_hand, branch_deck = _search_one(
                            branch_hand,
                            branch_deck,
                            energy_name,
                        )

                    feasible.update(
                        _families_before_box(
                            _key(branch_hand),
                            _key(branch_deck),
                            True,
                            stadium_used,
                            fan_used,
                            bunnelby_in_play,
                            fan_rotom_in_play,
                        )
                    )

    return frozenset(feasible)


def state_payment_family(raw_state) -> frozenset[Payment]:
    hand, remaining, active, top_five = raw_state
    picks: list[str | None] = [None]
    if active == "Jirachi":
        picks.extend(sorted(set(top_five) & STELLAR_TRAINERS))

    family: set[Payment] = set()
    for pick in picks:
        candidate_hand = hand.copy()
        candidate_deck = remaining.copy()
        if pick is not None:
            candidate_hand[pick] += 1
            candidate_deck[pick] -= 1
            if candidate_deck[pick] == 0:
                del candidate_deck[pick]

        _families_before_box.cache_clear()
        family.update(
            _families_before_box(
                _key(candidate_hand),
                _key(candidate_deck),
                False,
                False,
                False,
                active == "Bunnelby",
                active == "Fan Rotom",
            )
        )

    return frozenset(family)


def _singleton_floor(family: frozenset[Payment]) -> int:
    return min(
        sum(name in SINGLETONS for name in payment)
        for payment in family
    )


def _forced_singletons(family: frozenset[Payment]) -> frozenset[str]:
    names = set.intersection(*(set(payment) for payment in family))
    return frozenset(name for name in names if name in SINGLETONS)


def analyze_payment_families(
    trials: int,
    *,
    seed: int = 20261007,
) -> PaymentFamilyResult:
    rng = random.Random(seed)
    incremental = 0
    missing = 0
    family_total = 0
    family_min: int | None = None
    family_max = 0
    family_hist: Counter[int] = Counter()
    singleton_hist: Counter[int] = Counter()
    singleton_free = 0
    any_forced_singleton = 0
    forced_names: Counter[str] = Counter()
    cut_hist: Counter[int] = Counter()

    for _ in range(trials):
        while True:
            order = rng.sample(range(60), 60)
            baseline_state = _raw_state(BASE_DECK, order)
            if baseline_state is not None:
                break

        secret_state = _raw_state(SECRET_BOX_DECK, order)
        if secret_state is None:
            raise AssertionError("ACE SPEC substitution changed setup acceptance")

        if not _state_succeeds(secret_state) or _state_succeeds(baseline_state):
            continue

        incremental += 1
        family = state_payment_family(secret_state)
        if not family:
            missing += 1
            continue

        size = len(family)
        family_total += size
        family_min = size if family_min is None else min(family_min, size)
        family_max = max(family_max, size)
        family_hist[size] += 1

        floor = _singleton_floor(family)
        singleton_hist[floor] += 1
        singleton_free += int(floor == 0)

        forced = _forced_singletons(family)
        any_forced_singleton += int(bool(forced))
        forced_names.update(forced)

        cut = minimum_name_protection_cut(family)
        cut_hist[cut] += 1

    return PaymentFamilyResult(
        trials=trials,
        incremental_successes=incremental,
        missing_families=missing,
        family_size_total=family_total,
        family_size_min=family_min or 0,
        family_size_max=family_max,
        family_size_histogram=tuple(sorted(family_hist.items())),
        singleton_floor_histogram=tuple(sorted(singleton_hist.items())),
        singleton_free_states=singleton_free,
        any_forced_singleton_states=any_forced_singleton,
        forced_singleton_counts=tuple(
            sorted(forced_names.items(), key=lambda item: (-item[1], item[0]))
        ),
        protection_cut_histogram=tuple(sorted(cut_hist.items())),
    )


def main() -> None:
    result = analyze_payment_families(100_000)
    print(f"trials={result.trials}")
    print(f"incremental_successes={result.incremental_successes}")
    print(f"missing_families={result.missing_families}")
    print(f"family_size_total={result.family_size_total}")
    print(f"family_size_min={result.family_size_min}")
    print(f"family_size_max={result.family_size_max}")
    print(f"family_size_histogram={dict(result.family_size_histogram)}")
    print(f"singleton_floor_histogram={dict(result.singleton_floor_histogram)}")
    print(f"singleton_free_states={result.singleton_free_states}")
    print(f"any_forced_singleton_states={result.any_forced_singleton_states}")
    print(f"forced_singleton_counts={dict(result.forced_singleton_counts)}")
    print(f"protection_cut_histogram={dict(result.protection_cut_histogram)}")


if __name__ == "__main__":
    main()
