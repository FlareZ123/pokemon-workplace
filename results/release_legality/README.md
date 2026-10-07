# Date-aware product release legality

## Question

Can the repository strengthen the legality provenance of the 191 30th Celebration prints that currently rely on set-level Expanded metadata by applying the 2026 product-legality timing policy to an audited product-release anchor?

## Result

Yes, for release timing.

The 2026 product-legality update says Pokémon TCG products become tournament legal two weeks after the relevant product release anchor. For sets without the ordinary sleeved-booster path, the update uses the Elite Trainer Box or Booster Bundle release as the timing anchor. Pokémon's 30th Celebration launch coverage gives September 16, 2026 as the worldwide expansion release, and the official product showcase lists the 30th Celebration Elite Trainer Box as available on September 16.

That makes the audited ordinary tournament-legality date **September 30, 2026**.

The local card snapshot has exactly **191** legal prints still classified through `set_fallback`, all in the two 30th Celebration set records:

| Set | Fallback prints | Product anchor | Ordinary legality date |
| --- | ---: | --- | --- |
| `me55` 30th Celebration | 161 | 2026-09-16 | 2026-09-30 |
| `me55c` Classic Collection | 30 | 2026-09-16 | 2026-09-30 |

At the repository audit date of **October 7, 2026**, all 191 are past the ordinary release waiting period.

This strengthens the release-timing evidence for those prints. It does not manufacture missing card-level legality metadata, and it does not replace ban, card-text restriction, region, or reprint-equivalence checks.

## Immediate functional-reprint exception

The Q2 2026 tournament update separately allows functional reprints of released cards to become tournament legal when obtained, including during a prerelease window.

The tool therefore also computes a deliberately conservative lower bound: target prints whose raw repository gameplay fingerprint exactly matches an effectively legal Expanded print released at least 14 days before the 30th Celebration anchor.

Five target prints satisfy that strict local test:

| New print | Name | Set |
| --- | --- | --- |
| `me55-126` | Poké Pad | 30th Celebration |
| `me55-127` | Switch | 30th Celebration |
| `me55c-101` | N | Classic Collection |
| `me55c-50` | Raikou | Classic Collection |
| `me55c-203` | Magikarp | Classic Collection |

These five are **candidate evidence**, not an official ruling. Exact local fingerprints are intentionally stricter than the tournament handbook's semantic functional-equivalence standard. Ultra Ball is a useful example of why the count is a lower bound: wording and formatting changes can prevent exact fingerprint equality even when two prints may be functionally equivalent under tournament policy.

## Method

`tools/release_legality.py` stores product-release anchors separately from card identity.

For each audited set it records:

- expansion name and set IDs;
- product anchor date;
- anchor type;
- waiting period;
- ordinary legality date;
- source URLs.

`release_status()` then evaluates an explicit `as_of` date. The 30th Celebration audit also reuses the shared effective-legality classifier to identify the 191 set-fallback prints and the shared gameplay fingerprint for the conservative immediate-reprint candidate scan.

The prior-print scan only considers effectively legal Expanded prints from sets released at least 14 days before September 16. This avoids crediting a just-released predecessor as automatically tournament-ready without a separate product schedule.

## Evidence classes

**Official policy evidence.** The 2026 Pokémon TCG Product Legality Update describes the two-week product-anchor policy.

**Official product evidence.** Pokémon's 30th Celebration launch article and product showcase identify September 16, 2026 as the expansion launch and list the Elite Trainer Box as available that day.

**Database evidence.** The bundled snapshot marks `me55` and `me55c` Expanded-legal at set level while all 191 contained records lack card-level Expanded fields.

**Derived timing result.** September 16 plus 14 days is September 30.

**Computational result.** Exactly five target prints have a strict raw gameplay-fingerprint match to an older effectively legal Expanded print under the conservative prior cutoff.

## Sources

- 2026 Pokémon TCG Product Legality Update: https://community.pokemon.com/en-us/discussion/22216/pokemon-tcg-product-legality-update
- 30th Celebration launch: https://www.pokemon.com/us/news/the-pokemon-tcg-30th-celebration-expansion-is-available-now
- 30th Celebration product showcase: https://www.pokemon.com/us/news/pokemon-tcg-30th-celebration-product-showcase
- 2026 Expanded-format announcement: https://www.pokemon.com/uk/news/2026-pokemon-tcg-standard-format-rotation-announcement

## Limitations

This result contains one audited product anchor, not a complete historical release calendar.

The product update describes anchor products rather than assigning a date to every set ID in the local database. Mapping both `me55` and `me55c` to the same 30th Celebration launch is justified by the snapshot and product packaging, but remains an explicit repository mapping.

Product-date eligibility alone does not prove that a print is usable. Current bans, card-specific official-tournament exclusions, regional availability, errata, and functional-reprint semantics remain separate legality dimensions.

The five immediate-reprint candidates are a lower bound from exact local fingerprints. They should not be promoted into an automatic functional-reprint acceptance path without the repository's stronger semantic evidence layers.

## Next work

Build a broader audited product calendar for 2025-2026 sets and promotional releases. The key design should remain evidence-bearing: each set or promo family should carry its source, product anchor, region, and legality date rather than deriving tournament legality from `releaseDate + 14` as a universal rule.
