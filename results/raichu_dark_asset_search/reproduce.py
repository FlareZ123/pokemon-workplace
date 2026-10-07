"""Reproduce and independently validate first-order Dark Asset search value."""

from __future__ import annotations

from itertools import combinations
from math import isclose

from raichu_dark_asset_search import DarkAssetSearchResult, dark_asset_search_snapshot


def pct(value: float) -> str:
    return f"{100 * value:.6f}%"


def _quick_dark_success(deck: set[str], target_prized: bool, draws: int) -> float:
    crobats = sorted(card for card in deck if card.startswith("crobat-"))
    if not crobats:
        return 0.0
    next_deck = set(deck)
    next_deck.remove(crobats[0])
    gladion_in_deck = sum(card.startswith("gladion-") for card in next_deck)
    samples = list(combinations(next_deck, min(draws, len(next_deck))))
    wins = 0
    for sample in samples:
        if target_prized:
            success = any(card.startswith("gladion-") for card in sample) or (
                "forest-seal" in sample and gladion_in_deck > 0
            )
        else:
            success = "target" in sample or "forest-seal" in sample
        wins += success
    return wins / len(samples)


def _ultra_dark_success(deck: set[str], draws: int) -> float:
    crobats = sorted(card for card in deck if card.startswith("crobat-"))
    if not crobats:
        return 0.0
    next_deck = set(deck)
    next_deck.remove(crobats[0])
    gladion_in_deck = sum(card.startswith("gladion-") for card in next_deck)
    samples = list(combinations(next_deck, min(draws, len(next_deck))))
    wins = 0
    for sample in samples:
        success = any(card.startswith("gladion-") for card in sample) or (
            "forest-seal" in sample and gladion_in_deck > 0
        )
        wins += success
    return wins / len(samples)


def labeled_small_case() -> tuple[float, dict[str, float]]:
    cards = (
        "target", "gladion-1", "gladion-2", "ultra", "computer",
        "forest-seal", "crobat-1", "crobat-2", "quick",
        "disposable-1", "disposable-2", "giratina", "starter", "other",
    )
    crobats = {"crobat-1", "crobat-2"}
    starters = crobats | {"giratina", "starter"}
    disposables = {"disposable-1", "disposable-2", "giratina"}
    all_openings = list(combinations(cards, 3))
    accepted = [o for o in all_openings if set(o) & starters]
    valid = len(accepted) / len(all_openings)

    keys = (
        "state_mass", "target_prized_probability",
        "sequenced_forest_seal_access", "dark_asset_access",
        "incremental_dark_asset_access", "incremental_quick_dark_asset_access",
        "incremental_ultra_dark_asset_access",
        "quick_dark_asset_candidate_probability",
        "ultra_dark_asset_candidate_probability",
        "incremental_target_in_deck_access", "incremental_target_prized_access",
        "target_prized_sequenced_access", "target_prized_dark_asset_access",
    )
    out = {key: 0.0 for key in keys}
    ow = 1 / len(accepted)

    for opening_tuple in accepted:
        opening = set(opening_tuple)
        hand_after_setup = set(opening)
        crobat_in_play = False
        opening_crobats = sorted(hand_after_setup & crobats)
        if opening_crobats:
            hand_after_setup.remove(opening_crobats[0])
            crobat_in_play = True
        elif "starter" in hand_after_setup:
            hand_after_setup.remove("starter")
        else:
            hand_after_setup.remove("giratina")

        after_opening = [card for card in cards if card not in opening]
        prize_sets = list(combinations(after_opening, 2))
        pw = 1 / len(prize_sets)
        for prize_tuple in prize_sets:
            prizes = set(prize_tuple)
            after_prizes = [card for card in after_opening if card not in prizes]
            dw = 1 / len(after_prizes)
            for drawn in after_prizes:
                hand = hand_after_setup | {drawn}
                deck = set(after_prizes) - {drawn}
                mass = ow * pw * dw

                target_in_hand = "target" in hand
                target_prized = "target" in prizes
                target_in_deck = "target" in deck
                gladion_in_hand = any(card.startswith("gladion-") for card in hand)
                gladion_in_deck = sum(card.startswith("gladion-") for card in deck)
                ultra_in_hand = "ultra" in hand
                computer_in_hand = "computer" in hand
                fss_in_hand = "forest-seal" in hand
                crobat_available = crobat_in_play or bool(hand & crobats)
                crobat_in_deck = bool(deck & crobats)
                quick_in_hand = "quick" in hand
                disposable_count = len(hand & disposables)
                quick_payable = disposable_count >= 1
                two_payable = disposable_count >= 2

                baseline = target_in_hand or (
                    target_in_deck and two_payable and (ultra_in_hand or computer_in_hand)
                ) or (
                    target_prized and (
                        gladion_in_hand
                        or (two_payable and computer_in_hand and gladion_in_deck > 0)
                    )
                )
                seal_output = target_in_deck or (target_prized and gladion_in_deck > 0)
                direct = baseline or (fss_in_hand and crobat_available and seal_output)
                quick_gate = (
                    fss_in_hand and not crobat_available and crobat_in_deck
                    and quick_in_hand and quick_payable and seal_output
                )
                ultra_gate = (
                    fss_in_hand and not crobat_available and crobat_in_deck
                    and ultra_in_hand and two_payable and target_prized
                    and gladion_in_deck > 0
                )
                sequenced = direct or quick_gate or ultra_gate

                quick_candidate = quick_in_hand and quick_payable and crobat_in_deck
                ultra_candidate = target_prized and ultra_in_hand and two_payable and crobat_in_deck
                qp = _quick_dark_success(deck, target_prized, 5) if quick_candidate else 0.0
                up = _ultra_dark_success(deck, 6) if ultra_candidate and gladion_in_deck > 0 else 0.0

                if sequenced:
                    dark = 1.0
                    qi = ui = 0.0
                elif up >= qp:
                    dark = up
                    qi, ui = 0.0, up
                else:
                    dark = qp
                    qi, ui = qp, 0.0
                inc = dark - float(sequenced)

                vals = {
                    "state_mass": 1.0,
                    "target_prized_probability": target_prized,
                    "sequenced_forest_seal_access": sequenced,
                    "dark_asset_access": dark,
                    "incremental_dark_asset_access": inc,
                    "incremental_quick_dark_asset_access": qi,
                    "incremental_ultra_dark_asset_access": ui,
                    "quick_dark_asset_candidate_probability": quick_candidate,
                    "ultra_dark_asset_candidate_probability": ultra_candidate,
                    "incremental_target_in_deck_access": inc * target_in_deck,
                    "incremental_target_prized_access": inc * target_prized,
                    "target_prized_sequenced_access": target_prized * sequenced,
                    "target_prized_dark_asset_access": target_prized * dark,
                }
                for key, value in vals.items():
                    out[key] += mass * value
    return valid, out


