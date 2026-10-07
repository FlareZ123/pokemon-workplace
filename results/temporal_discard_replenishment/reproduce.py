from __future__ import annotations
from functools import lru_cache
from itertools import product
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

import aichi_vileplume_secret_box as t

HI = {
    "gnh": t.HAND_INDEX["gnh"],
    "tag_call": t.HAND_INDEX["tag_call"],
    "tm": t.HAND_INDEX["tm_evolution"],
    "artazon": t.HAND_INDEX["artazon"],
    "jet": t.HAND_INDEX["jet_energy"],
    "box": t.HAND_INDEX["secret_box"],
    "bunnelby": t.HAND_INDEX["bunnelby"],
    "fan": t.HAND_INDEX["fan_rotom"],
    "other": t.HAND_INDEX["other"],
}
DI = {
    "gnh": t.DECK_INDEX["gnh"],
    "tag_team_other": t.DECK_INDEX["tag_team_other"],
    "tag_call": t.DECK_INDEX["tag_call"],
    "tm": t.DECK_INDEX["tm_evolution"],
    "tool_other": t.DECK_INDEX["tool_other"],
    "artazon": t.DECK_INDEX["artazon"],
    "jet": t.DECK_INDEX["jet_energy"],
    "special_energy_other": t.DECK_INDEX["special_energy_other"],
    "box": t.DECK_INDEX["secret_box"],
    "bunnelby": t.DECK_INDEX["bunnelby"],
    "supporter_other": t.DECK_INDEX["supporter_other"],
}


def add(hand, index, amount=1):
    changed = list(hand)
    changed[index] += amount
    return tuple(changed)


def sub(hand, index, amount=1):
    changed = list(hand)
    changed[index] -= amount
    return tuple(changed)


def total(pre_box, generated, index):
    return pre_box[index] + generated[index]


def take_one(pre_box, generated, index):
    if generated[index] > 0:
        yield pre_box, sub(generated, index)
    if pre_box[index] > 0:
        yield sub(pre_box, index), generated


def generated_discard_selections(generated, cost):
    bounds = [min(count, cost) for count in generated]
    for selection in product(*(range(bound + 1) for bound in bounds)):
        if sum(selection) == cost:
            yield selection


def apply_selection(hand, selection):
    return tuple(count - spent for count, spent in zip(hand, selection))


