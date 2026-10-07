"""Region-aware semantic card-source resolution.

This module resolves decklist display names to either the bundled English
snapshot or a small, provenance-bearing external reference registry. It is a
source-coverage layer, not a tournament-legality oracle.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Literal

from tools.aichi_card_name_resolution import ALIASES, load_card_names, normalize_display_name

Region = Literal["international", "jp"]


class ResolutionKind(str, Enum):
    LOCAL_SNAPSHOT_EXACT = "local_snapshot_exact"
    LOCAL_SNAPSHOT_ALIAS = "local_snapshot_alias"
    EXTERNAL_REGION_RECORD = "external_region_record"
    EXTERNAL_OUT_OF_SCOPE = "external_out_of_scope"
    MISSING = "missing"


@dataclass(frozen=True)
class ExternalCardRecord:
    canonical_name: str
    source_print: str
    supertype: str
    subtypes: tuple[str, ...]
    available_regions: frozenset[Region]
    source_url: str
    translated_effect: str
    translation_status: Literal["unofficial"]

    def available_in(self, region: Region) -> bool:
        return region in self.available_regions


@dataclass(frozen=True)
class NameResolution:
    input_name: str
    normalized_name: str
    canonical_name: str | None
    kind: ResolutionKind
    region: Region
    local_print_count: int = 0
    external_record: ExternalCardRecord | None = None

    @property
    def has_semantic_source(self) -> bool:
        return self.kind in {
            ResolutionKind.LOCAL_SNAPSHOT_EXACT,
            ResolutionKind.LOCAL_SNAPSHOT_ALIAS,
            ResolutionKind.EXTERNAL_REGION_RECORD,
        }

    @property
    def region_scoped_external(self) -> bool:
        return self.kind == ResolutionKind.EXTERNAL_REGION_RECORD


DEFAULT_EXTERNAL_RECORDS: tuple[ExternalCardRecord, ...] = (
    ExternalCardRecord(
        canonical_name="Palace Book",
        source_print="XY-P promo reference",
        supertype="Trainer",
        subtypes=("Item",),
        available_regions=frozenset({"jp"}),
        source_url="https://limitlesstcg.com/cards/jp/XYP/NAN83?translate=en",
        translated_effect="Draw 3 cards. Your turn ends.",
        translation_status="unofficial",
    ),
    ExternalCardRecord(
        canonical_name="Palace Belt",
        source_print="BW-P 153",
        supertype="Trainer",
        subtypes=("Pokémon Tool",),
        available_regions=frozenset({"jp"}),
        source_url="https://limitlesstcg.com/cards/jp/BWP/153?translate=en",
        translated_effect=(
            "If the Pokémon this card is attached to is your Active Pokémon, "
            "draw 2 cards instead of 1 at the beginning of your turn."
        ),
        translation_status="unofficial",
    ),
    ExternalCardRecord(
        canonical_name="Player's Ceremony",
        source_print="S-P 127 reference",
        supertype="Trainer",
        subtypes=("Stadium",),
        available_regions=frozenset({"jp"}),
        source_url="https://limitlesstcg.com/cards/jp/SP/127?translate=en",
        translated_effect=(
            "Once during each player's turn, that player may draw 2 cards. "
            "If they do, their turn ends."
        ),
        translation_status="unofficial",
    ),
)


@dataclass(frozen=True)
class DeckResolutionSummary:
    region: Region
    resolutions: tuple[tuple[NameResolution, int], ...]

    def copies_by_kind(self) -> dict[str, int]:
        totals = {kind.value: 0 for kind in ResolutionKind}
        for resolution, copies in self.resolutions:
            totals[resolution.kind.value] += copies
        return totals

    @property
    def semantically_sourced_copies(self) -> int:
        return sum(
            copies
            for resolution, copies in self.resolutions
            if resolution.has_semantic_source
        )

    @property
    def unresolved_copies(self) -> int:
        return sum(
            copies
            for resolution, copies in self.resolutions
            if not resolution.has_semantic_source
        )


class RegionalCardSource:
    def __init__(
        self,
        local_cards_by_name: dict[str, tuple[dict, ...]],
        *,
        external_records: tuple[ExternalCardRecord, ...] = DEFAULT_EXTERNAL_RECORDS,
        aliases: dict[str, str] | None = None,
    ) -> None:
        self._local_cards_by_name = local_cards_by_name
        self._aliases = dict(ALIASES if aliases is None else aliases)

        external_by_name: dict[str, ExternalCardRecord] = {}
        for record in external_records:
            if record.canonical_name in external_by_name:
                raise ValueError(
                    f"duplicate external canonical name: {record.canonical_name}"
                )
            external_by_name[record.canonical_name] = record
        self._external_by_name = external_by_name

    @classmethod
    def from_cards_dir(
        cls,
        cards_dir: Path,
        *,
        external_records: tuple[ExternalCardRecord, ...] = DEFAULT_EXTERNAL_RECORDS,
        aliases: dict[str, str] | None = None,
    ) -> "RegionalCardSource":
        return cls(
            load_card_names(cards_dir),
            external_records=external_records,
            aliases=aliases,
        )

    def resolve_name(self, display_name: str, *, region: Region) -> NameResolution:
        normalized = normalize_display_name(display_name)
        local = self._local_cards_by_name.get(normalized)
        if local is not None:
            return NameResolution(
                input_name=display_name,
                normalized_name=normalized,
                canonical_name=normalized,
                kind=ResolutionKind.LOCAL_SNAPSHOT_EXACT,
                region=region,
                local_print_count=len(local),
            )

        alias = self._aliases.get(display_name)
        if alias is not None:
            alias_local = self._local_cards_by_name.get(alias)
            if alias_local is not None:
                return NameResolution(
                    input_name=display_name,
                    normalized_name=normalized,
                    canonical_name=alias,
                    kind=ResolutionKind.LOCAL_SNAPSHOT_ALIAS,
                    region=region,
                    local_print_count=len(alias_local),
                )

        external = self._external_by_name.get(normalized)
        if external is not None:
            kind = (
                ResolutionKind.EXTERNAL_REGION_RECORD
                if external.available_in(region)
                else ResolutionKind.EXTERNAL_OUT_OF_SCOPE
            )
            return NameResolution(
                input_name=display_name,
                normalized_name=normalized,
                canonical_name=external.canonical_name,
                kind=kind,
                region=region,
                external_record=external,
            )

        return NameResolution(
            input_name=display_name,
            normalized_name=normalized,
            canonical_name=None,
            kind=ResolutionKind.MISSING,
            region=region,
        )

    def resolve_counts(
        self,
        counts: dict[str, int],
        *,
        region: Region,
    ) -> DeckResolutionSummary:
        rows = []
        for name, copies in sorted(counts.items()):
            if copies <= 0:
                raise ValueError(f"{name} has nonpositive count {copies}")
            rows.append((self.resolve_name(name, region=region), copies))
        return DeckResolutionSummary(region=region, resolutions=tuple(rows))
