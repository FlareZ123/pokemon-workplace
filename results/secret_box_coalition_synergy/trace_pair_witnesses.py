"""Trace early-hand features of seeded Tool+Stadium synergy cases."""

from collections import Counter
from pathlib import Path
import random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))

from aichi_secret_box_output_dependencies import _state_succeeds_with_mask
from aichi_vileplume_secret_box import (
    BASE_DECK, SECRET_BOX_DECK, BOX_ALL_OUTPUTS,
    BOX_TOOL_OUTPUT, BOX_STADIUM_OUTPUT,
    _raw_state, _state_succeeds,
)


def main(trials: int = 100_000) -> None:
    rng = random.Random(20261007)
    total = 0
    profiles = Counter()
    pair = BOX_TOOL_OUTPUT | BOX_STADIUM_OUTPUT

    for _ in range(trials):
        while True:
            order = rng.sample(range(60), 60)
            baseline = _raw_state(BASE_DECK, order)
            if baseline is not None:
                break
        secret = _raw_state(SECRET_BOX_DECK, order)
        assert secret is not None
        if _state_succeeds(baseline):
            continue
        if not _state_succeeds_with_mask(secret, BOX_ALL_OUTPUTS):
            continue
        if not _state_succeeds_with_mask(secret, pair):
            continue
        if (_state_succeeds_with_mask(secret, BOX_TOOL_OUTPUT)
                or _state_succeeds_with_mask(secret, BOX_STADIUM_OUTPUT)):
            continue

        total += 1
        hand, deck, active, top = secret
        # All flags refer to the physical start before any chosen Stellar Wish.
        profile = (
            hand["Jet Energy"] > 0,
            hand["Technical Machine: Evolution"] > 0,
            hand["Artazon"] > 0,
            active == "Bunnelby" or hand["Bunnelby"] > 0,
            active == "Jirachi"
                and ("Guzma & Hala" in top or "Tag Call" in top),
            hand["Secret Box"] > 0,
            active == "Jirachi" and "Secret Box" in top,
            deck["Technical Machine: Evolution"] > 0,
            deck["Artazon"] > 0,
        )
        profiles[profile] += 1

    # Mask10 978, Tool-only 470, Stadium-only 135, two overlapping:
    # 978 - (470 + 135 - 2) = 375.
    assert total == {100_000: 375, 500_000: 1_917}[trials], total
    assert sum(profiles.values()) == total
    names = (
        "Jet already in hand", "TM Evolution already in hand",
        "Artazon already in hand", "Bunnelby active or in hand",
        "Jirachi may find G&H or Tag Call", "Box in hand",
        "Box visible to Jirachi", "TM searchable", "Artazon searchable",
    )
    for i, name in enumerate(names):
        print(name, sum(n for key, n in profiles.items() if key[i]))
    for profile, count in sorted(profiles.items()):
        print("profile", profile, count)
    print("Latent Tool+Stadium states:", total)
    print("Witness profile regression passed.")


if __name__ == "__main__":
    main()
