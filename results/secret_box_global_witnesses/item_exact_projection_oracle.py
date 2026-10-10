"""Independent physical-deck projection oracle for exact Item necessity.

Rejection-samples 12,000 accepted physical 60-card permutations with all
other Tool/Stadium Prized, and verifies the compressed exact enumerator's
category/Active/top-five projection reproduces the original planner's
three Boolean outcomes for the same physical state.
"""
from collections import Counter
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "tools"))

from aichi_vileplume_als import BASICS
from aichi_vileplume_secret_box import (
    BASE_DECK, SECRET_BOX_DECK, _raw_state, _state_succeeds,
    _compress_hand, _compress_deck,
)
from aichi_secret_box_output_dependencies import _state_succeeds_with_mask
from exact_six_prize_item_necessity import (
    COUNTS, GNH, TAG, TM, JET, ACE, BUN, FAN, JIR, BASIC,
    SUPPORT, TAG_OTHER, SPECIAL_OTHER, FILLER, STELLAR,
    outcome, state,
)
from importance_sample_prize_tails import forced_indices, conditioned_order

GROUPS = {
    "Guzma & Hala": GNH,
    "Tag Call": TAG,
    "Technical Machine: Evolution": TM,
    "Jet Energy": JET,
    "Grand Tree": ACE,
    "Secret Box": ACE,
    "Bunnelby": BUN,
    "Fan Rotom": FAN,
    "Jirachi": JIR,
    "Bellelba & Brycen-Man": TAG_OTHER,
    "Capture Energy": SPECIAL_OTHER,
    "Memory Energy": SPECIAL_OTHER,
    **{name: SUPPORT for name in (
        "Guzma", "Cassius", "Karen", "Plumeria", "Gladion",
        "Faba", "Lusamine", "Peonia", "Team Yell's Cheer"
    )},
}
STELLAR_BIT = {
    "Guzma & Hala": 1, "Tag Call": 2,
    "Technical Machine: Evolution": 4, "Secret Box": 8,
}

def group(name):
    if name in GROUPS:
        return GROUPS[name]
    return BASIC if name in BASICS else FILLER

def main(trials=12_000):
    rng = random.Random(20261010)
    required = forced_indices((
        "Stealthy Hood", "Stealthy Hood", "Stealthy Hood",
        "Counter Gain", "Artazon", "Artazon",
    ))
    hits = 0
    for j in range(trials):
        order = conditioned_order(rng, required)
        base = _raw_state(BASE_DECK, order)
        secret = _raw_state(SECRET_BOX_DECK, order)
        assert base is not None and secret is not None
        opening = [BASE_DECK[i] for i in order[:7]]
        draw = BASE_DECK[order[13]]
        top = [SECRET_BOX_DECK[i] for i in order[14:19]]
        cat_open = tuple(Counter(map(group, opening))[i] for i in range(13))
        assert all(n <= limit for n, limit in zip(cat_open, COUNTS))
        cat_draw = group(draw)
        act = secret[2] if secret[2] in ("Jirachi", "Fan Rotom", "Bunnelby") \
            else "other Basic"
        topmask = 0
        for n in top:
            topmask |= STELLAR_BIT.get(n, 0)
        projected = outcome(cat_open, cat_draw, act, topmask)

        source = (
            not _state_succeeds(base)
            and _state_succeeds_with_mask(secret, 15)
            and not _state_succeeds_with_mask(secret, 14)
        )
        assert projected == source, (
            j, order[:19], cat_open, cat_draw, act, topmask,
            projected, source
        )
        hits += int(source)
        if j % 1000 == 0:
            print("checked", j, "item_hits", hits, flush=True)
    print("All physical projections agree:", trials,
          "rare item hits:", hits)


if __name__ == "__main__":
    main()
