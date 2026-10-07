# Expanded is region-sensitive: Aichi decklists exceed the English snapshot

## Question

Can the repository's bundled English card snapshot resolve every card name in the published 2026 Aichi Open League lists already used by the research?

No.

The mismatch has two different causes:

1. one ordinary English card is stored under a longer database name than the tournament-list display name;
2. three Japanese promotional cards used in Aichi are absent from the English snapshot because they were not released internationally.

Implementation: `tools/aichi_card_name_resolution.py`  
Regression: `results/expanded_region_cardpool_boundary/reproduce.py`

## Local database audit

The audit uses the published-list count dictionaries already preserved in `tools/aichi_setup_inference.py` and every JSON record under `resources/cards/en/`.

It applies only one typography normalization before lookup:

`♢ -> ◇`

That resolves the Prism Star naming difference already present in the repository.

### Exact and alias-resolved gaps

| Published list | Exact-name mismatches | Alias-resolved | Still absent after aliasing | Absent copies |
| --- | --- | --- | --- | ---: |
| Aichi runner-up Vileplume | none | none | none | 0 |
| Kazuma Iron Thorns | Palace Book, Palace Belt, Player's Ceremony | none | all 3 | 3 |
| Ryoya Iron Thorns | Palace Book, Player's Ceremony | none | both | 4 |
| Kohei Iron Thorns | Target Whistle, Palace Belt, Player's Ceremony | Target Whistle | Palace Belt, Player's Ceremony | 3 |

The Kohei mismatch is a namespace issue. The bundled database contains `xy4-106` under the name `Target Whistle Team Flare Gear`, while the tournament transcript calls it `Target Whistle`. The local record is an Item, and an explicit alias resolves it without changing card identity.

The other three names are genuinely absent from the bundled English snapshot.

## Regional card-pool boundary

Current Limitless card references identify the missing cards as Japanese-only or internationally unreleased prints:

- Palace Belt, BW-P #153, is a Trainer Tool and is legal in Expanded (JP) while not legal in international Expanded: <https://limitlesstcg.com/cards/jp?display=classic&q=%21set%3ABWP+is%3Aunreleased&translate=en>
- Palace Book is a Trainer Item, appears in Japanese XY-P / SM-P promotional sets, and is legal in Expanded (JP) while not legal in international Expanded: <https://limitlesstcg.com/cards/jp/XYP/NAN83?translate=en>
- Player's Ceremony is a Trainer Stadium, has Japanese SM-P / S-P prints, and is legal in Expanded (JP) while not legal in international Expanded: <https://limitlesstcg.com/cards/jp/SP/127?translate=en>

These are the same kinds of cards that appear in the Aichi lists used elsewhere in the repository.

The local audit itself does not depend on those external legality labels. It only proves that the names cannot be resolved from `resources/cards/en/`. The regional interpretation is supported by the published Japanese tournament lists plus the current card references.

## Finding 1: "paper Expanded" is not one universal card pool

A Japanese Expanded tournament can contain cards that do not exist in the international English card pool.

That means a format state should include at least a regional card-pool dimension when research mixes:

- Japanese Expanded tournament lists;
- an English card database;
- international legality assumptions.

Without that dimension, a validator can incorrectly classify a real Japanese deck as malformed or illegal even when its list is faithfully transcribed.

For the three Aichi Iron Thorns lists, the English snapshot lacks:

- 3 of 60 slots for Kazuma;
- 4 of 60 slots for Ryoya;
- 3 of 60 slots for Kohei after resolving the Target Whistle alias.

## Finding 2: alias failure and card-pool absence must remain separate

`Target Whistle -> Target Whistle Team Flare Gear` is a resolvable naming mismatch.

Palace Belt, Palace Book, and Player's Ceremony require actual additional card records or an explicitly external regional-card source.

A fuzzy name matcher should not blur these cases together. Otherwise it can silently treat a missing card as though it were merely spelled differently.

A robust ingestion pipeline should therefore return distinct outcomes such as:

- exact match;
- explicit alias match;
- absent from this database snapshot;
- ambiguous match.

## Finding 3: list-dependent coverage can hide the problem

The Aichi Vileplume list used by the ALS research resolves completely against the English snapshot.

The Iron Thorns lists do not.

A few successful real-list analyses therefore do not validate database completeness for the event or region. Coverage needs to be checked per input list, especially before legality or card-type compilation.

## Validation

The regression loads the repository card JSON directly and asserts:

- every Vileplume non-Basic name resolves after Prism-symbol normalization;
- the exact missing-name sets for Kazuma, Ryoya, and Kohei;
- the exact unresolved copy counts;
- the explicit Target Whistle alias;
- the aliased local Target Whistle record has Item subtype.

No fuzzy matching is used.

## Consequences for existing research

The new G&H side-payload result classifies Palace Belt as a Tool using an external Japanese-card reference because that card cannot be typed from the bundled English snapshot.

More generally, research using Japanese Expanded lists should avoid assuming that failure to find a card in `resources/cards/en/` means the list is invalid or the card is outside the event's legal pool.

This also strengthens the repository's existing card-identity work: decklist display names, exact database names, print identities, gameplay identities, and regional legality are separate namespaces.

## Limits

The result audits four published lists already encoded in the repository.

It is not a complete census of Japanese-only Expanded cards.

The explicit Target Whistle alias is deliberately narrow. A production resolver needs an auditable alias table or source-backed identifier mapping rather than heuristic suffix stripping.

The external card references are used to characterize the regional boundary; they are not copied into the local database by this result.

## Next useful work

Build a regional card-source layer that can augment the English snapshot with Japanese-only records while retaining provenance and region-specific legality.

A smaller intermediate step is to audit every published Aichi list in the repository and measure exact/alias/missing coverage before any simulator consumes it.
