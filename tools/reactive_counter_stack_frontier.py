"""Bounded, card-grounded counter-reaction stacks for Active Mega Scrafty ex.

Static post-attack-effects, pre-Knock-Out research, not a match simulator.
"""
from __future__ import annotations
from dataclasses import dataclass
import json
from pathlib import Path
from build_expanded_legality_baseline import classify_effective_legality

SOURCE_CARDS = {
    "active": ("me2pt5-135", "Mega Scrafty ex", "Counterattacking Crest", "place 5 damage counters on the Attacking Pokémon"),
    "aura": ("me1-87", "Spiritomb", "Spiteful Swirl", "place 1 damage counter on the Attacking Pokémon"),
    "punk": ("me2-92", "Punk Helmet", "", "place 4 damage counters on the Attacking Pokémon"),
    "deluxe": ("sv7-134", "Deluxe Bomb", "", "put 12 damage counters on the Attacking Pokémon"),
    "spiky": ("sv9-159", "Spiky Energy", "", "put 2 damage counters on the Attacking Pokémon"),
}

@dataclass(frozen=True)
class Stack:
    spiritomb: int
    spiky: int
    tool: str = "none"

    def __post_init__(self) -> None:
        if not 0 <= self.spiritomb <= 4 or not 0 <= self.spiky <= 4:
            raise ValueError("counts must obey the four-copy rule")
        if self.tool not in {"none", "punk", "deluxe"}:
            raise ValueError("at most one known Tool can be attached")

    def counters(self, *, abilities=True, tools=True, special_energy=True) -> int:
        return (
            (5 + self.spiritomb if abilities else 0)
            + (2 * self.spiky if special_energy else 0)
            + ({"none": 0, "punk": 4, "deluxe": 12}[self.tool] if tools else 0)
        )

    def earliest_reaction_turn(self) -> int:
        """Lower bound with ordinary Stage 1 evolution and manual attachments."""
        return max(2, self.spiky)

    def earliest_outlaw_leg_turn(self) -> int:
        """Lower bound for two Darkness plus Colorless, no acceleration."""
        return max(2, self.spiky + (3 if self.spiky == 0 else 2))

def source_validate(resources: Path) -> None:
    sets = {s["id"]: s for s in json.loads((resources / "sets" / "en.json").read_text(encoding="utf-8"))}
    for role, (print_id, name, ability_name, text_fragment) in SOURCE_CARDS.items():
        set_id = print_id.split("-", 1)[0]
        meta = sets[set_id]
        if meta["legalities"].get("expanded") != "Legal" or meta["releaseDate"] > "2026/10/12":
            raise ValueError(f"{role}: set unavailable in paper Expanded as of 2026-10-12")
        cards = json.loads((resources / "cards" / "en" / f"{set_id}.json").read_text(encoding="utf-8"))
        card = next(c for c in cards if c["id"] == print_id)
        if card["name"] != name or classify_effective_legality(card)[0] != "Legal":
            raise ValueError(f"{role}: source identity or legality changed")
        if ability_name:
            texts = [a["text"] for a in card.get("abilities") or () if a["name"] == ability_name]
        else:
            texts = card.get("rules") or ()
        if not any(text_fragment in text and "is damaged by an attack" in text and "Knocked Out" in text for text in texts):
            raise ValueError(f"{role}: required reaction wording absent")
        if role == "active":
            if card.get("evolvesFrom") != "Scraggy" or card.get("subtypes", [])[:1] != ["Stage 1"]:
                raise ValueError("Mega Scrafty evolution line changed")
            if not any(a.get("cost") == ["Darkness", "Darkness", "Colorless"] for a in card.get("attacks") or []):
                raise ValueError("Outlaw Leg Energy cost changed")
        if role == "deluxe" and "ACE SPEC" not in card.get("subtypes", []):
            raise ValueError("Deluxe Bomb ACE SPEC constraint changed")
        if role == "spiky" and "Special" not in card.get("subtypes", []):
            raise ValueError("Spiky Energy class changed")

def pareto(threshold_counters: int, tool: str, *, abilities=True, tools=True, special_energy=True) -> tuple[Stack, ...]:
    """Return resource-nondominated Spiritomb Bench and Spiky attachment counts."""
    if threshold_counters < 0:
        raise ValueError("nonnegative threshold required")
    candidates = [Stack(b, e, tool) for b in range(5) for e in range(5)]
    feasible = [s for s in candidates if s.counters(abilities=abilities, tools=tools, special_energy=special_energy) >= threshold_counters]
    return tuple(s for s in feasible if not any(
        other.spiritomb <= s.spiritomb and other.spiky <= s.spiky
        and (other.spiritomb, other.spiky) != (s.spiritomb, s.spiky)
        for other in feasible
    ))

def study() -> dict:
    tools = ("punk", "deluxe")
    return {
        "sources": {key: value[0] for key, value in SOURCE_CARDS.items()},
        "full_stack_counters": {tool: Stack(4, 4, tool).counters() for tool in tools},
        "suppressed_full_stack": {
            "ability_lock": Stack(4, 4, "deluxe").counters(abilities=False),
            "tool_effect_lock": Stack(4, 4, "deluxe").counters(tools=False),
            "both_locks": Stack(4, 4, "deluxe").counters(abilities=False, tools=False),
        },
        "pareto": {
            str(threshold): {
                tool: [
                    {"spiritomb": s.spiritomb, "spiky": s.spiky,
                     "earliest_reaction_turn": s.earliest_reaction_turn(),
                     "earliest_attack_turn": s.earliest_outlaw_leg_turn()}
                    for s in pareto(threshold // 10, tool)
                ]
                for tool in tools
            }
            for threshold in (160, 220, 280, 290, 300)
        },
    }