@lru_cache(None)
def post_box_generated_only(
    pre_box,
    generated,
    deck,
    supporter_used,
    stadium_used,
    fan_used,
    bunnelby_in_play,
    fan_rotom_in_play,
):
    if (
        bunnelby_in_play
        and total(pre_box, generated, HI["tm"]) > 0
        and total(pre_box, generated, HI["jet"]) > 0
    ):
        return True

    if not bunnelby_in_play and total(pre_box, generated, HI["bunnelby"]) > 0:
        for next_pre, next_generated in take_one(
            pre_box, generated, HI["bunnelby"]
        ):
            if post_box_generated_only(
                next_pre,
                next_generated,
                deck,
                supporter_used,
                stadium_used,
                fan_used,
                True,
                fan_rotom_in_play,
            ):
                return True

    if not fan_rotom_in_play and total(pre_box, generated, HI["fan"]) > 0:
        for next_pre, next_generated in take_one(pre_box, generated, HI["fan"]):
            if post_box_generated_only(
                next_pre,
                next_generated,
                deck,
                supporter_used,
                stadium_used,
                fan_used,
                bunnelby_in_play,
                True,
            ):
                return True

    if (
        fan_rotom_in_play
        and not fan_used
        and not bunnelby_in_play
        and deck[DI["bunnelby"]] > 0
    ):
        if post_box_generated_only(
            pre_box,
            add(generated, HI["bunnelby"]),
            t._dec(deck, DI["bunnelby"]),
            supporter_used,
            stadium_used,
            True,
            bunnelby_in_play,
            fan_rotom_in_play,
        ):
            return True

    if (
        not stadium_used
        and total(pre_box, generated, HI["artazon"]) > 0
        and not bunnelby_in_play
        and total(pre_box, generated, HI["bunnelby"]) == 0
        and deck[DI["bunnelby"]] > 0
    ):
        for next_pre, next_generated in take_one(
            pre_box, generated, HI["artazon"]
        ):
            if post_box_generated_only(
                next_pre,
                next_generated,
                t._dec(deck, DI["bunnelby"]),
                supporter_used,
                True,
                fan_used,
                True,
                fan_rotom_in_play,
            ):
                return True

    if (
        total(pre_box, generated, HI["tag_call"]) > 0
        and deck[DI["gnh"]] + deck[DI["tag_team_other"]] > 0
    ):
        for next_pre, next_generated in take_one(
            pre_box, generated, HI["tag_call"]
        ):
            next_deck = list(deck)
            next_generated = list(next_generated)
            slots = 2

            if (
                total(next_pre, tuple(next_generated), HI["gnh"]) == 0
                and next_deck[DI["gnh"]] > 0
            ):
                next_deck[DI["gnh"]] -= 1
                next_generated[HI["gnh"]] += 1
                slots -= 1

            take = min(slots, next_deck[DI["tag_team_other"]])
            next_deck[DI["tag_team_other"]] -= take
            next_generated[HI["other"]] += take
            slots -= take

            take = min(slots, next_deck[DI["gnh"]])
            next_deck[DI["gnh"]] -= take
            next_generated[HI["gnh"]] += take

            if post_box_generated_only(
                next_pre,
                tuple(next_generated),
                tuple(next_deck),
                supporter_used,
                stadium_used,
                fan_used,
                bunnelby_in_play,
                fan_rotom_in_play,
            ):
                return True

    if total(pre_box, generated, HI["gnh"]) > 0 and not supporter_used:
        for base_pre, base_generated in take_one(pre_box, generated, HI["gnh"]):
            next_deck = list(deck)
            next_generated = list(base_generated)
            if next_deck[DI["artazon"]] > 0:
                next_deck[DI["artazon"]] -= 1
                next_generated[HI["artazon"]] += 1

            if post_box_generated_only(
                base_pre,
                tuple(next_generated),
                tuple(next_deck),
                True,
                stadium_used,
                fan_used,
                bunnelby_in_play,
                fan_rotom_in_play,
            ):
                return True

            if (
                total(base_pre, base_generated, HI["tm"]) == 0
                or total(base_pre, base_generated, HI["jet"]) == 0
            ) and sum(base_generated) >= 2:
                for selection in generated_discard_selections(base_generated, 2):
                    after_discard = apply_selection(base_generated, selection)
                    next_deck = list(deck)
                    next_generated = list(after_discard)

                    if next_deck[DI["artazon"]] > 0:
                        next_deck[DI["artazon"]] -= 1
                        next_generated[HI["artazon"]] += 1

                    if (
                        total(base_pre, tuple(next_generated), HI["tm"]) == 0
                        and next_deck[DI["tm"]] > 0
                    ):
                        next_deck[DI["tm"]] -= 1
                        next_generated[HI["tm"]] += 1
                    elif next_deck[DI["tool_other"]] > 0:
                        next_deck[DI["tool_other"]] -= 1
                        next_generated[HI["other"]] += 1
                    elif next_deck[DI["tm"]] > 0:
                        next_deck[DI["tm"]] -= 1
                        next_generated[HI["tm"]] += 1

                    if (
                        total(base_pre, tuple(next_generated), HI["jet"]) == 0
                        and next_deck[DI["jet"]] > 0
                    ):
                        next_deck[DI["jet"]] -= 1
                        next_generated[HI["jet"]] += 1
                    elif next_deck[DI["special_energy_other"]] > 0:
                        next_deck[DI["special_energy_other"]] -= 1
                        next_generated[HI["other"]] += 1
                    elif next_deck[DI["jet"]] > 0:
                        next_deck[DI["jet"]] -= 1
                        next_generated[HI["jet"]] += 1

                    if post_box_generated_only(
                        base_pre,
                        tuple(next_generated),
                        tuple(next_deck),
                        True,
                        stadium_used,
                        fan_used,
                        bunnelby_in_play,
                        fan_rotom_in_play,
                    ):
                        return True

    return False


