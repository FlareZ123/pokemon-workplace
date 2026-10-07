from __future__ import annotations

from dataclasses import dataclass, replace
from collections import Counter
from pathlib import Path
import re
from typing import Any, Literal

from tools.build_expanded_legality_baseline import classify_effective_legality, load_json

ActionClass = Literal["item", "supporter", "ability", "stadium", "attack"]


@dataclass(frozen=True)
class SearchState:
    deck_cards: int
    eligible_targets: int
    bench_slots: int = 5
    exact_prize_knowledge: bool = False

    def __post_init__(self) -> None:
        if self.deck_cards < 0 or self.eligible_targets < 0 or self.bench_slots < 0:
            raise ValueError("counts must be non-negative")
        if self.eligible_targets > self.deck_cards:
            raise ValueError("eligible targets cannot exceed cards in deck")


@dataclass(frozen=True)
class SearchResolution:
    legal: bool
    inspected_full_deck: bool
    target_moved: bool
    next_state: SearchState
    reason: str


def _is_attack(action_class: ActionClass) -> bool:
    return action_class == "attack"


def constrained_search_to_hand(
    state: SearchState, *, action_class: ActionClass
) -> SearchResolution:
    """Resolve a sole constrained full-deck search that puts an eligible target in hand.

    The model intentionally separates action legality from target availability.
    A non-attack action whose only effect is a full-deck search needs a nonempty
    deck to produce a resolvable search step. Once that step occurs, a constrained
    search may return zero targets while still inspecting the full deck.

    Attacks remain announceable when the search effect cannot be applied, assuming
    attack-specific prerequisites such as Energy and status have already been met.
    """

    if state.deck_cards == 0:
        return SearchResolution(
            legal=_is_attack(action_class),
            inspected_full_deck=False,
            target_moved=False,
            next_state=state,
            reason=(
                "attack may resolve with an unavailable search effect"
                if _is_attack(action_class)
                else "sole search effect has no nonempty deck to inspect"
            ),
        )

    moved = state.eligible_targets > 0
    next_state = replace(
        state,
        deck_cards=state.deck_cards - (1 if moved else 0),
        eligible_targets=state.eligible_targets - (1 if moved else 0),
        exact_prize_knowledge=True,
    )
    return SearchResolution(
        legal=True,
        inspected_full_deck=True,
        target_moved=moved,
        next_state=next_state,
        reason="full-deck search resolves; constrained search may return zero targets",
    )


def constrained_search_to_bench(
    state: SearchState, *, action_class: ActionClass
) -> SearchResolution:
    """Resolve a constrained deck search whose payload is put directly on the Bench.

    C-11 gives this family an additional destination gate. With a full Bench,
    Trainer cards and announced Abilities with this effect cannot be used. An attack
    can still be used, but its search ends before the deck is inspected.
    """

    if state.bench_slots == 0:
        return SearchResolution(
            legal=_is_attack(action_class),
            inspected_full_deck=False,
            target_moved=False,
            next_state=state,
            reason=(
                "attack remains legal but direct-to-Bench effect ends before deck search"
                if _is_attack(action_class)
                else "direct-to-Bench search is unusable with no open Bench slot"
            ),
        )

    base = constrained_search_to_hand(state, action_class=action_class)
    if not base.legal or not base.target_moved:
        return base
    return replace(
        base,
        next_state=replace(base.next_state, bench_slots=state.bench_slots - 1),
    )


def public_zone_up_to_retrieval(
    eligible_cards: int, *, action_class: ActionClass
) -> bool:
    """Legality for a sole `up to N` retrieval from a public zone.

    Trainers/announced Abilities/Stadium effects need at least one eligible card if
    choosing zero would leave game state unchanged. Attacks may still be used with
    zero eligible cards, assuming the attack itself is otherwise announceable.
    """

    if eligible_cards < 0:
        raise ValueError("eligible_cards must be non-negative")
    return eligible_cards > 0 or _is_attack(action_class)


def _trainer_action_class(card: dict[str, Any]) -> str:
    subtypes = set(card.get("subtypes") or ())
    if "Supporter" in subtypes:
        return "Supporter"
    if "Item" in subtypes:
        return "Item"
    if "Pokémon Tool" in subtypes:
        return "Pokémon Tool"
    if "Stadium" in subtypes:
        return "Stadium"
    return "Trainer"


def classify_trainer_search_destination(text: str) -> str:
    """Classify the destination of cards selected by the first full-deck search.

    Classification starts at the first search phrase so pre-search costs such as
    Pokemon Communication putting a hand card on top of the deck do not overwrite
    the destination of the searched card.
    """

    lower = " ".join(text.split()).lower()
    starts = [
        index
        for phrase in ("search your deck", "look through your deck")
        if (index := lower.find(phrase)) >= 0
    ]
    if not starts:
        raise ValueError("text does not contain a full-deck search phrase")
    search_text = lower[min(starts) :]

    if "put 1 of them into your hand. attach the other" in search_text:
        return "mixed_hand_attach"
    if "switch it with that" in search_text:
        return "replacement_switch"
    if (
        ("to evolve" in search_text or "counts as evolving" in search_text)
        and ("put it onto that pokémon" in search_text or "put it onto that pokemon" in search_text)
    ):
        return "evolve_in_play"
    if re.search(r"attach (?:it|them|those|the other)", search_text):
        return "attach_in_play"
    if "onto your bench" in search_text:
        return "bench"
    if re.search(r"discard (?:it|them|those cards)", search_text):
        return "discard"
    if (
        "put those cards on top of it" in search_text
        or "put that card on top of it" in search_text
        or "put those cards on top of your deck" in search_text
    ):
        return "topdeck"
    if "into your hand" in search_text or "in your hand" in search_text:
        return "hand"
    return "other"



def build_trainer_search_inventory(resources_root: Path) -> dict[str, Any]:
    sets = load_json(resources_root / "sets" / "en.json")
    expanded_sets = {
        entry["id"]
        for entry in sets
        if (entry.get("legalities") or {}).get("expanded") == "Legal"
    }

    variants: set[tuple[str, str, str]] = set()
    print_instances = 0

    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        if path.stem not in expanded_sets:
            continue
        for card in load_json(path):
            if card.get("supertype") != "Trainer":
                continue
            if classify_effective_legality(card)[0] == "Banned":
                continue
            action_class = _trainer_action_class(card)
            for rule in card.get("rules") or ():
                text = " ".join(rule.split())
                lower = text.lower()
                if "search your deck" not in lower and "look through your deck" not in lower:
                    continue
                if lower.startswith("you may play "):
                    continue
                print_instances += 1
                variants.add((action_class, card["name"], text))

    destination_counts = Counter(
        classify_trainer_search_destination(text)
        for _, _, text in variants
    )
    destination_rows = sorted(
        (
            classify_trainer_search_destination(text),
            action_class,
            name,
            text,
        )
        for action_class, name, text in variants
    )
    direct_to_bench = [
        row for row in destination_rows if row[0] == "bench"
    ]
    return {
        "print_text_instances": print_instances,
        "distinct_trainer_search_variants": len(variants),
        "destination_counts": dict(sorted(destination_counts.items())),
        "direct_to_bench_variants": len(direct_to_bench),
        "direct_to_bench_rows": [
            {"action_class": action_class, "card_name": name, "text": text}
            for _, action_class, name, text in direct_to_bench
        ],
    }
