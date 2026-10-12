# Current-handbook positive reprint evidence

## Question

Can the resolver turn the Tournament Handbook's explicit Copycat example into present-day positive reprint evidence without broad free-form text normalization?

## Result

Yes.

The current Tournament Handbook identifies Copycat `ex7-83` and `sm7-127` as functionally identical despite their wording difference. The bundled archive contains two more prints, `ecard1-138` and `ex15-73`, that share the certified source print's fingerprint. Two additional prints, `col1-77` and `hgss1-90`, use the expression “draw a number of cards equal to” rather than “count the number ... and draw that many”. Their count, shuffle, and draw transitions coincide; `tools/copycat_number_wording.py` applies that narrowly verified normalization before fingerprinting.

The positive-evidence layer therefore resolves exactly five historical prints:

- `ecard1-138`;
- `ex15-73`;
- `ex7-83`;
- `col1-77`;
- `hgss1-90`.

All three point to the explicitly certified legal target `sm7-127`.

The two count-wording forms now have explicit source-ID, name, Supporter-classification, and exact-rule guards. Their equivalence is a narrow, testable semantic inference; the Tournament Handbook directly certifies only `ex7-83` against `sm7-127`.

## Method

`tools/reprint_positive_evidence.py` uses a deliberately narrow transitive rule:

1. take the official positive source `ex7-83`;
2. verify the official target `sm7-127` is directly legal in the current paper Expanded model;
3. compute the current-semantic fingerprint of `ex7-83`;
4. admit only historical same-name prints with that exact source fingerprint after the two guarded count-wording normalizations.

If an old print is semantically identical under the repository fingerprint to a source that official current policy says is functionally identical to a legal target, the same legal target is valid for that exact duplicate.

## Resolver integration

The central resolver adds the state:

`official_semantic_candidate`

This state is checked after explicit negative evidence and before generic fingerprint or historical evidence routes. Positive and negative evidence sets are checked for overlap when the resolver is built.

The separation preserves provenance. A Copycat accepted through an explicit current-handbook semantic example remains distinguishable from an exact current-text match, an old historical bridge, or a name-wide erratum.

## Evidence

**Current tournament-policy evidence.** The repository semantic benchmark transcribes the Tournament Handbook's Copycat positive example as `ex7-83` / `sm7-127`.

**Repository card-text evidence.** `ecard1-138`, `ex15-73`, and `ex7-83` share one exact current-semantic fingerprint.

**Conservative inference.** Evidence propagates across the certified source fingerprint and the two audited count-wording synonyms, without generalizing to other cards.

## Reproduction

Run:

`python results/reprint_positive_evidence/reproduce.py`

Expected output class:

- 5 official semantic candidate prints;
- 1 name, Copycat;
- explicit legal target `sm7-127`.

## Next work

Use the same evidence-first pattern for other positive semantic families. Rule-backed transformations should remain small enough to explain exactly which textual difference they erase and why current game rules make that difference immaterial.
