"""Regression for region-aware semantic card-source resolution."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.aichi_setup_inference import (
    KAZUMA_IRON_NONBASIC_COUNTS,
    KOHEI_IRON_NONBASIC_COUNTS,
    RYOYA_IRON_NONBASIC_COUNTS,
    VILEPLUME_NONBASIC_COUNTS,
)
from tools.regional_card_source import (
    RegionalCardSource,
    ResolutionKind,
)


def main() -> None:
    source = RegionalCardSource.from_cards_dir(ROOT / "resources" / "cards" / "en")

    expected_jp = {
        "Kazuma": (KAZUMA_IRON_NONBASIC_COUNTS, 53, 0, 3),
        "Ryoya": (RYOYA_IRON_NONBASIC_COUNTS, 52, 0, 4),
        "Kohei": (KOHEI_IRON_NONBASIC_COUNTS, 52, 1, 3),
    }
    for label, (counts, exact, alias, external) in expected_jp.items():
        result = source.resolve_counts(counts, region="jp")
        kinds = result.copies_by_kind()
        assert result.unresolved_copies == 0
        assert result.semantically_sourced_copies == 56
        assert kinds[ResolutionKind.LOCAL_SNAPSHOT_EXACT.value] == exact
        assert kinds[ResolutionKind.LOCAL_SNAPSHOT_ALIAS.value] == alias
        assert kinds[ResolutionKind.EXTERNAL_REGION_RECORD.value] == external
        assert kinds[ResolutionKind.EXTERNAL_OUT_OF_SCOPE.value] == 0
        assert kinds[ResolutionKind.MISSING.value] == 0
        print(label, "JP", kinds)

    expected_international = {
        "Kazuma": (KAZUMA_IRON_NONBASIC_COUNTS, 3),
        "Ryoya": (RYOYA_IRON_NONBASIC_COUNTS, 4),
        "Kohei": (KOHEI_IRON_NONBASIC_COUNTS, 3),
    }
    for label, (counts, unavailable) in expected_international.items():
        result = source.resolve_counts(counts, region="international")
        kinds = result.copies_by_kind()
        assert result.unresolved_copies == unavailable
        assert kinds[ResolutionKind.EXTERNAL_OUT_OF_SCOPE.value] == unavailable
        assert kinds[ResolutionKind.EXTERNAL_REGION_RECORD.value] == 0
        assert kinds[ResolutionKind.MISSING.value] == 0
        print(label, "international", kinds)

    vileplume = source.resolve_counts(VILEPLUME_NONBASIC_COUNTS, region="jp")
    assert vileplume.unresolved_copies == 0
    assert vileplume.copies_by_kind()[ResolutionKind.LOCAL_SNAPSHOT_EXACT.value] == 46

    target = source.resolve_name("Target Whistle", region="jp")
    assert target.kind == ResolutionKind.LOCAL_SNAPSHOT_ALIAS
    assert target.canonical_name == "Target Whistle Team Flare Gear"

    book_jp = source.resolve_name("Palace Book", region="jp")
    assert book_jp.kind == ResolutionKind.EXTERNAL_REGION_RECORD
    assert book_jp.external_record is not None
    assert book_jp.external_record.subtypes == ("Item",)
    assert book_jp.external_record.translation_status == "unofficial"

    book_international = source.resolve_name("Palace Book", region="international")
    assert book_international.kind == ResolutionKind.EXTERNAL_OUT_OF_SCOPE
    assert not book_international.has_semantic_source

    unknown = source.resolve_name("Definitely Missing Card", region="jp")
    assert unknown.kind == ResolutionKind.MISSING
    assert unknown.canonical_name is None

    print("regional card source: PASS")


if __name__ == "__main__":
    main()
