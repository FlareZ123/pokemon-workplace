# Set-level Expanded legality fallback audit

## Question

After correcting the seven explicit tournament-prohibited false positives, what uncertainty remains in the repository's set-level Expanded legality fallback?

## Result

The remaining fallback is sharply localized. As of the bundled 2026-09-16 snapshot, all **191** legal prints whose card-level record omits an Expanded field come from exactly two sets:

| Set | Bundled release date | Fallback prints |
| --- | --- | ---: |
| 30th Celebration (\`me55\`) | 2026-09-16 | 161 |
| 30th Celebration: Classic Collection (\`me55c\`) | 2026-09-16 | 30 |

Both set records explicitly mark Expanded as Legal. In the live repository snapshot, all 191 card records omit card-level legality metadata entirely, including Unlimited. The separate legality classifier has already removed records whose own card text says they cannot be used at official tournaments.

This is materially stronger provenance than the previous picture of 198 unexplained fallback records spread across an unknown part of the card pool. It still remains fallback evidence rather than explicit per-print Expanded metadata.

## Release-timing context

Official Pokémon guidance for the 2026 season states that Expanded remains Black & White onward and that new expansions become legal for tournament play two weeks after release.

Using the bundled set metadata only as a timing cross-check, both remaining fallback sets have a 2026-09-16 release date, so a simple two-week offset is 2026-09-30. On the audit date 2026-10-07, every remaining fallback print is therefore past that nominal date.

This calculation is **not** used as a universal legality rule. The 2026 Tournament Handbook added a dedicated staggered-release schedule, promotional cards have their own legality status resource, and later 2026 guidance changed the immediate legality of functional reprints. A robust validator therefore needs an explicit date-aware product legality layer rather than assuming every database set's \`releaseDate + 14 days\` is authoritative.

Official references:

- https://www.pokemon.com/uk/news/2026-pokemon-tcg-standard-format-rotation-announcement
- https://www.pokemon.com/uk/pokemon-news/play-pokemon-rules-and-resources-updated-for-q1-2026
- https://www.pokemon.com/fr/actualites/mise-a-jour-des-regles-play-pokemon-du-deuxieme-trimestre-2026
- https://play.pokemon.com/en-gb/resources/documents/?filter=all

## Method

\`tools/audit_set_fallback_legality.py\` loads the same Expanded-scope set universe as the baseline and calls the shared \`classify_effective_legality()\` function for every card. It selects only cards classified as legal through \`set_fallback\`, then reports their set, bundled release date, a nominal 14-day timing cross-check, Unlimited status, and rules-text presence.

The tool accepts an explicit \`--as-of YYYY-MM-DD\` date so historical audits can avoid accidentally substituting the machine's current date.

\`results/set_fallback_legality_audit/reproduce.py\` fixes the audit date at 2026-10-07 and asserts the exact 161/30 split, the two 2026-09-30 nominal dates, and Unlimited legality for all 191 records.

## Interpretation

**Database fact:** all 191 remaining fallback records are confined to the two 30th Celebration set files.

**Rule fact:** official 2026 guidance keeps Expanded at Black & White onward and applies a two-week expansion legality delay in general.

**Derived timing check:** 2026-09-16 plus 14 days is 2026-09-30.

**Methodological judgment:** this localization makes the fallback substantially easier to audit and reason about. It does not turn a missing card-level Expanded field into first-class evidence.

## Limitations

The card database is a snapshot. Product legality can depend on an official release schedule, staggered releases, promo-specific dates, bans, card-specific restrictions, and functional-reprint rules that are not represented by a simple set date.

The audit also does not claim that \`Unlimited: Legal\` implies Expanded legality. That field is reported only as corroborating metadata after format scope and the shared legality classifier have been applied.

## Next work

Two legality layers remain especially valuable:

1. A date-aware release-legality model grounded in the official product and promo schedules rather than a generic set-date offset.
2. A conservative functional-reprint resolver for section 4.1.3 of the current Tournament Handbook, preserving cases where wording differs while the effect remains functionally identical.
