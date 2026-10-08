# Computer Search reprint rule-category divergence

## Question

Are the pre-Black & White Computer Search prints functionally identical to the legal Expanded ACE SPEC print?

## Finding

No under the current Standard/Expanded reprint criterion represented by the repository.

The current Tournament Handbook states that an older print can be used through a newer legal reprint when the name is identical and all printed text is functionally identical.

The two historical Computer Search prints audited here are:

- `base1-71`;
- `base4-101`.

Neither historical print is an ACE SPEC, and neither contains an ACE SPEC deck-construction rule.

The legal Expanded target `bw7-137` is an ACE SPEC and contains the explicit rule:

`You can't have more than 1 ACE SPEC card in your deck.`

That rule changes reachable deck configurations. A deck with two Computer Search cards distinguishes the source and target construction semantics.

The difference is therefore classified on the `rule_category` axis.

## Consequence

The two historical Computer Search prints should be known non-equivalent in the current resolver rather than remaining in semantic review.

This conclusion is narrower than saying every subtype difference creates reprint divergence. The witness depends on an explicit printed deck-construction rule whose effect changes legal deck states.

## Reproduction

`tools/reprint_deck_rule_divergence.py` validates the exact source and target identities against the bundled card snapshot, confirms that the target is effectively legal in Expanded, verifies the ACE SPEC subtype and deck rule on the target, and verifies their absence from both historical source prints.

`results/reprint_deck_rule_divergence/reproduce.py` checks the two source IDs and the exact target rule.

## Evidence class

- Tournament-policy fact: current Standard/Expanded reprint eligibility requires identical name plus functionally identical printed text.
- Card-text fact: the bundled target carries the ACE SPEC deck-wide rule and the two historical prints do not.
- Distinguishing witness: two Computer Search cards are permitted by the ordinary same-name four-copy ceiling before considering the target ACE SPEC rule, while the target rule caps the ACE SPEC channel at one.

The official current Tournament Handbook is linked from the Play! Pokémon resources page. The repository already uses that policy source for its reprint-equivalence benchmark.
