"""Independent physical-shuffle validation of the exact Poffin staging model."""

from __future__ import annotations

from collections import Counter
import json
import random

from reproduce import joint_access


def estimate(vip: int, nest: int, poffin: int, eligible: bool,
             trials: int = 200_000, seed: int = 20261010) -> tuple[float, float]:
    rng = random.Random(seed)
    original = (
        ["E"] * 4 + ["A"] * 4 + ["V"] * vip + ["N"] * nest
        + ["P"] * poffin + ["X"] * (52 - vip - nest - poffin)
    )
    staged = joint = 0
    for _ in range(trials):
        cards = original.copy()
        rng.shuffle(cards)
        hand = cards[:7]
        prizes = cards[7:13]
        deck = cards[13:]
        if "E" not in hand:
            continue
        hand.append(deck.pop(0))
        have = Counter(hand)
        missing_e = max(0, 2 - have["E"])
        missing_a = max(0, 1 - have["A"])
        missing = missing_e + missing_a
        remaining = max(0, missing - 2 * have["V"])
        if eligible:
            use_p = min(have["P"], (remaining + 1) // 2)
            use_n = max(0, remaining - 2 * use_p)
        elif have["V"]:
            use_p = use_n = 0
        else:
            use_p = min(have["P"], missing_e)
            use_n = missing_a + missing_e - use_p
        if use_n > have["N"]:
            continue
        if deck.count("E") < missing_e or deck.count("A") < missing_a:
            continue
        for _ in range(missing_e):
            deck.remove("E")
        for _ in range(missing_a):
            deck.remove("A")
        staged += 1
        if have["N"] + have["P"] - use_n - use_p > 0:
            joint += 1
        elif deck.pop(0) in ("N", "P"):
            joint += 1
    return staged/trials, joint/trials


def main() -> None:
    cases = [(0,0,4,True), (1,3,0,True), (1,3,0,False), (0,0,4,False),
             (0,1,3,True), (1,2,1,False)]
    results = []
    for vip,nest,poffin,eligible in cases:
        estimate_stage, estimate_joint = estimate(vip,nest,poffin,eligible)
        exact_stage, exact_joint = joint_access(
            vip,nest,poffin,anchor_poffin_eligible=eligible
        )
        # Absolute 0.3 percentage-point MC tolerance, ~6 standard errors.
        assert abs(estimate_stage - float(exact_stage)) < 0.003
        assert abs(estimate_joint - float(exact_joint)) < 0.003
        results.append({
            "vip":vip, "nest":nest, "poffin":poffin,
            "anchor_poffin_eligible":eligible,
            "stage_mc_percent":round(estimate_stage*100,5),
            "stage_exact_percent":round(float(exact_stage)*100,5),
            "joint_mc_percent":round(estimate_joint*100,5),
            "joint_exact_percent":round(float(exact_joint)*100,5),
        })
    print(json.dumps({"trials_per_case":200_000, "seed":20261010,"results":results},indent=2))


if __name__ == "__main__":
    main()
