# Region-aware semantic card-source resolution

## Question

How should a research pipeline resolve real Japanese Expanded decklists when the bundled card database is an English-language snapshot that omits legal Japanese-only cards?

The resolver should carry source provenance and requested regional scope explicitly. It should also keep naming aliases separate from genuine card-pool absence.

Implementation: `tools/regional_card_source.py`  
Regression: `results/regional_card_source/reproduce.py`

## Resolution states

The resolver returns one of five states for each decklist display name:

- `local_snapshot_exact`: the normalized display name exists in `resources/cards/en/`;
- `local_snapshot_alias`: an explicit audited alias points to a local record;
- `external_region_record`: a provenance-bearing external record exists for the requested region;
- `external_out_of_scope`: an external record exists, but its documented region availability excludes the requested region;
- `missing`: no known semantic source resolves the name.

These are source-resolution states, not tournament-legality verdicts.

A local English record can provide usable card semantics for a Japanese deck analysis without proving that the exact English print itself is a legal Japanese tournament print. Likewise, an external Japanese reference can fill a semantic gap without being promoted into the exact-print identity namespace used by the deck validator.

## External registry

The initial registry contains only the three region-only cards already required by the published Aichi Iron Thorns lists:

| Name | Semantic type | Region in registry | Source |
| --- | --- | --- | --- |
| Palace Book | Trainer / Item | JP | Limitless Japanese card reference |
| Palace Belt | Trainer / Pokemon Tool | JP | Limitless Japanese card reference |
| Player's Ceremony | Trainer / Stadium | JP | Limitless Japanese card reference |

Each record preserves:

- canonical name;
- a human-readable source-print reference;
- supertype and subtype;
- explicit available-region set;
- source URL;
- translated effect;
- translation status, currently `unofficial`.

This is deliberately a small audited registry rather than a fuzzy scraper.

## Aichi regression

The same four published Aichi list dictionaries used elsewhere in the repository are passed through the resolver.

For `region="jp"`:

| List | Local exact copies | Explicit alias copies | External JP copies | Unresolved copies |
| --- | ---: | ---: | ---: | ---: |
| Vileplume Control | 46 | 0 | 0 | 0 |
| Kazuma Iron Thorns | 53 | 0 | 3 | 0 |
| Ryoya Iron Thorns | 52 | 0 | 4 | 0 |
| Kohei Iron Thorns | 52 | 1 | 3 | 0 |

Kohei's one alias copy is `Target Whistle -> Target Whistle Team Flare Gear`.

For `region="international"`, the same three Japanese-only names become `external_out_of_scope`. The unresolved copy counts return to exactly 3, 4, and 3 for Kazuma, Ryoya, and Kohei. The Vileplume list remains fully backed by local snapshot records.

This creates a direct regression for the distinction found by `expanded_region_cardpool_boundary/`: changing only the requested regional scope changes whether the Japanese-only semantic records are admissible.

## Architectural consequence

Card identity and card-source provenance are separate axes.

The repository already distinguishes exact print, conservative variant, official reprint class, and deck name. Regional source resolution belongs upstream of those exchangeability namespaces. A decklist display string first needs a semantic source. Only then should a legality or identity layer decide whether a particular print or equivalence class is admissible for a tournament context.

A useful pipeline is therefore:

`display name -> source resolution -> canonical semantics -> exact/functional identity -> region/date legality -> game-state transitions`

Skipping source resolution can turn a missing database record into false evidence of illegality. Skipping region/date legality can turn semantic coverage into false evidence of tournament legality.

## Limits

The initial external registry is intentionally incomplete. It covers three names because they are directly evidenced by the Aichi lists and current card references.

The resolver does not infer aliases with fuzzy matching.

It does not claim that every local English card has a corresponding legal Japanese printing. Local records are semantic proxies until a legality layer proves the relevant regional print or functional equivalence.

The external translations are marked unofficial and should not override official Japanese card text or rulings.

This result does not implement a full Japanese card database, regional release calendar, or exact-print cross-language identifier map.

## Next work

The strongest extension is an auditable cross-language print map that links a decklist display name to regional print identifiers and release evidence. That would let the exact-print legality layer consume regional sources without collapsing semantic proxies into tournament-legality proof.
