"""Reproduce the exact K0 discard/reacquisition information-gap result."""

from __future__ import annotations

from math import isclose
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from aichi_vileplume_secret_box import (
    DECK_INDEX,
    DECK_NAMES,
    HAND_INDEX,
    HAND_NAMES,
    _core_possible,
)
from k0_discard_reacquisition_bias import (
    DiscardReacquisitionChoice,
    exhaustive_small_model,
)


def check_close(actual: float, expected: float) -> None:
    if not isclose(actual, expected, rel_tol=0.0, abs_tol=1e-15):
        raise AssertionError(f"{actual} != {expected}")


def counts(names: tuple[str, ...], values: dict[str, int]) -> tuple[int, ...]:
    return tuple(values.get(name, 0) for name in names)


def aichi_hidden_state(
    *,
    tm_replacement_in_deck: bool,
) -> tuple[tuple[int, ...], tuple[int, ...], bool, bool, bool, bool, bool]:
    """Build two K0-equivalent local worlds with opposite replacement prizes."""

    hand = counts(
        HAND_NAMES,
        {
            "secret_box": 1,
            "tm_evolution": 1,
            "artazon": 1,
            "jet_energy": 1,
            "other": 2,
        },
    )
    deck = counts(
        DECK_NAMES,
        {
            "tm_evolution": int(tm_replacement_in_deck),
            "artazon": int(not tm_replacement_in_deck),
            "bunnelby": 1,
        },
    )
    return hand, deck, False, False, False, False, False


def fixed_secret_box_choice(
    state: tuple[tuple[int, ...], tuple[int, ...], bool, bool, bool, bool, bool],
    *,
    discard_payload: str,
) -> bool:
    """Execute the local Box payment with one fixed K0 payload choice."""

    hand, deck, supporter_used, stadium_used, fan_used, bunnelby_in_play, fan_in_play = state
    next_hand = list(hand)
    next_deck = list(deck)

    next_hand[HAND_INDEX["secret_box"]] -= 1
    next_hand[HAND_INDEX["other"]] -= 2
    next_hand[HAND_INDEX[discard_payload]] -= 1
    if min(next_hand) < 0:
        raise AssertionError("invalid fixed Secret Box discard")

    if (
        next_hand[HAND_INDEX["tm_evolution"]] == 0
        and next_deck[DECK_INDEX["tm_evolution"]] > 0
    ):
        next_deck[DECK_INDEX["tm_evolution"]] -= 1
        next_hand[HAND_INDEX["tm_evolution"]] += 1

    if next_deck[DECK_INDEX["artazon"]] > 0:
        next_deck[DECK_INDEX["artazon"]] -= 1
        next_hand[HAND_INDEX["artazon"]] += 1

    return _core_possible(
        (
            tuple(next_hand),
            tuple(next_deck),
            supporter_used,
            stadium_used,
            fan_used,
            bunnelby_in_play,
            fan_in_play,
        )
    )


def main() -> None:
    flagship = DiscardReacquisitionChoice(
        unknown_pool=52,
        prize_count=6,
        candidate_classes=2,
        forced_critical_discards=1,
    )
    check_close(flagship.blind_k0_success, 0.8846153846153846)
    check_close(flagship.informed_k1_success, 0.9886877828054299)
    check_close(flagship.information_gap, 0.10407239819004532)

    forced_both = DiscardReacquisitionChoice(
        unknown_pool=52,
        prize_count=6,
        candidate_classes=2,
        forced_critical_discards=2,
    )
    check_close(forced_both.blind_k0_success, 0.7805429864253394)
    check_close(forced_both.informed_k1_success, forced_both.blind_k0_success)
    check_close(forced_both.information_gap, 0.0)

    three_choose_two = DiscardReacquisitionChoice(
        unknown_pool=52,
        prize_count=6,
        candidate_classes=3,
        forced_critical_discards=2,
    )
    check_close(three_choose_two.blind_k0_success, 0.7805429864253394)
    check_close(three_choose_two.informed_k1_success, 0.9678733031674208)
    check_close(three_choose_two.information_gap, 0.18733031674208145)

    for params in ((7, 2, 3, 1), (7, 2, 3, 2)):
        model = DiscardReacquisitionChoice(
            unknown_pool=params[0],
            prize_count=params[1],
            candidate_classes=params[2],
            forced_critical_discards=params[3],
        )
        exhaustive_blind, exhaustive_informed = exhaustive_small_model(*params)
        check_close(exhaustive_blind, model.blind_k0_success)
        check_close(exhaustive_informed, model.informed_k1_success)

    tm_live = aichi_hidden_state(tm_replacement_in_deck=True)
    artazon_live = aichi_hidden_state(tm_replacement_in_deck=False)

    if not _core_possible(tm_live):
        raise AssertionError("oracle Aichi planner should solve TM-live hidden world")
    if not _core_possible(artazon_live):
        raise AssertionError("oracle Aichi planner should solve Artazon-live hidden world")

    if not fixed_secret_box_choice(tm_live, discard_payload="tm_evolution"):
        raise AssertionError("TM-live world should permit discarding TM")
    if fixed_secret_box_choice(tm_live, discard_payload="artazon"):
        raise AssertionError("TM-live world should reject discarding Artazon")

    if fixed_secret_box_choice(artazon_live, discard_payload="tm_evolution"):
        raise AssertionError("Artazon-live world should reject discarding TM")
    if not fixed_secret_box_choice(artazon_live, discard_payload="artazon"):
        raise AssertionError("Artazon-live world should permit discarding Artazon")

    print(f"flagship blind K0 success={flagship.blind_k0_success:.9%}")
    print(
        "flagship informed K1/oracle success="
        f"{flagship.informed_k1_success:.9%}"
    )
    print(
        "flagship hidden-information gap="
        f"{flagship.information_gap * 100:.9f} percentage points"
    )
    print(
        "three-candidate/two-discard gap="
        f"{three_choose_two.information_gap * 100:.9f} percentage points"
    )
    print("Aichi hidden-world discard-choice counterexample passed.")
    print("All K0 discard-reacquisition checks passed.")


if __name__ == "__main__":
    main()
