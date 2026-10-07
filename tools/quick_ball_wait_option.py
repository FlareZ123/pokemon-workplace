"""One-draw option value for Quick Ball between attacker and Tapu Lele-GX."""

from __future__ import annotations


def policy_values(
    deck_cards: int,
    gladion_copies: int,
    *,
    attacker_value: float = 1.0,
    gladion_value: float = 1.0,
) -> dict[str, float]:
    """Return additive utility for eager and one-draw-wait policies.

    State assumptions:
    - one Quick Ball and one acceptable discard are already in hand;
    - one required Basic attacker is in deck;
    - one Tapu Lele-GX-like support Basic is in deck;
    - gladion_copies rescue Supporters are in deck;
    - neither objective is currently complete;
    - after one natural draw, Quick Ball may be allocated adaptively.
    """
    if deck_cards < gladion_copies + 2:
        raise ValueError("deck needs attacker, support Basic, and Gladion copies")
    if gladion_copies < 1:
        raise ValueError("at least one Gladion must remain in deck")
    if attacker_value < 0 or gladion_value < 0:
        raise ValueError("values must be non-negative")

    filler = deck_cards - gladion_copies - 2
    eager_attacker = (
        attacker_value
        + gladion_value * (gladion_copies + 1) / (deck_cards - 1)
    )
    eager_gladion = (
        gladion_value
        + attacker_value / (deck_cards - 2)
    )
    wait_one_draw = (
        (gladion_copies + 2) * (attacker_value + gladion_value)
        + filler * max(attacker_value, gladion_value)
    ) / deck_cards
    return {
        "eager_attacker": eager_attacker,
        "eager_gladion": eager_gladion,
        "wait_one_draw": wait_one_draw,
    }


def outcome_probabilities(
    deck_cards: int,
    gladion_copies: int,
) -> dict[str, float]:
    """Return the corresponding both/one-channel outcome probabilities."""
    if deck_cards < gladion_copies + 2 or gladion_copies < 1:
        raise ValueError("invalid deck state")
    filler = deck_cards - gladion_copies - 2
    return {
        "wait_both": (gladion_copies + 2) / deck_cards,
        "wait_choice": filler / deck_cards,
        "eager_attacker_both": (gladion_copies + 1) / (deck_cards - 1),
        "eager_attacker_only": filler / (deck_cards - 1),
        "eager_gladion_both": 1 / (deck_cards - 2),
        "eager_gladion_only": (deck_cards - 3) / (deck_cards - 2),
    }
