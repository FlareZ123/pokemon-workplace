from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal

from tools.build_expanded_legality_baseline import classify_effective_legality

SourceChannel = Literal["attack", "ability", "item", "supporter", "stadium", "rule"]
TimingPolicy = Literal["c12_default_permitted", "explicit_permitted", "blocked"]
FirstTurnWindow = Literal["both", "second_only", "none"]

_DIRECT_TO_EVOLVE_RE = re.compile(
    r"\bput\b[^.]*?\bonto\b[^.]*?\bto evolve\b",
    re.IGNORECASE,
)
_COUNTS_AS_EVOLVING_RE = re.compile(
    r"\bput\b[^.]*?\b(?:on|onto)\b[^.]*?\.\s*\(this counts as evolving",
    re.IGNORECASE,
)
_FIRST_TURN_BLOCK_RE = re.compile(
    r"(?:can't|cannot)[^.]*?(?:during (?:your|their) first turn|first turn)",
    re.IGNORECASE,
)
_ENTRY_TURN_BLOCK_RE = re.compile(
    r"(?:can't|cannot)[^.]*?(?:"
    r"on (?:a )?(?:basic )?pokémon that was put into play this turn"
    r"|(?:on )?the turn this pokémon was put into play"
    r")",
    re.IGNORECASE,
)
_GRAND_TREE_ENTRY_BLOCK_RE = re.compile(
    r"players can't evolve[^.]*?pokémon that was put into play this turn",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class EvolutionEffectProfile:
    card_id: str
    card_name: str
    supertype: str
    subtypes: tuple[str, ...]
    source_kind: Literal["attack", "ability", "rule"]
    source_name: str
    source_channel: SourceChannel
    timing_policy: TimingPolicy
    entry_turn_policy: TimingPolicy
    intrinsic_source_window: FirstTurnWindow
    structural_first_turn_window: FirstTurnWindow
    text: str


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_text(text: str) -> str:
    return " ".join(text.split())


def is_direct_evolution_effect(text: str) -> bool:
    normalized = normalize_text(text)
    return bool(_DIRECT_TO_EVOLVE_RE.search(normalized) or _COUNTS_AS_EVOLVING_RE.search(normalized))


def source_channel(card: dict[str, Any], source_kind: str) -> SourceChannel:
    if source_kind == "attack":
        return "attack"
    if source_kind == "ability":
        return "ability"

    subtypes = set(card.get("subtypes") or [])
    if "Item" in subtypes:
        return "item"
    if "Supporter" in subtypes:
        return "supporter"
    if "Stadium" in subtypes:
        return "stadium"
    return "rule"


def timing_policy(text: str) -> TimingPolicy:
    normalized = normalize_text(text)
    lower = normalized.lower()

    if _FIRST_TURN_BLOCK_RE.search(normalized) or "except during their first turn" in lower:
        return "blocked"

    explicit_markers = (
        "you can use this card during your first turn",
        "you can use this ability during your first turn",
        "can evolve during your first turn",
    )
    if any(marker in lower for marker in explicit_markers):
        return "explicit_permitted"
    if "if you go first, you can use this attack" in lower and "first turn" in lower:
        return "explicit_permitted"

    return "c12_default_permitted"


def entry_turn_policy(text: str) -> TimingPolicy:
    normalized = normalize_text(text)
    lower = normalized.lower()

    if _ENTRY_TURN_BLOCK_RE.search(normalized) or _GRAND_TREE_ENTRY_BLOCK_RE.search(normalized):
        return "blocked"

    explicit_markers = (
        "you can use this card during your first turn or on a pokémon that was put into play this turn",
        "you can use this ability during your first turn or on a pokémon that was put into play this turn",
        "you can use this card on a pokémon you put down when you were setting up to play or on a pokémon that was put into play this turn",
    )
    if any(marker in lower for marker in explicit_markers):
        return "explicit_permitted"

    return "c12_default_permitted"


def intrinsic_source_window(channel: SourceChannel, text: str) -> FirstTurnWindow:
    lower = normalize_text(text).lower()
    if channel == "attack":
        if "if you go first, you can use this attack" in lower and "first turn" in lower:
            return "both"
        return "second_only"
    if channel == "supporter":
        if "if you go first" in lower and (
            "may use this card during your first turn" in lower
            or "may play this card during your first turn" in lower
        ):
            return "both"
        return "second_only"
    return "both"


def structural_window(policy: TimingPolicy, source_window: FirstTurnWindow) -> FirstTurnWindow:
    if policy == "blocked":
        return "none"
    return source_window


def iter_effect_entries(card: dict[str, Any]):
    for attack in card.get("attacks") or []:
        yield "attack", attack.get("name", ""), attack.get("text", "")
    for ability in card.get("abilities") or []:
        yield "ability", ability.get("name", ""), ability.get("text", "")
    for index, text in enumerate(card.get("rules") or []):
        yield "rule", f"rule_{index}", text


def build_profiles(resources_root: Path) -> list[EvolutionEffectProfile]:
    sets = load_json(resources_root / "sets" / "en.json")
    expanded_sets = {
        row["id"]
        for row in sets
        if (row.get("legalities") or {}).get("expanded") == "Legal"
    }

    profiles: list[EvolutionEffectProfile] = []
    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        if path.stem not in expanded_sets:
            continue
        for card in load_json(path):
            status, _source = classify_effective_legality(card)
            if status != "Legal":
                continue
            for kind, name, raw_text in iter_effect_entries(card):
                text = normalize_text(raw_text)
                if not is_direct_evolution_effect(text):
                    continue
                channel = source_channel(card, kind)
                policy = timing_policy(text)
                entry_policy = entry_turn_policy(text)
                source_window = intrinsic_source_window(channel, text)
                profiles.append(
                    EvolutionEffectProfile(
                        card_id=card["id"],
                        card_name=card["name"],
                        supertype=card.get("supertype", ""),
                        subtypes=tuple(card.get("subtypes") or ()),
                        source_kind=kind,
                        source_name=name,
                        source_channel=channel,
                        timing_policy=policy,
                        entry_turn_policy=entry_policy,
                        intrinsic_source_window=source_window,
                        structural_first_turn_window=structural_window(policy, source_window),
                        text=text,
                    )
                )

    return sorted(profiles, key=lambda p: (p.card_name, p.card_id, p.source_kind, p.source_name))


def summarize(profiles: list[EvolutionEffectProfile]) -> dict[str, Any]:
    return {
        "print_level_profiles": len(profiles),
        "unique_card_names": len({p.card_name for p in profiles}),
        "by_timing_policy": dict(sorted(Counter(p.timing_policy for p in profiles).items())),
        "by_entry_turn_policy": dict(
            sorted(Counter(p.entry_turn_policy for p in profiles).items())
        ),
        "by_source_channel": dict(sorted(Counter(p.source_channel for p in profiles).items())),
        "by_structural_first_turn_window": dict(
            sorted(Counter(p.structural_first_turn_window for p in profiles).items())
        ),
        "c12_default_unique_names": len(
            {p.card_name for p in profiles if p.timing_policy == "c12_default_permitted"}
        ),
        "c12_default_both_order_names": sorted(
            {
                p.card_name
                for p in profiles
                if p.timing_policy == "c12_default_permitted"
                and p.structural_first_turn_window == "both"
            }
        ),
    }


def write_json_atomic_locked(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = path.with_suffix(path.suffix + ".lock")
    encoded = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    with lock_path.open("a+b") as lock_file:
        if os.name == "nt":
            import msvcrt

            if lock_path.stat().st_size == 0:
                lock_file.write(b"\0")
                lock_file.flush()
            lock_file.seek(0)
            msvcrt.locking(lock_file.fileno(), msvcrt.LK_LOCK, 1)
        else:
            import fcntl

            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)

        tmp_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=path.parent, delete=False
            ) as tmp_file:
                tmp_file.write(encoded)
                tmp_file.flush()
                os.fsync(tmp_file.fileno())
                tmp_path = Path(tmp_file.name)
            os.replace(tmp_path, path)
        finally:
            if tmp_path is not None and tmp_path.exists():
                tmp_path.unlink()
            if os.name == "nt":
                lock_file.seek(0)
                msvcrt.locking(lock_file.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compile literal direct-evolution effects and first-turn timing policy in paper Expanded."
    )
    parser.add_argument("--resources-root", type=Path, default=Path("resources"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    profiles = build_profiles(args.resources_root)
    payload = {
        "summary": summarize(profiles),
        "profiles": [asdict(profile) for profile in profiles],
    }

    if args.output is not None:
        write_json_atomic_locked(args.output, payload)

    print(json.dumps(payload["summary"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
