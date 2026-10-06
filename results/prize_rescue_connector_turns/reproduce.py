"""Reproduce turn-by-turn typed Prize-rescue results and validations."""

from __future__ import annotations

from itertools import combinations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from prize_rescue_connector_turns import rescue_success_by_turns  # noqa: E402


def pct(value: float) -> str:
    return f"{100 * value:.6f}%"


def _apply_actions(
    cards: list[str],
    critical_remaining: int,
    hand: tuple[int, ...],
    deck: tuple[int, ...],
) -> tuple[int, tuple[int, ...], tuple[int, ...]]:
    hand_cards = list(hand)
    deck_cards = list(deck)

    rescue_in_hand = sum(cards[index] == "R" for index in hand_cards)
    preserving = [
        index
        for index in hand_cards
        if cards[index] in {"PS", "PN"}
    ]
    rescue_in_deck = [
        index for index in deck_cards if cards[index] == "R"
    ]

    searches = min(
        len(preserving),
        len(rescue_in_deck),
        max(0, critical_remaining - rescue_in_hand),
    )
    for _ in range(searches):
        connector = preserving.pop()
        hand_cards.remove(connector)
        rescuer = next(
            index for index in deck_cards if cards[index] == "R"
        )
        deck_cards.remove(rescuer)
        hand_cards.append(rescuer)

    rescuer = next(
        (index for index in hand_cards if cards[index] == "R"),
        None,
    )
    if rescuer is not None:
        hand_cards.remove(rescuer)
        critical_remaining -= 1
        return (
            critical_remaining,
            tuple(sorted(hand_cards)),
            tuple(sorted(deck_cards)),
        )

    consuming = next(
        (index for index in hand_cards if cards[index] == "C"),
        None,
    )
    if consuming is not None:
        rescuer = next(
            (index for index in deck_cards if cards[index] == "R"),
            None,
        )
        if rescuer is not None:
            hand_cards.remove(consuming)
            deck_cards.remove(rescuer)
            hand_cards.append(rescuer)

    return (
        critical_remaining,
        tuple(sorted(hand_cards)),
        tuple(sorted(deck_cards)),
    )


def _labeled_future_success(
    cards: list[str],
    turns_remaining: int,
    critical_remaining: int,
    hand: tuple[int, ...],
    deck: tuple[int, ...],
) -> float:
    if critical_remaining == 0:
        return 1.0
    if turns_remaining == 0 or not deck:
        return 0.0

    probability = 0.0
    for drawn in deck:
        next_deck = list(deck)
        next_deck.remove(drawn)
        next_hand = tuple(sorted(hand + (drawn,)))
        next_critical, acted_hand, acted_deck = _apply_actions(
            cards,
            critical_remaining,
            next_hand,
            tuple(sorted(next_deck)),
        )
        probability += _labeled_future_success(
            cards,
            turns_remaining - 1,
            next_critical,
            acted_hand,
            acted_deck,
        )

    return probability / len(deck)


def exhaustive_conditional_success(
    deck_size: int,
    prize_count: int,
    *,
    starter_cards: int,
    critical_starter: int,
    critical_nonstarter: int,
    rescue_supporters: int,
    preserving_starter_connectors: int,
    preserving_nonstarter_connectors: int,
    consuming_connectors: int,
    opening_hand_size: int,
    rescue_turns: int,
) -> tuple[float, float]:
    filler_starter = (
        starter_cards - critical_starter - preserving_starter_connectors
    )
    nonstarter_specials = (
        critical_nonstarter
        + rescue_supporters
        + preserving_nonstarter_connectors
        + consuming_connectors
    )
    filler_nonstarter = deck_size - starter_cards - nonstarter_specials

    cards: list[str] = []
    cards += ["CS"] * critical_starter
    cards += ["CN"] * critical_nonstarter
    cards += ["R"] * rescue_supporters
    cards += ["PS"] * preserving_starter_connectors
    cards += ["PN"] * preserving_nonstarter_connectors
    cards += ["C"] * consuming_connectors
    cards += ["FS"] * filler_starter
    cards += ["FN"] * filler_nonstarter

    all_cards = set(range(deck_size))
    accepted_states = 0
    critical_states = 0
    successful_critical_mass = 0.0

    for hand_tuple in combinations(range(deck_size), opening_hand_size):
        hand = set(hand_tuple)
        if not any(
            cards[index] in {"CS", "PS", "FS"} for index in hand
        ):
            continue

        after_hand = all_cards - hand
        for prize_tuple in combinations(sorted(after_hand), prize_count):
            prizes = set(prize_tuple)
            accepted_states += 1
            critical_prized = sum(
                cards[index] in {"CS", "CN"} for index in prizes
            )
            if critical_prized == 0:
                continue

            critical_states += 1
            deck = tuple(sorted(after_hand - prizes))
            successful_critical_mass += _labeled_future_success(
                cards,
                rescue_turns,
                critical_prized,
                tuple(sorted(hand)),
                deck,
            )

    return (
        successful_critical_mass / critical_states,
        critical_states / accepted_states,
    )


