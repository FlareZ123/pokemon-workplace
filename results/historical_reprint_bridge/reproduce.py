from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.historical_reprint_evidence import (
    NO_REFERENCE_REPRINT_IDS,
    NO_REFERENCE_REPRINTS,
    summarize_historical_reprint_evidence,
)
from tools.reprint_errata_resolution import build_reprint_resolver

RESOURCES = ROOT / "resources"
summary = summarize_historical_reprint_evidence(RESOURCES)
counts = summary["counts"]

assert counts == {
    "historical_no_reference_prints": 42,
    "names": 8,
    "trainer_prints": 41,
    "energy_prints": 1,
}
assert summary["prints_by_name"] == {
    "Double Colorless Energy": 1,
    "Energy Search": 7,
    "Energy Switch": 7,
    "Full Heal": 1,
    "Poké Ball": 9,
    "Recycle": 1,
    "Super Scoop Up": 6,
    "Switch": 10,
}
assert len(NO_REFERENCE_REPRINT_IDS) == 42
assert set(summary["bridges"]) == set(NO_REFERENCE_REPRINTS)
assert all(
    bridge["bw_onward_targets_available_by_bridge_date"]
    for bridge in summary["bridges"].values()
)

resolver = build_reprint_resolver(RESOURCES)
boilerplate_exact = {"dp1-110", "dp5-85", "hgss1-93", "hgss1-95", "pl1-113"}
assert all(
    resolver.resolve(card_id).kind == "exact_fingerprint_candidate"
    for card_id in boilerplate_exact
)
assert all(
    resolver.resolve(card_id).kind == "historical_official_reprint_candidate"
    for card_id in NO_REFERENCE_REPRINT_IDS - boilerplate_exact
)
assert len(NO_REFERENCE_REPRINT_IDS - boilerplate_exact) == 37
assert resolver.resolve("base1-95").name == "Switch"
assert resolver.resolve("base1-96").name == "Double Colorless Energy"

print("historical official reprint bridge: PASS")
print("historical no-reference prints:", counts["historical_no_reference_prints"])
print("Trainer prints:", counts["trainer_prints"])
print("Energy prints:", counts["energy_prints"])
