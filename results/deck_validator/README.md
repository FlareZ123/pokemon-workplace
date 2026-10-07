# Conservative paper Expanded deck validator

## Question

Can the repository validate a concrete 60-card paper Expanded deck without collapsing exact-print legality, deck-building name identity, and card-specific copy-limit rules into one key?

## Answer

Yes, for the currently represented deck-construction rules. \`tools/deck_validator.py\` validates exact print IDs against the shared effective-legality classifier, aggregates the ordinary copy limit by card name, exempts Basic Energy, requires at least one Basic Pokémon, and applies special copy limits from the selected prints.

The implementation is deliberately conservative. Records whose Expanded legality exists only through set-level fallback produce warnings, and any future copy-limit text that matches the broad deck-constraint pattern but is not recognized produces an explicit warning rather than being silently ignored.

## Rules modeled

The official basic game rules require a 60-card deck, no more than four cards with the same name except Basic Energy, and at least one Basic Pokémon. The bundled Advanced Player's Rulebook independently confirms that the four-copy rule does not apply to Basic Energy and does apply to Special Energy.

The legal Expanded card corpus currently contains 97 print records with explicit \`can't have more than ... in your deck\` copy-limit text, covering five distinct rule texts:

- 53 ACE SPEC prints across the historical and modern wording variants, all sharing a deck-wide maximum of one ACE SPEC;
- 27 Prism Star prints, each limited to one Prism Star card with the same name;
- 16 Radiant Pokémon prints, sharing a deck-wide maximum of one Radiant Pokémon;
- 1 Shining Celebi print with a literal self-name maximum of one.

One additional in-scope but tournament-excluded print, Greninja ★, contains the Pokémon Star deck-wide maximum of one. The validator recognizes that rule family as well even though the corrected legality classifier already rejects that exact print for competitive play.

The corpus audit finds **98** copy-limit-bearing in-scope prints across **6** rule texts before legality filtering and **97** legal prints across **5** rule texts after legality filtering. Every one of those rule texts is recognized by the current validator.

## Exact print and name identity both matter

The validator uses exact print ID for legality and card text, then card name for the ordinary four-copy aggregation. This is necessary because Expanded contains mixed-legality names such as Shaymin-EX, where banned and legal prints share the same deck-building name.

A second, less obvious case is Shining Celebi. The 30th Celebration Classic Collection print \`me55c-106\` says \`You can't have more than 1 Shining Celebi in your deck.\`, while the older legal promo \`smp-SM79\` has no such rule. Therefore a global \`name -> maximum copies\` table would be too coarse: selecting the newer print activates a stricter rule on that deck-building name, while a deck using only the older print remains under the ordinary four-copy rule.

This reinforces the repository's three-layer identity model. Deck validation requires both exact-print properties and name-level aggregation.

## Legality provenance

The validator consumes the shared \`classify_effective_legality()\` function from \`tools/build_expanded_legality_baseline.py\` rather than duplicating ban logic. As a result it inherits the corrected exclusions for seven cards whose own rules text says they cannot be used at official tournaments, along with the maintained official ban overlay.

A legal print whose card-level Expanded field is absent but whose set is Expanded-legal is still accepted under the repository's set fallback, but the validator emits \`set_fallback_legality\` as a warning. This preserves the baseline's remaining 191-record provenance uncertainty instead of turning the fallback into invisible certainty.

## Validation behavior

\`ValidationReport.valid\` is true only when no error issues exist. Warnings do not invalidate the deck.

Errors currently cover:

- wrong total deck size;
- missing Basic Pokémon;
- unknown exact print ID;
- invalid quantities;
- banned or tournament-excluded exact prints;
- more than four non-Basic-Energy cards with the same name, aggregated across print IDs;
- more than one ACE SPEC;
- more than one Radiant Pokémon;
- more than one Prism Star with the same name;
- more than one Pokémon Star;
- literal self-name singleton rules such as the 30th Celebration Shining Celebi.

Warnings currently cover set-level legality fallback and unrecognized future copy-limit text.

## Reproduction and checks

\`results/deck_validator/reproduce.py\` exercises the validator against the bundled snapshot. Regression cases cover:

- unlimited Basic Energy;
- the four-copy limit for Special Energy;
- same-name aggregation across different Ultra Ball prints;
- ACE SPEC, Radiant, Prism Star, and self-named singleton limits;
- two different Prism Star names being allowed together;
- banned versus legal Shaymin-EX prints;
- the newly corrected tournament-excluded Dragapult promo;
- the print-conditional Shining Celebi rule;
- unknown IDs, invalid quantities, deck size, and the Basic-Pokémon requirement;
- full-corpus recognition of every current copy-limit rule text.

The current reproducer passes and asserts exactly 97 legal copy-limit-bearing prints and five recognized legal rule texts.

## Evidence classes

- **Rule fact:** the 60-card, four-same-name, Basic-Energy exception, and Basic-Pokémon requirements come from official Pokémon TCG rules; the Advanced Player's Rulebook supplied in the repository explicitly confirms the Basic versus Special Energy copy-limit distinction.
- **Card-text fact:** ACE SPEC, Prism Star, Radiant, Pokémon Star, and Shining Celebi limits are taken from the bundled exact print records.
- **Computational result:** 98 in-scope / 97 legal copy-limit-bearing print records and complete recognition of their current rule texts come from scanning the bundled 2026-09-16 card snapshot.
- **Methodological judgment:** set-level fallback is accepted with a warning because it remains useful for research but is weaker evidence than an explicit card-level Expanded field.

Official basic-rule reference used for the general deck-building constraints:

- https://assets.pokemon.com/assets/cms2/pdf/trading-card-game/rulebook/swsh10_rulebook_en.pdf

## Limitations

This is a conservative validator for the current local format model rather than a complete tournament deck-list adjudicator.

It does not yet implement official functional-reprint equivalence or errata policy for accepting an older print through a newer functionally equivalent printing. It validates card IDs that are already inside the repository's Expanded-scope set universe and therefore does not attempt to resolve arbitrary historical print submissions outside that index.

The remaining 191 set-fallback records still lack explicit card-level Expanded status. They are surfaced as warnings rather than claimed as fully verified legality.

Future mechanics could introduce a new deck-construction rule whose wording does not match the current broad \`can't have more than ... in your deck\` audit pattern. The validator should therefore be re-audited when the card snapshot changes.

## Next useful work

The strongest extension is an official reprint-equivalence resolver that can answer whether an older exact print is tournament-legal because a functionally equivalent current print exists. That layer should remain separate from deck-building name aggregation and should feed this validator as an explicit resolution step rather than weakening exact-print identity.
