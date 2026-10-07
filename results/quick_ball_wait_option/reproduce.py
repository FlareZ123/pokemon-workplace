from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from quick_ball_wait_option import outcome_probabilities, policy_values


def labeled_values(deck_cards, gladion_copies, attacker_value, gladion_value):
    cards = (
        ["attacker", "support"]
        + [f"gladion-{i}" for i in range(gladion_copies)]
        + [f"filler-{i}" for i in range(deck_cards - gladion_copies - 2)]
    )

    wait_total = 0.0
    for drawn in cards:
        if (
            drawn == "attacker"
            or drawn == "support"
            or drawn.startswith("gladion-")
        ):
            wait_total += attacker_value + gladion_value
        else:
            wait_total += max(attacker_value, gladion_value)

    after_attacker = [card for card in cards if card != "attacker"]
    eager_attacker = attacker_value + gladion_value * (
        sum(
            card == "support" or card.startswith("gladion-")
            for card in after_attacker
        )
        / len(after_attacker)
    )

    removed_gladion = f"gladion-{0}"
    after_gladion = [
        card
        for card in cards
        if card not in {"support", removed_gladion}
    ]
    eager_gladion = gladion_value + attacker_value * (
        sum(card == "attacker" for card in after_gladion)
        / len(after_gladion)
    )

    return {
        "eager_attacker": eager_attacker,
        "eager_gladion": eager_gladion,
        "wait_one_draw": wait_total / len(cards),
    }


for deck_cards, gladion_copies in ((8, 1), (8, 2), (12, 3)):
    for attacker_value, gladion_value in ((1, 1), (2, 1), (1, 3)):
        exact = policy_values(
            deck_cards,
            gladion_copies,
            attacker_value=attacker_value,
            gladion_value=gladion_value,
        )
        labeled = labeled_values(
            deck_cards,
            gladion_copies,
            attacker_value,
            gladion_value,
        )
        for policy in exact:
            assert abs(exact[policy] - labeled[policy]) < 1e-12

baseline = policy_values(40, 2)
probabilities = outcome_probabilities(40, 2)
assert abs(baseline["wait_one_draw"] - 1.1) < 1e-12
assert abs(baseline["eager_attacker"] - 1.0769230769230769) < 1e-12
assert abs(baseline["eager_gladion"] - 1.0263157894736843) < 1e-12
assert abs(probabilities["wait_both"] - 0.10) < 1e-12
assert abs(probabilities["eager_attacker_both"] - 3 / 39) < 1e-12
assert abs(probabilities["eager_gladion_both"] - 1 / 38) < 1e-12

for deck_cards in range(6, 21):
    for gladion_copies in range(1, deck_cards - 2):
        if deck_cards - gladion_copies - 2 == 0:
            continue
        for attacker_value, gladion_value in ((1, 1), (2, 1), (1, 2)):
            values = policy_values(
                deck_cards,
                gladion_copies,
                attacker_value=attacker_value,
                gladion_value=gladion_value,
            )
            assert values["wait_one_draw"] > values["eager_attacker"]
            assert values["wait_one_draw"] > values["eager_gladion"]

print(baseline)
print(probabilities)
print("validation passed")