def assert_matches(result: DarkAssetSearchResult, expected: dict[str, float]) -> None:
    for key, value in expected.items():
        actual = getattr(result, key)
        assert isclose(actual, value, rel_tol=0.0, abs_tol=3e-12), (key, actual, value)


def main() -> None:
    r = dark_asset_search_snapshot()
    assert isclose(r.state_mass, 1.0, rel_tol=0.0, abs_tol=3e-11)
    assert isclose(r.sequenced_forest_seal_access, 0.3446660915197917, abs_tol=3e-11)
    assert isclose(r.dark_asset_access, 0.3509250922888452, abs_tol=3e-11)
    assert isclose(r.incremental_dark_asset_access, 0.006259000769052371, abs_tol=3e-11)
    assert isclose(r.incremental_quick_dark_asset_access, 0.0051247941320766875, abs_tol=3e-11)
    assert isclose(r.incremental_ultra_dark_asset_access, 0.001134206636975726, abs_tol=3e-11)
    assert isclose(r.conditional_target_prized_dark_asset_access, 0.3560196118018326, abs_tol=3e-11)

    print("Harto first-order search-to-Crobat Dark Asset access")
    print("sequenced Forest Seal access:", pct(r.sequenced_forest_seal_access))
    print("plus first-order Dark Asset:", pct(r.dark_asset_access))
    print("incremental Dark Asset gain:", pct(r.incremental_dark_asset_access))
    print("Quick Ball Dark Asset contribution:", pct(r.incremental_quick_dark_asset_access))
    print("Ultra Ball Dark Asset contribution:", pct(r.incremental_ultra_dark_asset_access))
    print("Prized-target sequenced access:", pct(r.conditional_target_prized_sequenced_access))
    print("Prized-target with Dark Asset:", pct(r.conditional_target_prized_dark_asset_access))

    exact = dark_asset_search_snapshot(
        deck_size=14, prize_count=2, opening_hand_size=3,
        gladion_copies=2, ultra_ball_copies=1, computer_search_copies=1,
        forest_seal_copies=1, crobat_v_copies=2, quick_ball_copies=1,
        disposable_nonstarter_copies=2, disposable_starter_copies=1,
        other_starter_copies=1, quick_ball_discard_cost=1, two_card_discard_cost=2,
    )
    valid, brute = labeled_small_case()
    assert isclose(exact.valid_opening_probability, valid, abs_tol=1e-12)
    assert_matches(exact, brute)
    print("Independent labeled-card Dark Asset regression: PASS")
    print("small-case Dark Asset access:", pct(exact.dark_asset_access))


if __name__ == "__main__":
    main()
