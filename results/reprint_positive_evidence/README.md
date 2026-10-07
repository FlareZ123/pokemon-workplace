# Current-handbook positive reprint evidence

## Question

Can the resolver turn the Tournament Handbook's explicit Copycat example into present-day positive reprint evidence without broad free-form text normalization?

## Result

Yes.

The current Tournament Handbook identifies Copycat `ex7-83` and `sm7-127` as functionally identical despite their wording difference. The bundled archive also contains two other historical Copycat prints, `ecard1-138` and `ex15-73`, whose current-semantic fingerprints are exactly identical to the certified source print `ex7-83`.

The positive-evidence layer therefore resolves exactly three historical prints:

- `ecard1-138`;
- `ex15-73`;
- `ex7-83`.

All three point to the explicitly certified legal target `sm7-127`.

The two other pre-Black & White Copycat wording forms, `hgss1-90` and `col1-77`, remain in semantic review. Their effects appear closely related, but this result does not infer equivalence from that similarity.

## Method

`tools/reprint_positive_evidence.py` uses a deliberately narrow transitive rule:

1. take the official positive source `ex7-83`;
2. verify the official target `sm7-127` is directly legal in the current paper Expanded model;
3. compute the current-semantic fingerprint of `ex7-83`;
4. admit only historical same-name prints with that exact source fingerprint.

If an old print is semantically identical under the repository fingerprint to a source that official current policy says is functionally identical to a legal target, the same legal target is valid for that exact duplicate.

## Resolver integration

The central resolver adds the state:

`official_semantic_candidate`

This state is checked after explicit negative evidence and before generic fingerprint or historical evidence routes. Positive and negative evidence sets are checked for overlap when the resolver is built.

The separation preserves provenance. A Copycat accepted through an explicit current-handbook semantic example remains distinguishable from an exact current-text match, an old historical bridge, or a name-wide erratum.

## Evidence

**Current tournament-policy evidence.** The repository semantic benchmark transcribes the Tournament Handbook's Copycat positive example as `ex7-83` / `sm7-127`.

**Repository card-text evidence.** `ecard1-138`, `ex15-73`, and `ex7-83` share one exact current-semantic fingerprint.

**Conservative inference.** The evidence propagates only across that exact source fingerprint. The other historical Copycat wording class remains unresolved.

## Reproduction

Run:

`python results/reprint_positive_evidence/reproduce.py`

Expected output class:

- 3 official semantic candidate prints;
- 1 name, Copycat;
- explicit legal target `sm7-127`.

## Next work

Use the same evidence-first pattern for other positive semantic families. Rule-backed transformations should remain small enough to explain exactly which textual difference they erase and why current game rules make that difference immaterial.
