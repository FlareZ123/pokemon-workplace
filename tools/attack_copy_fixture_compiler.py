"""Compile legal attack-copy signatures into executable kernel fixture specs."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from attack_copy_catalog import build as build_catalog
from attack_copy_execution_phases import build as build_phases
from attack_copy_kernel import CopySelector


@dataclass(frozen=True)
class CompiledCopyFixture:
    attack_name: str
    card_names: tuple[str, ...]
    print_ids: tuple[str, ...]
    selector: CopySelector
    is_gx: bool = False
    pre_event: str | None = None
    post_event: str | None = None


SOURCE_MAP: dict[str, dict[str, Any]] = {
    "own_discard_dragon": {
        "source": "own_discard",
        "required_type": "Dragon",
    },
    "own_bench_fusion_strike": {
        "source": "own_bench",
        "required_subtype": "Fusion Strike",
    },
    "own_bench_named_n": {
        "source": "own_bench",
        "required_name_prefix": "N's ",
    },
    "own_bench_any": {"source": "own_bench"},
    "self_previous_evolution": {"source": "self_previous_evolution"},
    "own_deck_top_card": {"source": "own_deck_top"},
    "opponent_deck_top10": {"source": "opponent_revealed"},
    "opponent_hand": {"source": "opponent_hand"},
    "opponent_last_attack": {"source": "opponent_last_attack"},
    "opponent_active_tera": {
        "source": "opponent_active",
        "required_subtype": "Tera",
    },
    "opponent_active_non_gx": {
        "source": "opponent_active",
        "require_non_gx": True,
    },
    "opponent_active_any": {"source": "opponent_active"},
    "opponent_in_play": {"source": "opponent_in_play"},
    "opponent_chooses_in_play": {
        "source": "opponent_in_play",
        "chooser": "opponent",
    },
    "opponent_any_pokemon": {"source": "opponent_in_play"},
}


def _selector_for(signature: dict[str, Any], phase: dict[str, Any]) -> CopySelector:
    source_classes = signature["source_classes"]
    if len(source_classes) != 1:
        raise ValueError(
            f"signature has ambiguous source classes: {signature['attack_name']}"
        )
    source_class = source_classes[0]
    try:
        kwargs = dict(SOURCE_MAP[source_class])
    except KeyError as exc:
        raise ValueError(f"unsupported source class: {source_class}") from exc

    if signature["direct_non_gx_filter"]:
        kwargs["require_non_gx"] = True
    if signature["optional_selection"]:
        kwargs["optional_selection"] = True
    if phase["selected_attack_energy_gate_position"] is not None:
        kwargs["require_selected_energy"] = True

    lifetime = phase["source_lifetime_pattern"]
    if lifetime == "selected_source_discarded_from_opponent_hand_before_body":
        kwargs["move_selected_source_to"] = "discard"
    elif lifetime == "top_card_discarded_before_eligibility_and_body":
        kwargs["precommit_source_to"] = "discard"
        kwargs["require_no_rule_box"] = True

    return CopySelector(**kwargs)


def _outer_events(
    signature: dict[str, Any],
) -> tuple[str | None, str | None]:
    text = signature["text"].lower()
    if "top 10 cards of your opponent's deck" in text:
        return "reveal_top_10", "shuffle_revealed"
    if "opponent reveals their hand" in text:
        return "reveal_hand", None
    if "discard the top card of your deck" in text:
        return "discard_top_card", None
    return None, None


def build(resources_root: Path) -> dict[str, Any]:
    catalog = build_catalog(resources_root)
    phases = build_phases(resources_root)
    phase_by_key = {
        (row["attack_name"], row["attack_text"]): row
        for row in phases["signatures"]
    }

    fixtures: list[CompiledCopyFixture] = []
    for signature in catalog["signatures"]:
        key = (signature["attack_name"], signature["text"])
        phase = phase_by_key[key]
        pre_event, post_event = _outer_events(signature)
        fixtures.append(
            CompiledCopyFixture(
                attack_name=signature["attack_name"],
                card_names=tuple(signature["card_names"]),
                print_ids=tuple(signature["print_ids"]),
                selector=_selector_for(signature, phase),
                is_gx=phase["trailing_semantics"] == "gx_usage_rule",
                pre_event=pre_event,
                post_event=post_event,
            )
        )

    fixtures.sort(key=lambda row: (row.attack_name, row.print_ids))
    source_classes = sorted(
        {
            signature["source_classes"][0]
            for signature in catalog["signatures"]
        }
    )
    return {
        "signature_count": len(fixtures),
        "source_class_count": len(source_classes),
        "source_classes": source_classes,
        "fixtures": [
            {
                **{
                    key: value
                    for key, value in asdict(fixture).items()
                    if key != "selector"
                },
                "selector": asdict(fixture.selector),
            }
            for fixture in fixtures
        ],
    }


def atomic_write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, indent=2, ensure_ascii=False) + "\n"
    lock_path = path.with_suffix(path.suffix + ".lock")
    with lock_path.open("a+b") as lock_file:
        if os.name == "nt":
            import msvcrt

            if lock_file.tell() == 0:
                lock_file.write(b"0")
                lock_file.flush()
                lock_file.seek(0)
            msvcrt.locking(lock_file.fileno(), msvcrt.LK_LOCK, 1)
        else:
            import fcntl

            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)

        tmp_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=path.parent,
                delete=False,
            ) as tmp_file:
                tmp_file.write(payload)
                tmp_file.flush()
                os.fsync(tmp_file.fileno())
                tmp_path = Path(tmp_file.name)
            os.replace(tmp_path, path)
        finally:
            if tmp_path is not None and tmp_path.exists():
                tmp_path.unlink()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compile Expanded attack-copy signatures into kernel fixture specs."
    )
    parser.add_argument("--resources-root", type=Path, default=Path("resources"))
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/attack_copy_fixture_compiler/fixtures.json"),
    )
    args = parser.parse_args()
    result = build(args.resources_root)
    atomic_write_json(args.output, result)
    print(
        json.dumps(
            {
                "signature_count": result["signature_count"],
                "source_class_count": result["source_class_count"],
                "source_classes": result["source_classes"],
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
