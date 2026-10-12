"""Reproducible source-grounded 2026 Aichi top-32 opponent test plan.

This module emits *assignments*, not gameplay outcomes. Proxies are single
verified 60-card representatives of source archetypes, often not the other
players' actual decklists. Iron Thorns is an English-adapted Japanese 60.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIELD = ROOT / "results" / "tests" / "aichi_2026_top32_field" / "field.json"


def load_field(path: Path = FIELD) -> dict:
    """Load an explicitly time-frozen observed top-32 archetype classification."""
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data["groups"]
    assert data["source"] == "https://limitlesstcg.com/tournaments/566/statistics"
    assert data["successful_list_total"] == 32
    assert len(rows) == len({row["archetype"] for row in rows})
    assert all(type(row["count"]) is int and row["count"] > 0 for row in rows)
    assert sum(row["count"] for row in rows) == 32
    return data


def available_proxies(data: dict) -> dict[str, str]:
    """A source archetype may have only one proposed English 60-card proxy."""
    out = {
        g["archetype"]: g["proxy_dir"]
        for g in data["groups"] if g["proxy_dir"] is not None
    }
    for name in out.values():
        assert (ROOT / "results" / "decks" / name / "README.md").is_file(), name
    return out


def coverage(data: dict) -> dict:
    """Report classification coverage without misreporting 926-player shares."""
    rows = data["groups"]
    known = [r for r in rows if r["proxy_dir"] is not None]
    return {
        "observed_top32": sum(r["count"] for r in rows),
        "provisional_proxy_top32": sum(r["count"] for r in known),
        "archetypes": len(rows),
        "provisional_proxy_archetypes": len(known),
        "missing": [{"archetype": r["archetype"], "count": r["count"]}
                    for r in rows if r["proxy_dir"] is None],
    }


def assignment_seed(candidate: str, opponent: str, replica: int,
                    scenario: str) -> int:
    """Stable uint32 seed with explicit named input labels."""
    key = json.dumps(["aichi2026_top32_v1", candidate, opponent,
                      replica, scenario], separators=(",", ":"))
    return int.from_bytes(hashlib.sha256(key.encode("utf-8")).digest()[:4],
                          byteorder="big")


def paired_plan(data: dict, candidate: str,
                scenario: str = "observed_top32") -> list[dict]:
    """Build symmetric two-seat schedules across *available* archetype proxies.

    In the observed_top32 scenario each source category contributes its
    top-32 count, rather than 926-player registration share. In the
    equal_archetypes scenario each present proxy contributes once.

    A mirror assignment remains explicit as a policy/seat control but must
    not be counted as evidence of relative archetype strength. This does not
    prove the Twinleaf implementation can actually play either 60.
    """
    if scenario not in ("observed_top32", "equal_archetypes"):
        raise ValueError("unknown research scenario")
    proxies = available_proxies(data)
    if candidate not in proxies:
        raise ValueError("candidate must have a currently verified 60-card proxy")
    out = []
    pair_id = 0
    for row in data["groups"]:
        opponent = row["archetype"]
        if opponent not in proxies:
            continue
        repetitions = row["count"] if scenario == "observed_top32" else 1
        for replica in range(repetitions):
            seed = assignment_seed(candidate, opponent, replica, scenario)
            for orientation, first, second in (
                ("AB", candidate, opponent),
                ("BA", opponent, candidate),
            ):
                out.append({
                    "pair_id": pair_id, "seed": seed,
                    "scenario": scenario,
                    "candidate": candidate,
                    "opponent": opponent,
                    "seat_orientation": orientation,
                    "seat1_proxy": proxies[first],
                    "seat2_proxy": proxies[second],
                    "mirror_control": candidate == opponent,
                })
            pair_id += 1
    return out


if __name__ == "__main__":
    data = load_field()
    print(json.dumps({"coverage": coverage(data),
                      "example_paired_plan": paired_plan(data, "Regidrago")[:4]},
                     indent=2))
