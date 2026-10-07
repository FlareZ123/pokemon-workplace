# Conservative reprint-equivalence candidates

## Question

How much paper Expanded legality is missed if repository tools only accept exact print IDs from sets already marked Expanded-legal?

## Tournament-rule context

Section 4.1.3 of the Pokémon TCG Tournament Handbook is the relevant rule. The long-standing rule allows an older version when the new and old cards have the same name and their printed text is functionally identical. The handbook's worked examples explicitly treat Copycat (CES 127) and Copycat (TRR 83) as equivalent despite wording changes, while distinguishing two Rainbow Energy wordings because damage and damage counters are different mechanics.

Official 2026 rules updates matter here:

- the Q1 2026 update says section 4.1.3 was clarified regarding which cards can be used under the reprint rule;
- the Q2 2026 update says functional reprints of released cards become tournament-legal upon obtaining the card, including during an expansion's Prerelease window.

Current official resource page:
https://play.pokemon.com/en-gb/resources/documents/?filter=all

Official update references:
https://www.pokemon.com/uk/pokemon-news/play-pokemon-rules-and-resources-updated-for-q1-2026
https://www.pokemon.com/fr/actualites/mise-a-jour-des-regles-play-pokemon-du-deuxieme-trimestre-2026

The current official handbook download is linked from the resource page. This result deliberately avoids turning a local text-equality heuristic into an official legality oracle.

## Exact-fingerprint scan

\`tools/reprint_equivalence_candidates.py\` scans every print in the bundled database, then builds the set of effectively legal Expanded variants using the shared legality classifier.

For cards outside the database's Expanded-set universe, it reports an **exact gameplay-fingerprint candidate** when the existing conservative fingerprint is identical to at least one legal Expanded print. It excludes source cards whose own rules text prohibits official-tournament use or whose Unlimited status is explicitly Banned.

Snapshot result:

- **100** outside-scope printings are exact-fingerprint candidates;
- they form **16** gameplay fingerprints and **16** card names;
- **91** are Energy cards;
- **9** are Pokémon;
- no Trainer card survives the exact fingerprint requirement.

The 16 names are:

- the eight pre-Fairy Basic Energy types represented in the snapshot;
- Double Colorless Energy;
- Magikarp;
- Mewtwo-EX;
- Reshiram;
- Surfing Pikachu;
- Tapu Lele-GX;
- Xerneas-EX;
- Zekrom.

Several of the Pokémon candidates come from special reprint products such as the 25th Anniversary Classic Collection, whose set metadata does not itself define the normal Expanded-set universe even though the printed card can be a functional reprint of an Expanded card.

## Exact equality is too narrow

The scanner also finds **4,248** outside-scope prints across **636** names that merely share a name with at least one legal Expanded card. This is a review pool rather than a legality list.

The handbook's Copycat example demonstrates why a semantic layer is necessary:

- \`sm7-127\` Copycat and \`ex7-83\` Copycat have the same name;
- the local gameplay fingerprints differ because their Supporter reminder wording and effect wording differ;
- the handbook nevertheless uses those printings as an example of functional equivalence because the described game effect is unchanged.

This is a direct counterexample to the proposition that exact structured-text equality is necessary for legal reprint equivalence.

The reverse failure also matters. Same name alone is nowhere near sufficient: the review pool contains thousands of Pokémon whose attacks, HP, typing, or other text differ.

## Modeling consequence

A useful reprint resolver should therefore have at least three states:

1. **Direct format print:** exact print is already in the effective Expanded pool.
2. **Conservative reprint candidate:** exact gameplay fingerprint matches a legal Expanded variant.
3. **Semantic review required:** name matches a legal Expanded card but exact fingerprint does not.

The second category is strong evidence for equivalence within the local data model, but it remains a candidate unless the tournament rule and any applicable errata have been checked. The third category cannot be automated safely by card name.

This is why \`tools/deck_validator.py\` currently rejects outside-scope print IDs rather than silently accepting the 100 candidates. Automatic acceptance should wait for a dedicated rule/errata resolver.

## Reproduction

\`results/reprint_equivalence_candidates/reproduce.py\` asserts the current snapshot counts:

- 100 exact candidates;
- 16 exact candidate variants;
- 16 exact candidate names;
- 4,248 same-name review prints;
- 636 same-name review names;
- exact-candidate supertype split of 91 Energy / 9 Pokémon.

It also loads the two Copycat print records and asserts that their gameplay fingerprints differ, preserving the handbook example as a regression against over-reliance on exact fingerprint identity.

## Evidence classes

- **Rule fact:** functional reprints can bridge otherwise non-current printings when the tournament-handbook criteria are satisfied.
- **Official 2026 update:** functional reprints receive special immediate-legality treatment, including prerelease acquisition after the Q2 update.
- **Computational result:** 100 exact candidates and the 4,248-print same-name review pool are deterministic results from the bundled snapshot.
- **Methodological judgment:** exact gameplay fingerprint is useful as a conservative candidate generator and insufficient as a complete official-equivalence resolver.

## Limitations

The current fingerprint is intentionally conservative and database-dependent. It can miss wording-only equivalence, errata, historical type/subtype representation changes, and other semantics the tournament rules may treat as equivalent.

This scan also does not decide whether an older card has an applicable official erratum. The current TCG Errata resource should be incorporated into any automatic acceptance path.

## Next work

The highest-value next layer is an errata-aware semantic resolver. A first version can focus on Trainer and Energy cards, where reprint equivalence is common and game-text normalization is more tractable, while retaining explicit manual review for ambiguous pairs.
