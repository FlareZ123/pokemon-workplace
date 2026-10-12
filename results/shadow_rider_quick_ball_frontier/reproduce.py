"""Reproduce source-checked exact Quick Ball launch and physical-card oracles."""
import json
from fractions import Fraction
from pathlib import Path

from results.competitive_deck_baselines import shadow_rider_reproduce as baseline
from tools.shadow_rider_quick_ball_frontier import (
    COUNTS, exact, labeled_toy, policy,
)


def verify() -> None:
    baseline.verify()
    assert COUNTS == (1, 4, 4, 1, 1, 13, 11, 25)
    assert baseline.POKEMON["Radiant Eternatus"] == COUNTS[0]
    assert baseline.POKEMON["Shadow Rider Calyrex VMAX"] == COUNTS[1]
    assert baseline.TRAINERS["Mysterious Treasure"] == COUNTS[2]
    assert baseline.TRAINERS["Hisuian Heavy Ball"] == COUNTS[3]
    assert baseline.TRAINERS["Quick Ball"] == COUNTS[4]
    assert sum(baseline.ENERGY.values()) == COUNTS[6]
    assert sum(COUNTS) == sum(baseline.POKEMON.values()) + sum(
        baseline.TRAINERS.values()
    ) + sum(baseline.ENERGY.values()) == 60

    root = Path(__file__).resolve().parents[2]
    specs = [
        ("Radiant Eternatus", "abilities", "Climactic Gate", "up to 2 Pokémon VMAX"),
        ("Quick Ball", "rules", None, "Search your deck for a Basic Pokémon"),
        ("Mysterious Treasure", "rules", None, "Psychic or Dragon Pokémon"),
        ("Hisuian Heavy Ball", "rules", None, "face-down Prize cards"),
    ]
    for name, field, ability, fragment in specs:
        card_id = baseline.PRINT_IDS[name]
        set_id = card_id.rsplit("-", 1)[0]
        records = json.loads(
            (root / "resources" / "cards" / "en" / (set_id + ".json")).read_text(
                encoding="utf-8"
            )
        )
        card = next(card for card in records if card["id"] == card_id)
        if ability:
            texts = [a["text"] for a in card["abilities"] if a["name"] == ability]
        else:
            texts = card[field]
        assert any(fragment in text for text in texts), (name, fragment)

    for toy in (
        (1, 2, 1, 1, 1, 2, 2, 2),
        (1, 2, 2, 1, 1, 2, 1, 3),
    ):
        grouped = exact(toy, 3, 2)
        physical = labeled_toy(toy)
        assert grouped == physical, (toy, grouped, physical)

    grouped = exact()
    assert sum(grouped.values()) == 1
    assert grouped["direct"] == Fraction(2431309737, 20230837760)
    assert grouped["heavy"] == Fraction(121298091771, 9791725475840)
    assert grouped["treasure_energy_paid"] == Fraction(
        402091494907, 1618467020800
    )
    assert grouped["quick_energy_paid"] == Fraction(7449584241, 161846702080)
    assert grouped["quick_unrestricted_only"] == Fraction(
        99575546409, 8901568614400
    )
    assert policy(grouped, "unrestricted") == Fraction(
        4960433059823, 9791725475840
    )
    assert policy(grouped, "energy") == Fraction(
        83628107904937, 195834509516800
    )
    assert policy(grouped, "energy_or_extra_search") == Fraction(
        8825535109147, 19583450951680
    )
    old_routes = (
        grouped["direct"] + grouped["heavy"] +
        grouped["treasure_energy_paid"] + grouped["treasure_ball_paid"] +
        grouped["treasure_unrestricted_only"]
    )
    assert abs(float(old_routes) - 0.4493794401251962) < 1e-14
    without_quick = exact((1, 4, 4, 1, 0, 13, 11, 26))
    assert policy(without_quick, "unrestricted") == old_routes

    for name in ("unrestricted", "energy", "energy_or_extra_search"):
        print(name, f"{100 * float(policy(grouped, name)):.9f}%")
    print("incremental Quick Ball", f"{100 * float(grouped['quick_energy_paid'] + grouped['quick_unrestricted_only']):.9f} points")
    print("two independent exact physical toy oracles passed")


if __name__ == "__main__":
    verify()
