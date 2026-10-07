# Audited combat-data override layer

## Question

How should a simulator handle a card-database combat field that conflicts with independent current card references?

Preserve the raw resource and apply a narrow, provenance-carrying override above it.

Implementation: tools/combat_data_overrides.py
Regression: results/combat_data_overrides/reproduce.py

## Murkrow me55-93

The bundled record for 30th Celebration Murkrow me55-93 says:

- Weakness: Lightning x2
- Resistance: Fighting x2

The Resistance entry is inconsistent with multiple current references for the same 093/128 card.

References checked on 2026-10-07:

- Serebii 30th Celebration #93: Fighting Resistance -30
  https://www.serebii.net/card/30thcelebration/093.shtml
- New Realm Games 093/128 listing: Fighting Resistance -30
  https://newrealmgames.com/products/murkrow-093-128-common-holofoil
- Out of Games 30th Celebration Murkrow: Fighting Resistance -30
  https://outof.games/realms/pokemon-tcg/cards/30th-celebration/murkrow-100019027/
- Collector's Edge 093/128 listing: Fighting Resistance -30
  https://collectorsedge.co.uk/products/pokemon-30th-celebration-murkrow-093-128-holofoil

Several Scrydex-derived or similarly structured sites repeat the x2 value, so agreement among those records is not treated as independent confirmation.

The override layer changes only me55-93's Resistance to Fighting -30.

## Uxie me55c-43

The bundled Classic Collection Uxie carries Psychic Weakness +20. This looks unusual in the modern card pool but is consistent with the historical Uxie card being reprinted and with current references for the Classic Collection print.

No override is applied.

This distinction matters: unusual data should not be normalized away merely because it is uncommon. The correct action depends on whether independent evidence supports the unusual value.

## Design

The raw resources remain untouched.

apply_combat_data_overrides(card) returns a deep-copied mapping and applies only fields listed in COMBAT_DATA_OVERRIDES. The overlay stores a reason and source URLs alongside each correction.

This mirrors the repository's existing legality-overlay pattern and keeps source discrepancies auditable.

## Confidence and limits

The Murkrow correction is high-confidence based on several mutually consistent current references, but this result does not claim a first-party Pokemon card-database citation was found. If a stronger primary source becomes available, it should replace or strengthen the provenance.

The override layer currently contains one card. It should remain narrow. A discrepancy should be added only after card-specific verification rather than through broad heuristic cleanup.
