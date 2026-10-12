"""Independent physical-card witness for the grouped Forest Seal Stone solver."""
from collections import Counter
from fractions import Fraction
from itertools import combinations

from tools.shadow_rider_forest_stone_frontier import (
    MODES, exact_stone, success,
)
from tools.shadow_rider_quick_ball_frontier import exact, policy
from results.competitive_deck_baselines import shadow_rider_reproduce as baseline

TOYS = (
    (1, 2, 1, 1, 1, 2, 2, 2),
    (1, 2, 2, 1, 1, 2, 1, 3),
)


def physical_oracle(
    counts: tuple[int, ...], v_copies: int = 1,
) -> dict[str, dict[str, Fraction]]:
    """Deal labeled individual cards; identify true Stone and true V."""
    cards = []
    for category, quantity in enumerate(counts):
        for i in range(quantity):
            flag = (
                "V" if category == 5 and i < v_copies
                else "Stone" if category == 7 and i == 0
                else ""
            )
            cards.append((category, flag))
    stats = {mode: Counter() for mode in MODES}
    denominator = 0
    indices = set(range(len(cards)))
    for opener_ids in combinations(range(len(cards)), 3):
        opener = [cards[i] for i in opener_ids]
        if not any(c in (0, 5) for c, _ in opener):
            continue
        remaining = indices.difference(opener_ids)
        for prize_ids in combinations(remaining, 2):
            prize = [cards[i] for i in prize_ids]
            for draw_id in remaining.difference(prize_ids):
                denominator += 1
                hand = opener + [cards[draw_id]]
                deck = [
                    cards[i] for i in
                    remaining.difference(prize_ids).difference({draw_id})
                ]
                hand_names = [c for c, _ in hand]
                prize_names = [c for c, _ in prize]
                deck_names = [c for c, _ in deck]
                for mode, tallies in stats.items():
                    if not any(c == 5 for c, _ in opener):
                        label = "no_alternate_basic"
                    elif deck_names.count(1) < 2:
                        label = "vm_depleted"
                    elif 0 in hand_names:
                        label = "direct"
                    elif 3 in hand_names and 0 in prize_names:
                        label = "heavy"
                    elif (
                        0 in deck_names and 2 in hand_names and (
                            mode == "unrestricted"
                            or 6 in hand_names
                            or (
                                mode == "energy_or_extra_search"
                                and (
                                    hand_names.count(2) > 1
                                    or 4 in hand_names
                                )
                            )
                        )
                    ):
                        label = "treasure"
                    elif (
                        0 in deck_names and 4 in hand_names and (
                            mode == "unrestricted"
                            or 6 in hand_names
                            or (
                                mode == "energy_or_extra_search"
                                and 2 in hand_names
                            )
                        )
                    ):
                        label = "quick"
                    elif (
                        any(flag == "Stone" for _, flag in hand)
                        and any(flag == "V" for _, flag in hand)
                        and (
                            0 in deck_names
                            or (0 in prize_names and 3 in deck_names)
                        )
                    ):
                        label = (
                            "stone_radiant" if 0 in deck_names
                            else "stone_heavy"
                        )
                    else:
                        label = "fail"
                    tallies[label] += 1
    return {
        mode: {
            key: Fraction(n, denominator) for key, n in count.items()
        }
        for mode, count in stats.items()
    }


def verify() -> None:
    baseline.verify()
    assert baseline.POKEMON["Shadow Rider Calyrex V"] == 3
    assert baseline.TRAINERS["Forest Seal Stone"] == 1

    for counts in TOYS:
        grouped = exact_stone(counts, 3, 2, v_copies=1)
        physical = physical_oracle(counts)
        for mode in MODES:
            assert dict(grouped[mode]) == physical[mode], (counts, mode)

    a = exact_stone()
    q = exact()
    fractions = {
        "unrestricted": Fraction(3177239486592979, 5982744265738240),
        "energy": Fraction(3901028598627549, 8546777522483200),
        "energy_or_extra_search": Fraction(
            409306820761549, 854677752248320
        ),
    }
    for mode in MODES:
        assert success(a[mode]) == fractions[mode]
        assert success(a[mode]) - policy(q, mode) == (
            a[mode]["stone_radiant"] + a[mode]["stone_heavy"]
        )
        print(mode, f"{100 * float(success(a[mode])):.9f}%")
    print("Two independent physical Stone + V card oracles matched.")


if __name__ == "__main__":
    verify()
