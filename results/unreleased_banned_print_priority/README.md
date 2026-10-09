# Release-before-ban precedence for historical legality queries

## Counterexample

The original dated legality composition evaluated a print's current
database ban before its release date. For Shaymin-EX xy6-77 from
XY Roaring Skies (set release May 6, 2015), a historical query on
January 1, 2014 therefore yielded direct_banned.

Because the bundled database lacks the effective date of this old
ban, the deck adjudicator conservatively converted direct_banned to
unresolved for such historical queries. That is incorrect for
any date before the print's own set release: the print could
not have been used then, independent of when the ban began.

## Correct precedence

For an exact direct Expanded-set print, pre-release dates return
direct_not_yet_released before any banned-status classification.
On released cards, dated ban evidence and any audited tournament
waiting period retain their existing separate treatment.

This is a strict information distinction. The source database's
current banned flag is retained as provenance in the historical
unreleased result, while the disposition uses independently
decisive release evidence.

For xy6-77 specifically:

| Query date | Disposition | Print eligibility |
|---|---|---|
| 2014-01-01 | direct_not_yet_released | ineligible |
| 2016-01-01 | direct_banned, historically undated | unresolved |
| 2026-10-09 | direct_banned | ineligible |

The 2016 result is a conservative evidence limitation rather
than a claim that Shaymin-EX was actually legal in 2016.

## Reproduction

- tools/legality_provenance.py implements precedence.
- results/unreleased_banned_print_priority/reproduce.py verifies
  three boundaries and the complete 2014 deck disposition.
- Existing provenance/deck proof regressions check integration.

The evaluation remains bounded by English snapshot and the
repository's documented date-aware Expanded policy.

## Exhaustive snapshot regression

The corrected release-first priority was checked against all 55
direct Expanded-scope prints currently banned or excluded by
tournament text, queried January 1, 2010, before every
Expanded-set release. All 55 now yield decisive pre-release
ineligibility.

Forty-eight would previously have yielded direct_banned plus an
historically unresolved disposition: 41 database ban flags with
unknown effective dates, and seven explicit tournament-text
exclusions. The remaining seven Flapple and Medicham V exact
prints are official dated ban overlays, so their pre-2025 direct
status is Legal even though the prints are unreleased in 2010.

The new regression checks the entire card set as a corpus
property, with a selected Shaymin-EX three-date case retained.
