# Paper Expanded legality baseline

## Question

Can the bundled card database be used directly as a legality oracle for paper Pokémon TCG Expanded research?

## Answer

No. It is a strong search resource, but two distinct gaps matter: seven prints miss later official Expanded bans, and seven additional in-scope records omit an Expanded field even though their own rules text says they cannot be used at official tournaments. Legality also has to be represented at print or functional-variant granularity because a card name can contain both legal and banned versions.

This result adds a reproducible baseline builder at `tools/build_expanded_legality_baseline.py`. It combines the bundled database with a small, auditable overlay for official 2025 and 2026 ban changes that are missing from the snapshot.

## Evidence

Official Play! Pokémon material states that the 2026 Expanded format remains Black & White Series onward and that new expansions become legal two weeks after release. The bundled set metadata covers Expanded-eligible sets from BW Black Star Promos through the September 16, 2026 30th Celebration release.

The bundled database already marks 41 historical banned prints. It still marks the following seven officially banned prints as `expanded: Legal`:

| Card | Print IDs | Effective date | Official announcement |
| --- | --- | --- | --- |
| Flapple with Apple Drop | `swsh2-22`, `swsh45sv-SV013`, `swsh10tg-TG02`, `swshp-SWSH022` | 2025-10-10 | Mega Evolution Banned List and Rule Changes Announcement |
| Medicham V with Yoga Loop | `swsh7-83`, `swsh7-185`, `swsh7-186` | 2026-04-10 | Mega Evolution Perfect Order Banned List and Rule Changes Announcement |

The Chaos Rising announcement reported no further Expanded ban changes. The current Play! Pokémon Rules & Resources page, checked 2026-10-06, lists the Pitch Black rule changes announcement as the latest set-specific rules update. The generated overlay intentionally contains only the specific missing bans directly identified from official announcements.

A separate audit of the 198 records that previously used set-level fallback found seven false positives. Each of these records has no card-level Expanded field, has `unlimited: Banned`, and contains the explicit rules text `(This card cannot be used at official tournaments.)`:

| Print ID | Card |
| --- | --- |
| `swshp-SWSH132` | Dragapult |
| `swshp-SWSH135` | Zacian LV.X |
| `swshp-SWSH136` | Mimikyu δ |
| `swshp-SWSH137` | Light Toxtricity |
| `swshp-SWSH138` | Hydreigon C |
| `swshp-SWSH144` | Greninja ★ |
| `xy12-112` | Imakuni?'s Doduo |

For competitive paper Expanded research, explicit prohibition from official tournaments dominates the set-level fallback.

Sources:

- https://www.pokemon.com/uk/news/2026-pokemon-tcg-standard-format-rotation-announcement
- https://www.pokemon.com/uk/play-pokemon/about/mega-evolution/mega-evolution-banned-list-and-rule-changes-announcement
- https://www.pokemon.com/uk/play-pokemon/about/mega-evolution/mega-evolution-perfect-order-banned-list-and-rule-changes-announcement
- https://www.pokemon.com/us/play-pokemon/about/mega-evolution/mega-evolution-chaos-rising-rule-changes-announcement
- https://www.pokemon.com/us/play-pokemon/about/card-dex/

## Method

The builder reads `resources/sets/en.json` and every JSON file under `resources/cards/en/`. Sets whose metadata says `expanded: Legal` define the candidate format scope. Card-level `expanded: Banned` status takes precedence, followed by the seven missing official bans applied by exact print ID. Records whose own rules text explicitly says they cannot be used at official tournaments are also excluded. Set-level legality fallback is used only after those checks when an in-scope card record omits the card-level Expanded field.

For analysis of reprints, the builder also creates a short gameplay fingerprint from fields that can affect play: name, supertype, subtype, HP, types, evolution origin, Abilities, attacks, rules text, Ancient Trait, Weakness, Resistance, and Retreat Cost. Artwork, rarity, collector number, and image metadata are excluded.

The generated `summary.json` is deterministic for a fixed card database and overlay. The writer uses a file lock and atomic replacement so concurrent research runs do not expose partially written output.

## Results from the bundled 2026-09-16 snapshot

- Expanded-scope print records: **14,884**
- Effectively legal prints after format bans and tournament exclusions: **14,829**
- Banned or tournament-excluded prints: **55**
- Card names with at least one banned print: **32**
- Legal unique names: **3,371**
- Legal distinct gameplay fingerprints: **10,416**
- Prints using set-level legality fallback: **191**
- Database records contradicted by the two official ban updates: **7**
- Set-fallback records excluded by explicit tournament-prohibition text: **7**

Legal print counts by supertype are 12,504 Pokémon, 2,119 Trainers, and 206 Energy cards.

## Important finding: card name is an unsafe legality key

Eleven names contain both legal and banned printings in the bundled Expanded scope after applying the corrected legality classification:

| Name | Banned print IDs | Number of legal same-name prints in the snapshot |
| --- | --- | ---: |
| Archeops | `bw3-67`, `bw5-110` | 6 |
| Dragapult | `swshp-SWSH132` | 12 |
| Flabébé | `sm6-83` | 10 |
| Flapple | `swsh2-22`, `swsh45sv-SV013`, `swsh10tg-TG02`, `swshp-SWSH022` | 4 |
| Marshadow | `sm35-45`, `smp-SM85` | 7 |
| Milotic | `xy2-23` | 10 |
| Mismagius | `sm10-78` | 10 |
| Oranguru | `sm5-114` | 12 |
| Sableye | `bw5-62` | 16 |
| Shaymin-EX | `xy6-77`, `xy6-77a`, `xy6-106` | 4 |
| Unown | `sm8-90`, `sm8-91` | 3 |

This means a deck validator, optimizer, simulator, or search index that stores legality only as `name -> legal/banned` is structurally wrong for Expanded. The minimum safe representation is print-level legality. A stronger future representation should additionally model official functional reprint equivalence, because tournament policy can allow older functionally identical printings of a currently legal card.

## Limitations

The bundled database is external data and can lag official rulings, as demonstrated here. The seven-print overlay repairs two confirmed gaps; it is not a substitute for periodically refreshing the official banned-card list. The fallback audit removes seven explicit tournament-prohibited records, leaving 191 set-fallback records whose missing card-level Expanded fields remain a provenance limitation.

The gameplay fingerprint is a research convenience rather than an official definition of functional identity. Official reprint equivalence can depend on errata and wording interpretation. Any deck-legality tool built on this work should implement the tournament handbook's functional-equivalence rules explicitly before accepting older printings through reprint equivalence.

## Next useful work

The repository now has the three-layer print/variant/name identity model. The next natural extension is a deck validator that consumes the shared legality classifier, aggregates copy limits by deck-building name, and enforces special deck-construction rules such as ACE SPEC, Radiant Pokémon, and Prism Star limits.
