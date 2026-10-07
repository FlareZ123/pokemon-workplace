"""Exact optional-starter policy case study for 2018 Gardevoir/Talonflame."""

from __future__ import annotations

from math import comb
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.build_expanded_legality_baseline import load_json  # noqa: E402
from tools.setup_eligibility import _effective_status  # noqa: E402
from tools.setup_hand_value_policy import (  # noqa: E402
    SetupHandState,
    opening_acceptance_hand_policy,
    opening_hand_distribution,
    specific_class_card_prize_probability,
)

DECK = {
    "Talonflame": 4,
    "Ralts": 4,
    "Kirlia": 2,
    "Gardevoir-GX": 3,
    "Gallade": 2,
    "Tapu Lele-GX": 2,
    "Alolan Vulpix": 1,
    "Mew-EX": 1,
    "Giratina": 1,
    "Professor Sycamore": 4,
    "Guzma": 3,
    "N": 2,
    "Cynthia": 2,
    "Brigette": 2,
    "Skyla": 1,
    "Ultra Ball": 4,
    "Rare Candy": 4,
    "Field Blower": 2,
    "Super Rod": 1,
    "Enhanced Hammer": 1,
    "Choice Band": 2,
    "Parallel City": 1,
    "Fairy Energy": 7,
    "Double Colorless Energy": 4,
}

FORCED_BASICS = 9
OPTIONAL_TALONFLAME = 4
BRIGETTE = 2
ULTRA_BALL = 4
SKYLA = 1
ENERGY = 11
OTHER = 29
FEATURE_GROUPS = (BRIGETTE, ULTRA_BALL, SKYLA, ENERGY)


def has_brigette(state: SetupHandState) -> bool:
    return state.feature_counts[0] > 0


def has_ultra_ball(state: SetupHandState) -> bool:
    return state.feature_counts[1] > 0


def has_skyla(state: SetupHandState) -> bool:
    return state.feature_counts[2] > 0


def direct_search(state: SetupHandState) -> bool:
    return has_brigette(state) or has_ultra_ball(state)


def connector_search(state: SetupHandState) -> bool:
    return direct_search(state) or has_skyla(state)


def aero_ready(state: SetupHandState) -> bool:
    return state.feature_counts[3] > 0


def policy_decline(state: SetupHandState) -> float:
    return 0.0


def policy_direct_search(state: SetupHandState) -> float:
    return float(direct_search(state))


def policy_connector_search(state: SetupHandState) -> float:
    return float(connector_search(state))


def policy_connector_or_aero(state: SetupHandState) -> float:
    return float(connector_search(state) or aero_ready(state))


def policy_accept_all(state: SetupHandState) -> float:
    return 1.0


def validate_deck_and_card_pool() -> None:
    assert sum(DECK.values()) == 60
    assert (
        FORCED_BASICS
        + OPTIONAL_TALONFLAME
        + BRIGETTE
        + ULTRA_BALL
        + SKYLA
        + ENERGY
        + OTHER
        == 60
    )

    sets = load_json(ROOT / "resources" / "sets" / "en.json")
    expanded_sets = {
        row["id"]
        for row in sets
        if (row.get("legalities") or {}).get("expanded") == "Legal"
    }
    named_status: dict[str, bool] = {name: False for name in DECK}
    card_by_id = {}

    for path in sorted((ROOT / "resources" / "cards" / "en").glob("*.json")):
        if path.stem not in expanded_sets:
            continue
        for card in load_json(path):
            card_by_id[card["id"]] = card
            name = card["name"]
            if name in named_status and _effective_status(card) == "Legal":
                named_status[name] = True

    missing = [name for name, legal in named_status.items() if not legal]
    if missing:
        raise AssertionError(("no effectively legal Expanded printing", missing))

    talonflame = card_by_id["xy11-96"]
    assert _effective_status(talonflame) == "Legal"
    assert "Stage 2" in talonflame["subtypes"]
    gale_wings = next(
        ability
        for ability in talonflame["abilities"]
        if ability["name"] == "Gale Wings"
    )
    assert "setting up to play" in gale_wings["text"]
    aero_blitz = next(
        attack
        for attack in talonflame["attacks"]
        if attack["name"] == "Aero Blitz"
    )
    assert aero_blitz["cost"] == ["Colorless"]
    assert "up to 2 cards" in aero_blitz["text"]

    brigette = card_by_id["xy8-134"]
    assert _effective_status(brigette) == "Legal"
    assert "Supporter" in brigette["subtypes"]
    assert "3 Basic Pokémon" in brigette["rules"][0]

    ultra_ball = card_by_id["sm1-135"]
    assert _effective_status(ultra_ball) == "Legal"
    assert "Item" in ultra_ball["subtypes"]
    assert "Discard 2 cards" in ultra_ball["rules"][0]
    assert "search your deck for a Pokémon" in ultra_ball["rules"][0]

    skyla = card_by_id["xy8-148"]
    assert _effective_status(skyla) == "Legal"
    assert "Supporter" in skyla["subtypes"]
    assert "Trainer card" in skyla["rules"][0]