def secret_box_self_funded(
    hand,
    deck,
    supporter_used,
    stadium_used,
    fan_used,
    bunnelby_in_play,
    fan_rotom_in_play,
):
    if hand[HI["box"]] <= 0:
        return False

    base_hand = t._dec(hand, HI["box"])
    if sum(base_hand) < 3:
        return False

    for selection in t._discard_selections(base_hand, 3):
        pre_box = tuple(
            count - discarded
            for count, discarded in zip(base_hand, selection)
        )
        generated = [0] * len(pre_box)
        next_deck = list(deck)

        if next_deck[DI["tag_call"]] > 0:
            next_deck[DI["tag_call"]] -= 1
            generated[HI["tag_call"]] += 1

        if total(pre_box, tuple(generated), HI["tm"]) == 0 and next_deck[DI["tm"]] > 0:
            next_deck[DI["tm"]] -= 1
            generated[HI["tm"]] += 1
        elif next_deck[DI["tool_other"]] > 0:
            next_deck[DI["tool_other"]] -= 1
            generated[HI["other"]] += 1
        elif next_deck[DI["tm"]] > 0:
            next_deck[DI["tm"]] -= 1
            generated[HI["tm"]] += 1

        if (
            total(pre_box, tuple(generated), HI["gnh"]) == 0
            and next_deck[DI["gnh"]] > 0
        ):
            next_deck[DI["gnh"]] -= 1
            generated[HI["gnh"]] += 1
        elif next_deck[DI["supporter_other"]] > 0:
            next_deck[DI["supporter_other"]] -= 1
            generated[HI["other"]] += 1
        elif next_deck[DI["tag_team_other"]] > 0:
            next_deck[DI["tag_team_other"]] -= 1
            generated[HI["other"]] += 1
        elif next_deck[DI["gnh"]] > 0:
            next_deck[DI["gnh"]] -= 1
            generated[HI["gnh"]] += 1

        if next_deck[DI["artazon"]] > 0:
            next_deck[DI["artazon"]] -= 1
            generated[HI["artazon"]] += 1

        if post_box_generated_only(
            pre_box,
            tuple(generated),
            tuple(next_deck),
            supporter_used,
            stadium_used,
            fan_used,
            bunnelby_in_play,
            fan_rotom_in_play,
        ):
            return True

    return False


@lru_cache(None)
def pre_box_self_funded(state):
    hand, deck, supporter_used, stadium_used, fan_used, bunnelby_in_play, fan_rotom_in_play = state

    if secret_box_self_funded(
        hand,
        deck,
        supporter_used,
        stadium_used,
        fan_used,
        bunnelby_in_play,
        fan_rotom_in_play,
    ):
        return True

    if not bunnelby_in_play and hand[HI["bunnelby"]] > 0:
        if pre_box_self_funded(
            (
                t._dec(hand, HI["bunnelby"]),
                deck,
                supporter_used,
                stadium_used,
                fan_used,
                True,
                fan_rotom_in_play,
            )
        ):
            return True

    if not fan_rotom_in_play and hand[HI["fan"]] > 0:
        if pre_box_self_funded(
            (
                t._dec(hand, HI["fan"]),
                deck,
                supporter_used,
                stadium_used,
                fan_used,
                bunnelby_in_play,
                True,
            )
        ):
            return True

    if (
        fan_rotom_in_play
        and not fan_used
        and not bunnelby_in_play
        and deck[DI["bunnelby"]] > 0
    ):
        if pre_box_self_funded(
            (
                t._inc(hand, HI["bunnelby"]),
                t._dec(deck, DI["bunnelby"]),
                supporter_used,
                stadium_used,
                True,
                bunnelby_in_play,
                fan_rotom_in_play,
            )
        ):
            return True

    if (
        not stadium_used
        and hand[HI["artazon"]] > 0
        and not bunnelby_in_play
        and hand[HI["bunnelby"]] == 0
        and deck[DI["bunnelby"]] > 0
    ):
        if pre_box_self_funded(
            (
                t._dec(hand, HI["artazon"]),
                t._dec(deck, DI["bunnelby"]),
                supporter_used,
                True,
                fan_used,
                True,
                fan_rotom_in_play,
            )
        ):
            return True

    if hand[HI["tag_call"]] > 0 and deck[DI["gnh"]] + deck[DI["tag_team_other"]] > 0:
        next_hand = list(t._dec(hand, HI["tag_call"]))
        next_deck = list(deck)
        slots = 2

        if next_hand[HI["gnh"]] == 0 and next_deck[DI["gnh"]] > 0:
            next_deck[DI["gnh"]] -= 1
            next_hand[HI["gnh"]] += 1
            slots -= 1

        take = min(slots, next_deck[DI["tag_team_other"]])
        next_deck[DI["tag_team_other"]] -= take
        next_hand[HI["other"]] += take
        slots -= take

        take = min(slots, next_deck[DI["gnh"]])
        next_deck[DI["gnh"]] -= take
        next_hand[HI["gnh"]] += take

        if pre_box_self_funded(
            (
                tuple(next_hand),
                tuple(next_deck),
                supporter_used,
                stadium_used,
                fan_used,
                bunnelby_in_play,
                fan_rotom_in_play,
            )
        ):
            return True

    return False


