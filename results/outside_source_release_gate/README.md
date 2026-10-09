# Outside-set physical source release is a hard date gate

## Problem and counterexample

A source print outside the set-level paper Expanded scope
may nonetheless have strong semantic equivalence evidence to an
earlier legal Expanded print. The older target's existence does
not mean that the newer *physical printing* existed yet.

The 2021 Celebrations Classic Collection has 25 print records,
including six whose database card-level metadata says
Expanded: Legal even though the set-level scope flag is absent.

The former provenance logic checked the current reprint
resolution for those prints without checking the source set's
release date. Thus a query for a Celebrations Classic physical
print in 2012 could be unresolved under a high-confidence
reprint policy rather than decisively ineligible on release
grounds.

## Formal date precedence

For any source print with set release date t_source and
query date t_query strictly earlier than t_source, the
exact physical print is unavailable at t_query.

The new outside_not_yet_released disposition preserves
the reprint evidence class as metadata and sets its
timing_status to before_set_release. Deck adjudication
marks such prints ineligible independently of what
older same-name target prints existed.

This is source-print release availability; it does not
itself certify ordinary tournament legality on the day
the source set released. That may require an audited
waiting-period calendar and other rules.

## Verified witnesses

- cel25c-113_A Reshiram at 2012-01-01:
  outside_not_yet_released and ineligible despite
  current reprint classification and metadata.
- All 25 Celebrations Classic Collection print IDs
  at 2021-10-07: source unreleased and ineligible.
- The same print at 2021-10-08: release boundary
  has passed; ordinary reprint evidence is evaluated.
- base1-96 Double Colorless Energy at 2012-01-01:
  its 1999 physical source existed and the normal
  strong reprint candidate class remains intact.

## Reproduction

Run python -m results.outside_source_release_gate.reproduce.

The workflow also executes existing legality provenance,
deck adjudication, and outside-set metadata audits.

Scope: exact source-print release dates from the supplied
English set metadata. It does not infer region-specific
release dates or full historical promotional calendars.