def policy_metrics(policy) -> tuple[float, float]:
    acceptance = opening_acceptance_hand_policy(
        60,
        FORCED_BASICS,
        (OPTIONAL_TALONFLAME,),
        FEATURE_GROUPS,
        policy,
    )
    return acceptance, (1.0 - acceptance) / acceptance


def prize_rates(policy) -> tuple[float, ...]:
    return tuple(
        specific_class_card_prize_probability(
            60,
            6,
            forced_starters=FORCED_BASICS,
            optional_group_sizes=(OPTIONAL_TALONFLAME,),
            feature_group_sizes=FEATURE_GROUPS,
            optional_policy=policy,
            class_index=index,
        )
        for index in range(7)
    )


def main() -> None:
    validate_deck_and_card_pool()

    distribution = opening_hand_distribution(
        60,
        FORCED_BASICS,
        (OPTIONAL_TALONFLAME,),
        FEATURE_GROUPS,
    )
    optional_only = [
        (state, mass)
        for state, mass in distribution
        if state.forced_in_hand == 0 and sum(state.optional_counts) > 0
    ]
    optional_mass = sum(mass for _, mass in optional_only)

    def conditional(predicate) -> float:
        return (
            sum(mass for state, mass in optional_only if predicate(state))
            / optional_mass
        )

    print("optional-only mass", optional_mass)
    print("conditional Brigette", conditional(has_brigette))
    print("conditional Ultra Ball", conditional(has_ultra_ball))
    print("conditional Skyla", conditional(has_skyla))
    print("conditional Brigette-only", conditional(
        lambda state: has_brigette(state) and not has_ultra_ball(state)
    ))
    print("conditional Ultra-Ball-only", conditional(
        lambda state: has_ultra_ball(state) and not has_brigette(state)
    ))
    print("conditional both direct channels", conditional(
        lambda state: has_brigette(state) and has_ultra_ball(state)
    ))
    print("conditional direct-search", conditional(direct_search))
    print("conditional connector-search", conditional(connector_search))
    print("conditional aero-ready", conditional(aero_ready))
    print(
        "conditional connector-or-aero",
        conditional(lambda state: connector_search(state) or aero_ready(state)),
    )
    print(
        "conditional neither",
        conditional(
            lambda state: not connector_search(state) and not aero_ready(state)
        ),
    )

    policies = (
        ("decline", policy_decline),
        ("direct-search", policy_direct_search),
        ("connector-search", policy_connector_search),
        ("connector-or-aero", policy_connector_or_aero),
        ("accept-all", policy_accept_all),
    )
    for name, policy in policies:
        acceptance, mulligans = policy_metrics(policy)
        print(name, "acceptance", acceptance, "mulligans", mulligans)
        print(name, "Prize rates", prize_rates(policy))

    # Optional-only hands contain no Ralts. If Skyla is the only search route,
    # it can fail to find Ultra Ball only when all four Ultra Ball copies are
    # among the six Prize cards. The same count applies to all-four-Ralts
    # Prized after an optional-only hand.
    four_of_four_prized = comb(49, 2) / comb(53, 6)
    print("all 4 Ralts prized after optional-only hand", four_of_four_prized)
    print("all 4 Ultra Ball prized after Skyla-only hand", four_of_four_prized)


if __name__ == "__main__":
    main()
