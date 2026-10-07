# Errata-aware reprint candidates

## Question

How much of the semantic reprint gap can be reduced using official policy evidence before attempting general natural-language equivalence?

## Official evidence used

The current Pokémon TCG Errata page states that its listed text reflects corrections to cards rather than their original printed wording. Its major name-level changes include Trainer cards such as Rare Candy, Great Ball, Quick Ball, Potion, Super Rod, and several others.

Source:
https://play.pokemon.com/fr-ca/resources/documents/tcg-errata/

The Tournament Handbook's reprint section supplies two especially useful worked examples:

- Copycat (Celestial Storm 127) and Copycat (Team Rocket Returns 83) are functionally equivalent despite wording differences.
- Rainbow Energy (Celestial Storm 151) and Rainbow Energy (Team Rocket 17) are not functionally equivalent because placing a damage counter and doing 10 damage are distinct mechanics.

Current handbook access:
https://play.pokemon.com/en-gb/resources/documents/?filter=all

The repository stores these narrowly scoped facts in \`tools/reprint_policy_evidence.py\` rather than attempting to scrape policy at runtime.

## Result

\`tools/errata_reprint_candidates.py\` combines the live card corpus with that policy evidence.

### Name-level errata bridge

Eleven names from the current major errata list have pre-Expanded prints in the corpus while also having a legal Expanded print:

| Name | Outside-direct-scope prints |
| --- | ---: |
| Potion | 16 |
| Rare Candy | 7 |
| PlusPower | 6 |
| Great Ball | 4 |
| Energy Retrieval | 3 |
| Quick Ball | 2 |
| Lum Berry | 2 |
| Leftovers | 1 |
| Hyper Potion | 1 |
| Sitrus Berry | 1 |
| Super Rod | 1 |

That is **44** pre-Expanded Trainer prints whose current game text is materially informed by official name-level errata. None of these were discovered by the exact-fingerprint bridge because their historical database text or subtype representation differs from modern prints.

### Handbook positive example lifted to its old fingerprint class

The explicit Copycat example connects old fingerprint \`ex7-83\` to legal Expanded print \`sm7-127\`.

Three outside-direct-scope prints share the old Copycat fingerprint:

- \`ecard1-138\`
- \`ex15-73\`
- \`ex7-83\`

The first two are a conservative variant-level inference from the worked example: they have exactly the same local gameplay fingerprint as the handbook's old Copycat print.

### Handbook negative example lifted to its old fingerprint class

The explicit Rainbow Energy counterexample identifies \`base5-17\` as functionally different from \`sm7-151\`.

Two outside-direct-scope prints share that old Rainbow Energy fingerprint:

- \`base5-17\`
- \`base5-80\`

This negative class is important because it shows why a same-name resolver must preserve semantic distinctions even when the historical wording looks superficially close.

## Combined coverage

The errata bridge contributes 44 outside-scope prints and the positive Copycat fingerprint class contributes 3 more, for **47 semantic-policy candidates** beyond the 100 exact-fingerprint candidates in \`reprint_equivalence_candidates/\`.

These 47 prints should still be understood as evidence-backed candidates until a full resolver specifies how official errata, current printed wording, card categories, and reprint policy compose. The result narrows the semantic problem without pretending that every same-name card is equivalent.

## Method

\`tools/reprint_policy_evidence.py\` preserves:

- the two handbook worked-example relations;
- the 15 names listed under the current official major name-level errata section;
- source URLs and the errata page's current \`2024-11-07\` last-update field.

\`tools/errata_reprint_candidates.py\` then:

1. builds the effective direct Expanded pool;
2. finds outside-scope prints whose names are covered by major errata and have a legal Expanded same-name target;
3. expands the Copycat and Rainbow Energy worked examples across prints with the same conservative fingerprint as the cited older print;
4. excludes source prints explicitly marked tournament-prohibited or Unlimited-banned.

\`results/errata_reprint_candidates/reproduce.py\` asserts the live snapshot counts and exact Copycat/Rainbow fingerprint-class memberships.

## Evidence classes

- **Official rule example:** the Copycat and Rainbow Energy relations come from the Tournament Handbook.
- **Official errata fact:** the major-name list and corrected-card status come from the current Pokémon TCG Errata page.
- **Computational result:** 44 errata candidates, 3 Copycat-class positive candidates, and 2 Rainbow-class negative examples come from the live repository corpus.
- **Inference:** extending a cited print relation to other prints with the identical conservative fingerprint is a repository modeling step, not an additional official ruling.

## Limitations

The major errata list is not a complete semantic reprint map. Some functional reprints differ only in wording and have no name-level erratum because no correction was required.

Specific-print errata also exists. Those corrections may affect equivalence for individual historical Pokémon or Trainer printings and are not yet incorporated into the candidate resolver.

The current official errata page served in 2026 still reports a last update of November 7, 2024. Any future update should trigger a refresh of this static evidence catalog.

## Next work

A stronger resolver should normalize Trainer and Energy effects into a semantic representation, then validate that representation against:

- the positive Copycat pair;
- the negative Rainbow Energy pair;
- the major errata names;
- specific-print errata where applicable.

That would provide a testable bridge between raw card text and official functional equivalence.
