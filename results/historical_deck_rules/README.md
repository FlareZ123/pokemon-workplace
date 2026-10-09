# Historical deck-construction rules and Arceus reprint divergence

## Findings

The bundled snapshot contains 15 historical Arceus / Arceus LV.X prints
with the explicit rule "You may have as many of this card in your deck as
you like." The ordinary four-card name cap therefore needs an exact-print
exception. A historical Arceus LV.X-only deck still needs a Basic Pokémon.

Another 26 pre-Black & White Unown prints say "You may have up to 4 Basic
Pokémon cards in your deck with Unown in their names." This restricts a
family of different printed names together, provided at least one such
rule-bearing print is included in the construction. Two Unown [A] and
three Unown [B] exceed the family cap while satisfying ordinary per-name
limits.

Ten of the unlimited-rule Arceus prints share their name with three
Expanded-legal XY promo Arceus prints, none of which has the unlimited
rule. The historical source IDs are dpp-DP50 and pl4-AR1 through
pl4-AR9. The targets are xyp-XY83, xyp-XY116, and xyp-XY197.

Five copies of a historical rule-bearing Arceus print can be constructed
under that printed exception. Five copies of one of the later Expanded
Arceus prints violate the ordinary same-name four-copy ceiling. This is a
deck-rule distinguishing witness independent of attack text. The ten
historical prints consequently become known non-equivalent reprint
candidates under the current all-printed-text functional-equivalence
standard represented in the existing repository policy evidence.

Five historical Arceus LV.X prints also carry an unlimited-copy rule but
have no current legal Expanded same-name target in the snapshot. These
construction semantics do not imply paper Expanded legality for those
historical cards.

## Reproducibility and consequences

Run: python -m results.historical_deck_rules.reproduce

The new standalone collector lives in
tools/arceus_unlimited_reprint_divergence.py and is integrated into
tools/reprint_negative_evidence.py. The construction changes live in
tools/deck_validator.py. Tests cover source text population counts,
ordinary versus exceptional copy limits, a mixed-name Unown witness,
and the resolver transition.

The known-negative same-name historical pool grows from 67 to 77 prints
and from 21 to 22 names. The unresolved semantic-review pool falls from
3,974 to 3,964 prints, with the total review population unchanged at 4,260.

The report distinguishes exact printed deck rules, a derived
construction witness, and current format eligibility. Regional and
non-Arceus historical reprint rulings remain separate research topics.

## Mixed-era, stage-sensitive Unown proof

A historical rule-bearing Unown [A] (neo2-14) plus four Unown V
(swsh12-65) fails the family rule even though the names differ:
Unown V is a Basic Pokémon with Unown in its name. Replacing the
four Unown V with four Unown VSTAR (swsh12-66) avoids the
Basic-Pokémon-specific family cap, because VSTAR is an Evolution
subtype. Four Unown V alone also passes the card-text family test,
since that historical restriction is not in the submitted deck.

These are **hypothetical historical construction** witnesses, not
paper Expanded legal deck recommendations: neo2-14 is an outside-scope
print with no independently established current reprint eligibility.
