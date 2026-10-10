"""Trace the other two inclusion-minimal two-category Aichi routes.

Replays the pinned 500k accepted-opening seed. Per category-pair, collect
observed state features and Prize/searchability signatures without
supposing the card sequence from a compressed state histogram alone.
"""

from collections import Counter
from pathlib import Path
import random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))

from aichi_secret_box_output_dependencies import _state_succeeds_with_mask
from aichi_vileplume_secret_box import (
    BASE_DECK, SECRET_BOX_DECK, BOX_ALL_OUTPUTS,
    _raw_state, _state_succeeds,
    TOOL_OTHER, SUPPORTER_OTHER, TAG_TEAM_OTHER,
)


def minimal_pair(outcomes, pair):
    return outcomes[pair] and all(
        not outcomes[sub]
        for sub in range(16)
        if sub != pair and sub & pair == sub
    )


def main(trials: int = 500_000) -> None:
    rng = random.Random(20261007)
    profiles = {6: Counter(), 12: Counter()}
    raw_features = {6: Counter(), 12: Counter()}
    shared = 0
    incremental = 0

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
        incremental += 1

        outcomes = {
            2: _state_succeeds_with_mask(secret, 2),
            4: _state_succeeds_with_mask(secret, 4),
            6: _state_succeeds_with_mask(secret, 6),
            8: _state_succeeds_with_mask(secret, 8),
            12: _state_succeeds_with_mask(secret, 12),
        }
        a = outcomes[6] and not outcomes[2] and not outcomes[4]
        b = outcomes[12] and not outcomes[4] and not outcomes[8]
        if not (a or b):
            continue
        shared += a and b

        hand, deck, active, top = secret
        features = (
            hand["Jet Energy"] > 0,
            hand["Technical Machine: Evolution"] > 0,
            hand["Artazon"] > 0,
            active == "Bunnelby" or hand["Bunnelby"] > 0,
            hand["Guzma & Hala"] > 0,
            hand["Tag Call"] > 0,
            hand["Secret Box"] > 0,
            active == "Jirachi" and "Secret Box" in top,
            active == "Jirachi" and "Guzma & Hala" in top,
            active == "Jirachi" and "Tag Call" in top,
            deck["Jet Energy"] > 0,
            deck["Technical Machine: Evolution"] > 0,
            deck["Artazon"] > 0,
            deck["Guzma & Hala"] > 0,
            deck["Tag Call"] > 0,
            deck["Bunnelby"] > 0,
            any(deck[name] > 0 for name in TOOL_OTHER),
            any(deck[name] > 0 for name in SUPPORTER_OTHER),
            any(deck[name] > 0 for name in TAG_TEAM_OTHER),
            deck["Counter Gain"] > 0,
            deck["Stealthy Hood"] > 0,
        )
        for bit, is_pair in ((6, a), (12, b)):
            if is_pair:
                profiles[bit][features] += 1
                raw_features[bit][
                    (active, sum(count for name, count in hand.items()
                                 if name not in {
                                     "Guzma & Hala", "Tag Call",
                                     "Technical Machine: Evolution",
                                     "Artazon", "Jet Energy", "Secret Box",
                                     "Bunnelby", "Fan Rotom",
                                 }), hand["Jet Energy"],
                     hand["Technical Machine: Evolution"],
                     hand["Artazon"], hand["Bunnelby"],
                     deck["Jet Energy"], deck["Technical Machine: Evolution"],
                     deck["Artazon"], deck["Guzma & Hala"],
                     deck["Tag Call"], deck["Bunnelby"])
                ] += 1

    assert incremental == 20_785, incremental
    assert sum(profiles[6].values()) == 42
    assert sum(profiles[12].values()) == 42
    assert shared == 24, shared

    labels = (
        "Jet initial", "TM initial", "Artazon initial", "Bunnelby initial",
        "G&H initial", "Tag Call initial", "Box initial", "Jirachi sees Box",
        "Jirachi sees G&H", "Jirachi sees Tag Call", "Jet searchable",
        "TM searchable", "Artazon searchable", "G&H searchable",
        "Tag Call searchable", "Bunnelby searchable",
        "non-TM Tool searchable", "other Supporter searchable",
        "other TAG TEAM searchable",
        "Counter Gain searchable", "Stealthy Hood searchable",
    )
    for mask in (6, 12):
        print("pair", mask, "total", sum(profiles[mask].values()))
        for i, label in enumerate(labels):
            n = sum(count for values, count in profiles[mask].items() if values[i])
            print("trait", mask, label, n)
        print("unique_binary_profiles", mask, len(profiles[mask]))
        for values, count in sorted(profiles[mask].items()):
            print("binary_profile", mask, values, count)
        print("unique_raw_profiles", mask, len(raw_features[mask]))
        for values, count in raw_features[mask].most_common(12):
            print("common_raw_profile", mask, values, count)
    print("both-pair minimal states:", shared)
    print("Small-pair witness classification passed.")


if __name__ == "__main__":
    main()
