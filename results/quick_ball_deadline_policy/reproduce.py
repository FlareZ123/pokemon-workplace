from functools import lru_cache
from math import comb
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from quick_ball_deadline_policy import deadline_success_probability


def labeled_probability(deck, attacker_deadline, gladion_deadline):
    horizon = max(attacker_deadline, gladion_deadline)

    @lru_cache(maxsize=None)
    def value(cards, quick_ball, attacker_done, gladion_done, elapsed):
        cards = tuple(cards)
        actions = [(cards, quick_ball, attacker_done, gladion_done)]

        if quick_ball:
            if not attacker_done and "attacker" in cards:
                actions.append((
                    tuple(card for card in cards if card != "attacker"),
                    False,
                    True,
                    gladion_done,
                ))
            support = "support" in cards
            gladions = [card for card in cards if card.startswith("gladion-")]
            if not gladion_done and support and gladions:
                removed = {"support", gladions[0]}
                actions.append((
                    tuple(card for card in cards if card not in removed),
                    False,
                    attacker_done,
                    True,
                ))

        best = 0.0
        for next_cards, next_quick, a_done, g_done in actions:
            if (
                (not a_done and elapsed >= attacker_deadline)
                or (not g_done and elapsed >= gladion_deadline)
            ):
                continue
            if a_done and g_done:
                best = 1.0
                continue
            if elapsed >= horizon:
                continue

            probability = 0.0
            for index, drawn in enumerate(next_cards):
                remaining = next_cards[:index] + next_cards[index + 1:]
                draw_a_done = a_done or drawn == "attacker"
                draw_g_done = g_done or drawn.startswith("gladion-")

                if drawn == "support" and not draw_g_done:
                    gladions = [
                        card
                        for card in remaining
                        if card.startswith("gladion-")
                    ]
                    if gladions:
                        removed = gladions[0]
                        remaining = tuple(
                            card for card in remaining if card != removed
                        )
                        draw_g_done = True

                probability += value(
                    tuple(sorted(remaining)),
                    next_quick,
                    draw_a_done,
                    draw_g_done,
                    elapsed + 1,
                ) / len(next_cards)

            best = max(best, probability)

        return best

    return value(tuple(sorted(deck)), True, False, False, 0)


small_deck = (
    "attacker",
    "support",
    "gladion-0",
    "gladion-1",
    "filler-0",
    "filler-1",
    "filler-2",
)
for attacker_deadline in range(0, 4):
    for gladion_deadline in range(0, 4):
        exact = deadline_success_probability(
            7,
            2,
            attacker_deadline=attacker_deadline,
            gladion_deadline=gladion_deadline,
        )
        labeled = labeled_probability(
            small_deck,
            attacker_deadline,
            gladion_deadline,
        )
        assert abs(exact - labeled) < 1e-12, (
            attacker_deadline,
            gladion_deadline,
            exact,
            labeled,
        )

for deadline in range(1, 9):
    exact = deadline_success_probability(
        40,
        2,
        attacker_deadline=deadline,
        gladion_deadline=deadline,
    )
    closed = 1 - comb(36, deadline) / comb(40, deadline)
    assert abs(exact - closed) < 1e-12

baseline_pairs = (
    (1, 1),
    (2, 2),
    (4, 4),
    (1, 4),
    (2, 4),
    (4, 1),
    (4, 2),
)
for attacker_deadline, gladion_deadline in baseline_pairs:
    value = deadline_success_probability(
        40,
        2,
        attacker_deadline=attacker_deadline,
        gladion_deadline=gladion_deadline,
    )
    print(attacker_deadline, gladion_deadline, f"{value:.9%}")

print("validation passed")
