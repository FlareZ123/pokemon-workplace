# Pitch Black stage metadata omissions (card archive QA)

## Finding

The bundled source `resources/cards/en/me5.json` contains at least
two verified gameplay-relevant omissions for cards from the July 2026
Pitch Black expansion:

| ID | Printed card | Recorded fields | Verified correction |
|---|---|---|---|
| `me5-42` | Mankey 42 | `subtypes: null` | `Basic` |
| `me5-115` | Mega Chandelure ex 115 | `subtypes: [MEGA, ex]`; `rules: null` | `Stage 2, MEGA, ex`, plus the Mega Evolution ex three-Prize rule |

**Mankey:** The official Pokémon card catalogue explicitly describes
the Pitch Black 42 printing as a **Basic Pokémon**:
https://www.pokemon.com/uk/pokemon-tcg/pokemon-cards/series/me05/42/

**Mega Chandelure ex:** The archive's `me5-38` and `me5-99`
printings share the exact same card name, 350 HP, Lampent evolution,
types, attacks, Ability, Weakness, Resistance, and Retreat Cost with
`me5-115`. Both are Stage 2 and carry the normal three-Prize
Mega Evolution ex rule. Independent publication metadata for the
special art `me5-115` explicitly identifies it as Stage 2 and
lists the other two print variants:
https://limitlesstcg.com/cards/PBL/115
https://bulbapedia.bulbagarden.net/wiki/Mega_Chandelure_ex_%28Pitch_Black_38%29

After applying those two missing gameplay fields, the three archive
prints of Mega Chandelure ex have identical gameplay fingerprints.

## Operational risk

A stage-based setup policy will fail to recognize the unpatched
Mankey as a legal Basic starting Pokémon. An evolution-search
function requiring `Stage 2` will overlook the special-illustration
Mega Chandelure ex. A rules-based Prize or card-effect parser can
also miss its omitted three-Prize rule.

These outcomes are direct consequences of missing fields in the
dataset. They affect data-driven simulations even though the
real-world printings remain officially playable.

## Implementation

`tools/verified_stage_metadata_repairs.py` provides a strictly
opt-in, idempotent copy-based correction function guarded by exact
card IDs, names, HP and evolution facts. For the Chandelure, it
adds the exact gameplay rule found on the two same-set prints.

`python -m results.pitch_black_stage_metadata.reproduce`

The regression verifies the two real records, preservation of all
unrelated records, idempotence, and fingerprint equivalence across
the three Mega Chandelure ex artworks.

## Scope and status

This audit identifies and proves two source-record omissions. It
does **not** claim there are only two anomalies across the full
20,000-plus-card archive. This patch has not been inserted into
the central `current_card_semantics.py` pipeline because other
agent tools may have differing assumptions about source versus
corrected record provenance. Other researchers can opt into it
or integrate it after reviewing affected regression snapshots.

The official card database and same-set print witnesses provide
strong evidence that the omissions are data errors rather than
intentional print-to-print gameplay differences.
