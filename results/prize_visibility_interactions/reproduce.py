"""Reproduce Prize-visibility interaction catalog results."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from prize_visibility_interactions import (  # noqa: E402
    direct_exact_prize_publicity,
    own_face_down_prize_effects,
)


def main() -> None:
    resources = ROOT / "resources"

    face_down = own_face_down_prize_effects(resources)
    assert len(face_down) == 12

    names = {row["card_name"] for row in face_down}
    assert names == {
        "Mr. Mime",
        "Chinchou",
        "Blacephalon",
        "Gladion",
        "Beast Ball",
        "Poipole",
        "Daisy's Help",
        "Cresselia",
        "Hisuian Heavy Ball",
        "Arc Phone",
        "Patrat",
        "Umbreon",
    }

    publicity = direct_exact_prize_publicity(resources)
    assert len(publicity["public"]) == 4
    assert len(publicity["private"]) == 5

    public_names = {row["card_name"] for row in publicity["public"]}
    private_names = {row["card_name"] for row in publicity["private"]}

    assert public_names == {
        "Town Map",
        "Celesteela-GX",
        "Naganadel & Guzzlord-GX",
        "Here Comes Team Rocket!",
    }
    assert private_names == {
        "Gladion",
        "Beast Ball",
        "Poipole",
        "Daisy's Help",
        "Hisuian Heavy Ball",
    }

    print("Own-face-down-Prize effect variants:", len(face_down))
    for row in face_down:
        suffix = f" / {row['effect_name']}" if row["effect_name"] else ""
        print(f"  {row['action_class']}: {row['card_name']}{suffix}")

    print("\nDirect exact-Prize publicity")
    print("  public face-up:")
    for name in sorted(public_names):
        print(f"    {name}")
    print("  private look:")
    for name in sorted(private_names):
        print(f"    {name}")

    print("\nAll Prize-visibility interaction checks passed.")


if __name__ == "__main__":
    main()
