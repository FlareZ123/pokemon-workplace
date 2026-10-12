"""SFT: first-turn Basic access if Ditto Prism Star's Ability is suppressed.

Permanent Ditto-off source readiness requires both native Voltorb and Pikachu.
The remaining assumptions match the exact paid Quick Ball Energy policy study.
"""

from __future__ import annotations

import json
from fractions import Fraction

from quick_ball_upper import search
from quick_ball_energy_sensitivity import (
    BASIC_TYPES, POLICIES, actor_state, sample_space,
)
from reproduce import MANIFEST, native_bases, source_card, validate_sources


def main() -> None:
    validate_sources()
    rows = json.loads(MANIFEST.read_text(encoding="utf-8"))["cards"]
    assert any(row["print_id"] == "sv1-96" for row in rows)
    assert any(row["print_id"] == "sm8-154" for row in rows)
    klefki = source_card("sv1-96")["abilities"][0]["text"]
    ditto = source_card("sm8-154")["abilities"][0]["text"]
    assert "Basic Pokémon in play" in klefki and "have no Abilities" in klefki
    assert "put any Stage 1 card" in ditto

    total = natural_native = 0
    success = {policy: 0 for policy in POLICIES}
    for seven, prizes, drawn, weight in sample_space():
        total += weight
        observed = list(seven)
        observed[drawn] += 1
        if native_bases(observed[0], observed[1]):
            natural_native += weight
        for policy in POLICIES:
            works = any(
                search(
                    *actor_state(seven, prizes, drawn, active),
                    policy, "native",
                )
                for active in BASIC_TYPES if seven[active]
            )
            if works:
                success[policy] += weight

    assert Fraction(natural_native, total) == Fraction(351120, 9797437)
    assert Fraction(success["all_cards"], total) == Fraction(
        489234081697, 2227643250690
    )
    assert Fraction(success["energy_only"], total) == Fraction(
        205174562628, 1262331175391
    )
    assert (
        success["all_cards"] >= success["energy_or_quickball"]
        >= success["energy_only"] >= natural_native
    )
    print(json.dumps({
        "native_only_natural": natural_native / total,
        "native_only_unrestricted_quick_ball": success["all_cards"] / total,
        "native_only_energy_or_quickball": (
            success["energy_or_quickball"] / total
        ),
        "native_only_energy_only": success["energy_only"] / total,
        "fraction_unrestricted": str(Fraction(success["all_cards"], total)),
        "fraction_energy_only": str(Fraction(success["energy_only"], total)),
        "interpretation": "Ditto Ability remains disabled; native source pair required",
        "not_modeled": "Klefki switching, other Items and Abilities, opponent",
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
