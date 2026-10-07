from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from energy_disruption_text_catalog import (
    catalog_energy_disruption_texts,
    text_summary,
)


rows = catalog_energy_disruption_texts(ROOT / "resources")
assert rows
assert len({
    (row.card_id, row.source_kind, row.source_name, row.text)
    for row in rows
}) == len(rows)

known_names = {row.name for row in rows}
assert "Crushing Hammer" in known_names or "Enhanced Hammer" in known_names

summary = text_summary(rows)
print(summary)
