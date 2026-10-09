"""Audit source-backed physical card identity on a revealed Quick Ball search."""

from pathlib import Path
import runpy
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from card_identity import build_identity_index
from card_class_namespace import CardClassNamespace
from identity_materialization import CardInstance
from trusted_print_reveal import validate_materialized_print
from revealed_target_identity import public_reveal_label

index = build_identity_index(ROOT / "resources")

old = index.prints_by_id["xy1-42"]
new = index.prints_by_id["swsh7-49"]
assert old.name == new.name == "Pikachu"
assert old.effective_status == new.effective_status == "Legal"
assert old.variant_id != new.variant_id

old_instance = CardInstance(
    "searched-old", "exact_print:xy1-42", "Pikachu", "hand"
)
new_instance = CardInstance(
    "searched-new", "exact_print:swsh7-49", "Pikachu", "hand"
)
assert validate_materialized_print(old_instance, index) == "xy1-42"
assert validate_materialized_print(new_instance, index) == "swsh7-49"
assert public_reveal_label(
    old_instance, CardClassNamespace.DECK_NAME
) == "Pikachu"
assert public_reveal_label(
    old_instance, CardClassNamespace.EXACT_PRINT
) == "xy1-42"

# Source mismatch: a caller cannot attach another Pokémon's name to a genuine
# Pikachu print ID and have it treated as a verified physical public reveal.
wrong_name = CardInstance(
    "wrong-name", "exact_print:xy1-42", "Porygon", "hand"
)
try:
    validate_materialized_print(wrong_name, index)
except ValueError as exc:
    assert "name disagrees" in str(exc)
else:
    raise AssertionError("materialized print/name disagreement accepted")

try:
    validate_materialized_print(
        CardInstance("missing-print", "exact_print:unknown-id", "A", "hand"),
        index,
    )
except ValueError as exc:
    assert "unknown Expanded-scope" in str(exc)
else:
    raise AssertionError("nonexistent Expanded print accepted")

banned = next(
    record for record in index.prints_by_id.values()
    if record.effective_status == "Banned"
)
banned_instance = CardInstance(
    "banned-instance",
    f"exact_print:{banned.card_id}",
    banned.name,
    "hand",
)
try:
    validate_materialized_print(banned_instance, index)
except ValueError as exc:
    assert "not legal" in str(exc)
else:
    raise AssertionError("effectively banned print accepted")
assert validate_materialized_print(
    banned_instance, index, require_legal=False
) == banned.card_id

# Reuse the full previous physical/latent Quick Ball regression. This time
# supply the authoritative index before Bayesian observer update.
shared = runpy.run_path(str(
    ROOT / "results" / "revealed_search_coarse_physical_bridge" / "reproduce.py"
))
run = shared["run"]
result = run("Pikachu", print_identity_index=index)
searched = result.exact_transaction.physical_after.ledger.instance(
    "searched-old-print"
)
assert searched.card_class == "exact_print:xy1-42"
assert validate_materialized_print(searched, index) == "xy1-42"

try:
    run(
        "Pikachu", print_identity_index=index,
        material_name="Porygon",
    )
except ValueError as exc:
    assert "name disagrees" in str(exc)
else:
    raise AssertionError("source-invalid physical target bypassed bridge")

print("source-backed legal Pikachu prints validated in exact identity catalog")
print("fake source print, wrong name and effectively banned print rejected")
print("exact physical Quick Ball and coarsened observer bridge verified")
