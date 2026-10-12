"""SFT: independent labeled physical-card oracle for Item discard routes."""
from collections import Counter
from fractions import Fraction
from itertools import combinations
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from regidrago_payload_load_frontier import Build, exact_access, counterfactuals


def physical(
    build: Build, *, opening_size: int, prize_count: int
) -> dict[str, Fraction]:
    groups = {
        "dp": (build.dragapult, False),
        "bc": (build.compressor, False),
        "qb": (build.quick_ball, False),
        "mt": (build.mysterious_treasure, False),
        "rv": (build.regidrago_v, True),
        "ob": (build.other_basics, True),
        "safe": (build.safe_filler, False),
    }
    other = build.total - sum(count for count, _ in groups.values())
    groups["protected"] = (other, False)
    cards = [
        (name, basic) for name, (count, basic) in groups.items()
        for _ in range(count)
    ]
    assert len(cards) == build.total
    event_counts = Counter()
    worlds = 0

    for opener in combinations(range(len(cards)), opening_size):
        if not any(cards[i][1] for i in opener):
            continue
        outside_hand = [i for i in range(len(cards)) if i not in opener]
        for prizes in combinations(outside_hand, prize_count):
            prize_set = set(prizes)
            remaining = [i for i in outside_hand if i not in prize_set]
            for drawn in remaining:
                worlds += 1
                hand = Counter(cards[i][0] for i in (*opener, drawn))
                deck = Counter(cards[i][0] for i in remaining if i != drawn)
                compressor = hand["bc"] > 0 and deck["dp"] > 0
                held = (
                    hand["dp"] > 0 and hand["qb"] + hand["mt"] > 0
                    and deck["rv"] > 0
                )
                chain = (
                    deck["dp"] > 0 and hand["mt"] > 0
                    and hand["qb"] + hand["mt"] >= 2 and deck["rv"] > 0
                )
                direct = compressor or held
                ideal = direct or chain
                safe = direct or (chain and hand["safe"] > 0)
                events = {
                    "dragapult_not_all_prized": hand["dp"] + deck["dp"] > 0,
                    "loaded_direct": direct,
                    "loaded_ideal": ideal,
                    "loaded_safe": safe,
                    "loaded_bc": compressor,
                    "loaded_hand_payment": held,
                    "loaded_chain_ideal": chain,
                    "loaded_chain_safe": chain and hand["safe"] > 0,
                    "regidrago_hand": hand["rv"] > 0,
                    "joint_loaded_ideal_regidrago_hand": ideal and hand["rv"] > 0,
                    "joint_loaded_safe_regidrago_hand": safe and hand["rv"] > 0,
                }
                for key, occurred in events.items():
                    if occurred:
                        event_counts[key] += 1
    return {
        key: Fraction(event_counts[key], worlds)
        for key in (
            "dragapult_not_all_prized", "loaded_direct", "loaded_ideal",
            "loaded_safe", "loaded_bc", "loaded_hand_payment",
            "loaded_chain_ideal", "loaded_chain_safe", "regidrago_hand",
            "joint_loaded_ideal_regidrago_hand",
            "joint_loaded_safe_regidrago_hand",
        )
    }


def check() -> None:
    toy = (
        Build(
            dragapult=1, compressor=1, quick_ball=1, mysterious_treasure=1,
            regidrago_v=2, other_basics=2, safe_filler=1, total=12,
        ),
        Build(
            dragapult=2, compressor=0, quick_ball=1, mysterious_treasure=1,
            regidrago_v=2, other_basics=2, safe_filler=1, total=12,
        ),
        Build(
            dragapult=2, compressor=1, quick_ball=0, mysterious_treasure=1,
            regidrago_v=2, other_basics=2, safe_filler=0, total=12,
        ),
        Build(
            dragapult=1, compressor=0, quick_ball=1, mysterious_treasure=2,
            regidrago_v=2, other_basics=2, safe_filler=1, total=12,
        ),
    )
    for case in toy:
        exact = exact_access(case, prize_count=2, opening_size=3)
        oracle = physical(case, opening_size=3, prize_count=2)
        assert exact == oracle, {
            key: (exact[key], oracle[key])
            for key in oracle if exact[key] != oracle[key]
        }
        print("toy labeled-deck oracle PASS", case)

    original = exact_access(Build())
    for safe_count in (0, 10, 20, 30):
        profiles = counterfactuals(safe_count)
        findings = {name: exact_access(build) for name, build in profiles.items()}
        assert findings["published"]["loaded_direct"] == original["loaded_direct"]
        for row in findings.values():
            assert (
                row["loaded_direct"] <= row["loaded_safe"]
                <= row["loaded_ideal"] <= row["dragapult_not_all_prized"]
            )
        assert (
            findings["second Dragapult for Battle Compressor"]["loaded_direct"]
            < original["loaded_direct"]
        )
        print("safe filler", safe_count)
        for name, row in findings.items():
            print(" ", name, {
                key: f"{100 * float(row[key]):.8f}%"
                for key in ("loaded_direct", "loaded_safe", "loaded_ideal")
            })

    print("PASS: exact first-draw route model and independent physical oracle")


if __name__ == "__main__":
    check()