def state_self_funded(raw_state):
    hand, remaining, active, top_five = raw_state
    picks = [None]
    if active == "Jirachi":
        picks.extend(sorted(set(top_five) & t.STELLAR_TRAINERS))

    for pick in picks:
        candidate_hand = hand.copy()
        candidate_deck = remaining.copy()
        if pick is not None:
            candidate_hand[pick] += 1
            candidate_deck[pick] -= 1
            if candidate_deck[pick] == 0:
                del candidate_deck[pick]

        state = (
            t._compress_hand(candidate_hand.elements()),
            t._compress_deck(candidate_deck.elements()),
            False,
            False,
            False,
            active == "Bunnelby",
            active == "Fan Rotom",
        )
        if pre_box_self_funded(state):
            return True

    return False


def initial_discard_stock(first_cost, second_cost, generated_fodder):
    return first_cost + max(0, second_cost - generated_fodder)


def reproduce(trials=100_000, seed=20261007):
    rng = random.Random(seed)
    counts = {
        "baseline": 0,
        "secret": 0,
        "incremental": 0,
        "self_funded": 0,
        "missing_jet": 0,
        "self_funded_missing_jet": 0,
    }

    for _ in range(trials):
        while True:
            order = rng.sample(range(60), 60)
            baseline_state = t._raw_state(t.BASE_DECK, order)
            if baseline_state is not None:
                break

        secret_state = t._raw_state(t.SECRET_BOX_DECK, order)
        if secret_state is None:
            raise AssertionError("ACE SPEC substitution changed setup acceptance")

        baseline_ok = t._state_succeeds(baseline_state)
        secret_ok = t._state_succeeds(secret_state)
        counts["baseline"] += int(baseline_ok)
        counts["secret"] += int(secret_ok)

        if secret_ok and not baseline_ok:
            counts["incremental"] += 1
            self_funded = state_self_funded(secret_state)
            counts["self_funded"] += int(self_funded)
            hand, _deck, _active, _top_five = secret_state
            if hand["Jet Energy"] == 0:
                counts["missing_jet"] += 1
                counts["self_funded_missing_jet"] += int(self_funded)

    return counts


def main():
    assert initial_discard_stock(3, 2, 0) == 5
    assert initial_discard_stock(3, 2, 1) == 4
    assert initial_discard_stock(3, 2, 2) == 3

    counts = reproduce()
    expected = {
        "baseline": 70_709,
        "secret": 74_884,
        "incremental": 4_175,
        "self_funded": 4_175,
        "missing_jet": 3_197,
        "self_funded_missing_jet": 3_197,
    }
    if counts != expected:
        raise AssertionError((counts, expected))

    avg_throughput = (
        3 * (counts["incremental"] - counts["missing_jet"])
        + 5 * counts["missing_jet"]
    ) / counts["incremental"]
    print(counts)
    print(f"baseline={counts['baseline'] / 100_000:.6%}")
    print(f"secret_box={counts['secret'] / 100_000:.6%}")
    print(f"incremental={counts['incremental'] / 100_000:.6%}")
    print(f"missing_jet_share={counts['missing_jet'] / counts['incremental']:.6%}")
    print(f"mean_discard_throughput={avg_throughput:.6f}")
    print("All temporal discard replenishment checks passed.")


if __name__ == "__main__":
    main()