def validate() -> None:
    kwargs = {
        "starter_cards": 4,
        "critical_starter": 1,
        "critical_nonstarter": 1,
        "rescue_supporters": 2,
        "preserving_starter_connectors": 1,
        "preserving_nonstarter_connectors": 1,
        "consuming_connectors": 1,
        "opening_hand_size": 3,
        "rescue_turns": 2,
    }
    exact = rescue_success_by_turns(10, 2, **kwargs)
    brute_success, brute_any = exhaustive_conditional_success(
        10, 2, **kwargs
    )

    if abs(exact.conditional_success_probability - brute_success) > 1e-15:
        raise AssertionError(
            (exact.conditional_success_probability, brute_success)
        )
    if abs(exact.any_critical_prized - brute_any) > 1e-15:
        raise AssertionError((exact.any_critical_prized, brute_any))
    if abs(exact.state_mass - 1.0) > 1e-14:
        raise AssertionError(exact.state_mass)

    no_connector = rescue_success_by_turns(
        60,
        6,
        starter_cards=12,
        critical_starter=0,
        critical_nonstarter=4,
        rescue_supporters=2,
        rescue_turns=1,
    )
    consuming_only = rescue_success_by_turns(
        60,
        6,
        starter_cards=12,
        critical_starter=0,
        critical_nonstarter=4,
        rescue_supporters=2,
        consuming_connectors=4,
        rescue_turns=1,
    )
    if abs(
        no_connector.conditional_success_probability
        - consuming_only.conditional_success_probability
    ) > 1e-15:
        raise AssertionError(
            (
                no_connector.conditional_success_probability,
                consuming_only.conditional_success_probability,
            )
        )


def main() -> None:
    validate()

    configurations = [
        ("none", 0, 0),
        ("2 preserving", 2, 0),
        ("2 consuming", 0, 2),
        ("4 preserving", 4, 0),
        ("4 consuming", 0, 4),
        ("2 preserving + 2 consuming", 2, 2),
    ]

    print(
        "Conditional probability of rescuing every initially Prized critical"
    )
    print(
        "60 cards, 6 Prizes, 7-card valid opener, 12 starters, "
        "4 non-starter criticals, 2 rescue Supporters"
    )
    print(
        "connector package                 | turn 1     | turn 2     | "
        "turn 3     | turn 4"
    )
    for name, preserving, consuming in configurations:
        values = []
        for turns in [1, 2, 3, 4]:
            result = rescue_success_by_turns(
                60,
                6,
                starter_cards=12,
                critical_starter=0,
                critical_nonstarter=4,
                rescue_supporters=2,
                preserving_nonstarter_connectors=preserving,
                consuming_connectors=consuming,
                rescue_turns=turns,
            )
            values.append(pct(result.conditional_success_probability))

        print(
            f"{name:33} | {values[0]:>10} | {values[1]:>10} | "
            f"{values[2]:>10} | {values[3]:>10}"
        )

    baseline = rescue_success_by_turns(
        60,
        6,
        starter_cards=12,
        critical_starter=0,
        critical_nonstarter=4,
        rescue_supporters=2,
        rescue_turns=1,
    )
    print(
        f"\nP(any critical initially Prized | valid start) = "
        f"{pct(baseline.any_critical_prized)}"
    )


if __name__ == "__main__":
    main()
