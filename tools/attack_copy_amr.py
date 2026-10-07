"""AMR-oriented gate profiles for Expanded attack-copy effects.

The semantic copy graph says which selections can exist. This module records
additional stochastic, adversarial, resource, and information gates that make
those selections more or less realistic in actual game states.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import tempfile
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Any

from attack_copy_catalog import build as build_copy_catalog


def top_n_hit_probability(deck_size: int, eligible_cards: int, reveal_count: int) -> Fraction:
    if not 0 <= eligible_cards <= deck_size:
        raise ValueError("eligible_cards must be between 0 and deck_size")
    if deck_size <= 0:
        raise ValueError("deck_size must be positive")
    if reveal_count < 0:
        raise ValueError("reveal_count must be non-negative")
    sample = min(deck_size, reveal_count)
    if sample == 0 or eligible_cards == 0:
        return Fraction(0, 1)
    misses = math.comb(deck_size - eligible_cards, sample) if deck_size - eligible_cards >= sample else 0
    return Fraction(1, 1) - Fraction(misses, math.comb(deck_size, sample))


def top_card_hit_probability(deck_size: int, eligible_cards: int) -> Fraction:
    if not 0 <= eligible_cards <= deck_size:
        raise ValueError("eligible_cards must be between 0 and deck_size")
    if deck_size <= 0:
        raise ValueError("deck_size must be positive")
    return Fraction(eligible_cards, deck_size)


def gate_flags(signature: dict[str, Any]) -> dict[str, bool]:
    text = signature["text"].lower()
    return {
        "coin_flip_gate": "flip a coin" in text,
        "copied_energy_gate": "necessary energy" in text,
        "adversarial_choice": "your opponent chooses an attack" in text,
        "random_top_card_sample": "discard the top card of your deck" in text,
        "opponent_top_10_sample": "top 10 cards of your opponent" in text,
        "opponent_hand_observation": "opponent reveals their hand" in text,
        "prize_count_gate": "exactly 2 prize cards remaining" in text,
        "empty_hand_gate": "no cards in your hand" in text,
        "previous_turn_attack_gate": (
            "during their last turn" in text or "during his or her last turn" in text
        ),
        "pre_copy_discard": (
            "discard the top card of your deck" in text
            or "may discard a pokémon you find there" in text
        ),
        "post_copy_continuation": "shuffle the revealed cards into your opponent" in text,
        "optional_copy": bool(signature["optional_selection"]),
    }


def build(resources_root: Path) -> dict[str, Any]:
    catalog = build_copy_catalog(resources_root)
    profiles = []
    counts: Counter[str] = Counter()
    any_extra_gate = 0

    for signature in catalog["signatures"]:
        flags = gate_flags(signature)
        active = sorted(name for name, enabled in flags.items() if enabled)
        for name in active:
            counts[name] += 1
        if active:
            any_extra_gate += 1
        profiles.append(
            {
                "attack_name": signature["attack_name"],
                "card_names": signature["card_names"],
                "source_classes": signature["source_classes"],
                "active_gate_flags": active,
            }
        )

    example_haughty = [
        {
            "deck_size": 50,
            "eligible_cards": eligible,
            "reveal_count": 10,
            "hit_probability": float(top_n_hit_probability(50, eligible, 10)),
        }
        for eligible in (1, 2, 4, 8, 12)
    ]

    return {
        "scope": catalog["scope"],
        "counts": {
            "copy_signatures": len(profiles),
            "signatures_with_any_extra_gate": any_extra_gate,
            "signatures_without_listed_extra_gate": len(profiles) - any_extra_gate,
            "gate_flags": dict(sorted(counts.items())),
        },
        "profiles": profiles,
        "exact_probability_tools": {
            "top_n_without_replacement": "1 - C(N-K, n) / C(N, n), where n=min(reveal_count,N)",
            "top_card": "K / N",
            "haughty_order_examples": example_haughty,
        },
        "modeling_notes": [
            "Coin-flip gates have a base success chance of one half before any game effects that modify or repeat coin flips.",
            "Necessary-Energy wording is a deterministic state predicate and overrides the C-18 default that copied attacks do not require their printed Energy cost.",
            "Opponent-choice copy effects should be evaluated under an opponent policy or worst-case response rather than as if the copying player chooses the endpoint.",
            "Top-card and top-N sampling gates can be evaluated exactly from the current eligible-card count when the deck composition is known.",
            "Observed hand, Prize-count, empty-hand, and previous-turn gates are state variables rather than fixed card values.",
            "These profiles supplement source-zone eligibility; they do not replace board, lock, Energy, or matchup modeling.",
        ],
    }


def atomic_write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, indent=2, ensure_ascii=False) + "\n"
    lock_path = path.with_suffix(path.suffix + ".lock")
    with lock_path.open("a+b") as lock_file:
        if os.name == "nt":
            import msvcrt
            msvcrt.locking(lock_file.fileno(), msvcrt.LK_LOCK, 1)
        else:
            import fcntl
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)

        tmp_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as tmp_file:
                tmp_file.write(payload)
                tmp_file.flush()
                os.fsync(tmp_file.fileno())
                tmp_path = Path(tmp_file.name)
            os.replace(tmp_path, path)
        finally:
            if tmp_path is not None and tmp_path.exists():
                tmp_path.unlink()


def main() -> None:
    parser = argparse.ArgumentParser(description="Profile Active Move Realism gates on attack-copy effects.")
    parser.add_argument("--resources-root", type=Path, default=Path("resources"))
    parser.add_argument("--output", type=Path, default=Path("results/attack_copy_semantics/amr_profile.json"))
    args = parser.parse_args()
    result = build(args.resources_root)
    atomic_write_json(args.output, result)
    print(json.dumps(result["counts"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
