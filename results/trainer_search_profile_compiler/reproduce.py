"""Reproduce the conservative multi-output Trainer profile compiler."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from trainer_search_profile_compiler import (  # noqa: E402
    SearchOutput,
    compile_multi_output_trainer_profiles,
)


def _representative(
    profiles: tuple,
    name: str,
):
    matches = [
        profile
        for profile in profiles
        if profile.name == name
    ]
    if not matches:
        raise AssertionError(f"{name} missing")
    return matches[0]


def main() -> None:
    profiles = compile_multi_output_trainer_profiles(
        ROOT / "resources"
    )

    if len(profiles) != 40:
        raise AssertionError(len(profiles))
    if len({profile.name for profile in profiles}) != 16:
        raise AssertionError(
            sorted({profile.name for profile in profiles})
        )

    arven = _representative(profiles, "Arven")
    if arven.action_class != "Supporter":
        raise AssertionError(arven)
    if arven.base_outputs != (
        SearchOutput("Item card", 1),
        SearchOutput("Pokémon Tool card", 1),
    ):
        raise AssertionError(arven)

    secret_box = _representative(profiles, "Secret Box")
    if secret_box.action_class != "Item":
        raise AssertionError(secret_box)
    if secret_box.required_discard_other_cards != 3:
        raise AssertionError(secret_box)
    if secret_box.base_outputs != (
        SearchOutput("Item card", 1),
        SearchOutput("Pokémon Tool card", 1),
        SearchOutput("Supporter card", 1),
        SearchOutput("Stadium card", 1),
    ):
        raise AssertionError(secret_box)

    larry = _representative(profiles, "Larry's Skill")
    if not larry.discards_entire_hand:
        raise AssertionError(larry)
    if len(larry.base_outputs) != 3:
        raise AssertionError(larry)

    rosa = _representative(profiles, "Rosa")
    if rosa.play_condition is None:
        raise AssertionError(rosa)
    if "Knocked Out" not in rosa.play_condition:
        raise AssertionError(rosa.play_condition)

    guzma_hala = _representative(profiles, "Guzma & Hala")
    if guzma_hala.base_outputs != (
        SearchOutput("Stadium card", 1),
    ):
        raise AssertionError(guzma_hala)
    if guzma_hala.conditional_outputs != (
        SearchOutput("Pokémon Tool card", 1),
        SearchOutput("Special Energy card", 1),
    ):
        raise AssertionError(guzma_hala)
    if guzma_hala.optional_discard_other_cards != 2:
        raise AssertionError(guzma_hala)

    sabrina_brycen = _representative(
        profiles,
        "Sabrina & Brycen",
    )
    if sabrina_brycen.base_outputs != (
        SearchOutput("basic Energy card", 2),
    ):
        raise AssertionError(sabrina_brycen)
    if sabrina_brycen.conditional_outputs != (
        SearchOutput("Pokémon of different types", 3),
    ):
        raise AssertionError(sabrina_brycen)
    if sabrina_brycen.optional_discard_other_cards != 5:
        raise AssertionError(sabrina_brycen)

    print(
        {
            "compiled_prints": len(profiles),
            "compiled_unique_names": len(
                {profile.name for profile in profiles}
            ),
        }
    )
    for profile in (
        arven,
        secret_box,
        guzma_hala,
        sabrina_brycen,
    ):
        print(profile)


if __name__ == "__main__":
    main()
