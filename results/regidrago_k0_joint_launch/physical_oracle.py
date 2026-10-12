"""Independent physical-card K0 first-action oracle for small decks."""

from collections import Counter, defaultdict, deque
from fractions import Fraction
from functools import lru_cache
from itertools import combinations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from regidrago_joint_launch import Build
from regidrago_joint_launch_k0 import analyze_k0, first_actions

CATEGORIES = ("RV", "BASIC", "DP", "VIP", "QB", "MT", "BC", "D", "P")


def physical_k0(build: Build, *, opener=2, prizes=1):
    counts = (
        build.regidrago_v, build.other_basics, build.dragapult,
        build.vip, build.quick_ball, build.treasure, build.compressor,
        build.safe,
    )
    cards = []
    for name, n in zip(CATEGORIES, (*counts, build.total - sum(counts))):
        cards.extend([name] * n)
    assert len(cards) == build.total

    @lru_cache(maxsize=None)
    def choices(state):
        hand, deck, has_rv, loaded = state
        hand_by_type = {
            group: tuple(i for i in hand if cards[i] == group)
            for group in CATEGORIES
        }
        deck_by_type = {
            group: tuple(i for i in deck if cards[i] == group)
            for group in CATEGORIES
        }
        output = defaultdict(set)

        for item in hand_by_type["VIP"]:
            remaining_hand = hand - {item}
            output["vip"].add((remaining_hand, deck, has_rv, loaded))
            for target in deck_by_type["RV"]:
                output["vip"].add((
                    remaining_hand, deck - {target}, True, loaded,
                ))
        for item in hand_by_type["BC"]:
            remaining_hand = hand - {item}
            output["bc"].add((remaining_hand, deck, has_rv, loaded))
            for target in deck_by_type["DP"]:
                output["bc"].add((
                    remaining_hand, deck - {target}, has_rv, True,
                ))

        for kind in ("QB", "MT"):
            for item in hand_by_type[kind]:
                for payment_group in ("DP", "D"):
                    for payment in hand_by_type[payment_group]:
                        remaining_hand = hand - {item, payment}
                        now_loaded = loaded or payment_group == "DP"
                        action = (
                            ("qb" if kind == "QB" else "mt")
                            + ("_dp" if payment_group == "DP" else "_safe")
                        )
                        output[action].add((
                            remaining_hand, deck, has_rv, now_loaded,
                        ))
                        for target in deck_by_type["RV"]:
                            output[action].add((
                                remaining_hand, deck - {target}, True, now_loaded,
                            ))
                        if kind == "MT":
                            for target in deck_by_type["DP"]:
                                output[action].add((
                                    remaining_hand | {target},
                                    deck - {target}, has_rv, now_loaded,
                                ))
        return dict(output)

    @lru_cache(maxsize=None)
    def succeeds(start):
        pending = deque([start])
        seen = {start}
        while pending:
            state = pending.popleft()
            if state[2] and state[3]:
                return True
            for next_states in choices(state).values():
                for following in next_states:
                    if following not in seen:
                        seen.add(following)
                        pending.append(following)
        return False

    action_hits = defaultdict(Counter)
    worlds_per_hand = Counter()
    clairvoyant_hits = 0
    worlds = 0
    for opening in combinations(range(build.total), opener):
        if not any(cards[i] in ("RV", "BASIC") for i in opening):
            continue
        remaining = tuple(i for i in range(build.total) if i not in opening)
        for prize in combinations(remaining, prizes):
            remaining_after_prizes = [i for i in remaining if i not in prize]
            for drawn in remaining_after_prizes:
                hand = frozenset((*opening, drawn))
                deck = frozenset(
                    i for i in remaining_after_prizes if i != drawn
                )
                counts_hand = Counter(cards[i] for i in hand)
                key = tuple(counts_hand[name] for name in CATEGORIES)
                start = (hand, deck, bool(counts_hand["RV"]), False)
                legal_actions = first_actions(key)
                available = choices(start)
                assert set(legal_actions) == set(available), (
                    legal_actions, set(available)
                )
                for action in legal_actions:
                    action_hits[key][action] += any(
                        succeeds(next_state)
                        for next_state in available[action]
                    )
                clairvoyant_hits += succeeds(start)
                worlds_per_hand[key] += 1
                worlds += 1

    best_hits = sum(max(action_hits[key].values(), default=0) for key in worlds_per_hand)
    return {
        "k0_joint": Fraction(best_hits, worlds),
        "clairvoyant_joint": Fraction(clairvoyant_hits, worlds),
        "information_gap": Fraction(clairvoyant_hits - best_hits, worlds),
    }


def verify():
    for build in (
        Build(regidrago_v=2, other_basics=2, dragapult=1, vip=1,
              quick_ball=1, treasure=1, compressor=1, safe=0, total=10),
        Build(regidrago_v=2, other_basics=2, dragapult=2, vip=1,
              quick_ball=1, treasure=1, compressor=0, safe=1, total=10),
    ):
        exact = analyze_k0(build, opener=2, prizes=1)
        physical = physical_k0(build, opener=2, prizes=1)
        for metric, observed in physical.items():
            assert exact[metric] == observed, (build, metric, exact[metric], observed)
        print("PASS labeled-card K0 commitment oracle", build, physical, flush=True)


if __name__ == "__main__":
    verify()
