from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.reprint_equivalence_vector import benchmark_profiles, summarize_benchmark_profiles
from tools.reprint_errata_resolution import build_reprint_resolver

RESOURCES = ROOT / "resources"

profiles = {row.name: row for row in benchmark_profiles()}
summary = summarize_benchmark_profiles()
resolver = build_reprint_resolver(RESOURCES)

assert summary["counts"] == {
    "profiles": 4,
    "state_model_equivalent": 1,
    "state_model_divergent": 3,
    "state_model_unresolved": 0,
    "tournament_certified_equivalent": 1,
    "tournament_certified_non_equivalent": 1,
    "tournament_unresolved": 2,
}

copycat = profiles["Copycat"]
assert copycat.axes.state_model_status() == "equivalent"
assert copycat.tournament_status == "certified_equivalent"
assert resolver.resolve(copycat.source_id).kind == copycat.expected_resolver_kind
assert copycat.target_id in resolver.resolve(copycat.source_id).target_print_ids

rainbow = profiles["Rainbow Energy"]
assert rainbow.axes.event_semantics == "divergent"
assert rainbow.axes.state_model_status() == "divergent"
assert rainbow.tournament_status == "certified_non_equivalent"
assert resolver.resolve(rainbow.source_id).kind == rainbow.expected_resolver_kind

life_herb = profiles["Life Herb"]
assert life_herb.axes.target_domain == "divergent"
assert life_herb.axes.state_model_status() == "divergent"
assert life_herb.tournament_status == "unresolved"
assert resolver.resolve(life_herb.source_id).kind == life_herb.expected_resolver_kind

pokedex = profiles["Pokédex"]
assert pokedex.axes.material_transition == "equivalent"
assert pokedex.axes.private_observation == "divergent"
assert pokedex.axes.state_model_status() == "divergent"
assert pokedex.tournament_status == "unresolved"
assert resolver.resolve(pokedex.source_id).kind == pokedex.expected_resolver_kind
assert resolver.resolve("base4-115").kind == "semantic_review"

print("reprint equivalence vector regression: PASS")
print(summary["counts"])
