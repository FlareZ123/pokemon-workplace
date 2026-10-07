# Reprint and errata resolution

## Scope

This result builds an auditable evidence ladder for historical prints that share a name with a legal paper Expanded card.

The resolver applies current card semantics before comparing prints. Current semantics currently includes official print-specific errata and the current Pokémon Tool category rule.

## Current partition

The bundled snapshot contains 4,260 historical outside-scope prints whose name also exists on a legal Expanded card.

They currently resolve as:

- 106 exact current-semantic fingerprint candidates;
- 42 historical-official reprint candidates;
- 44 name-wide official-errata candidates;
- 34 known non-equivalent prints;
- 4,034 unresolved semantic-review prints.

The positive high-confidence candidate set contains 192 prints.

For Trainers, 168 historical prints share a name with a legal Expanded Trainer. Exact fingerprints resolve 2, the historical official bridge resolves 41, name-wide errata resolves 44, and the contextual Life Herb witness rules out 2. That gives 87 positive Trainer candidates and 2 known-negative Trainer prints before free-form semantic comparison.

## Evidence ladder

### Exact current-semantic fingerprint

The strongest repository-local structural path requires the historical card and a legal Expanded card to have the same fingerprint after authoritative current-semantics normalization.

There are 106 such historical candidates.

### Historical official reprint evidence

The official 2012 Modified-Legal Reprint List identifies old prints that were legal reprints at that date and marks whether updated reference text was required.

This resolver uses a narrow 42-print bridge. Every included print was marked "Reference Required: No", and a same-name Black & White-onward print had already been released by 2012-03-13. The bridge covers Switch, Poké Ball, Energy Search, Energy Switch, Super Scoop Up, Full Heal, Recycle, and Double Colorless Energy.

### Name-wide official errata

The current TCG Errata resource provides name-wide corrections for historical Trainer cards. Fifteen names are represented in the normalization table, and 44 historical prints across 11 names become candidates through this route.

The affected historical counts are:

| Name | Prints |
| --- | ---: |
| Potion | 16 |
| Rare Candy | 7 |
| PlusPower | 6 |
| Great Ball | 4 |
| Energy Retrieval | 3 |
| Lum Berry | 2 |
| Quick Ball | 2 |
| Hyper Potion | 1 |
| Leftovers | 1 |
| Sitrus Berry | 1 |
| Super Rod | 1 |

### Known non-equivalence

The resolver also records explicit negative evidence.

Thirty historical Special Darkness Energy and Metal Energy prints collide by name with current Basic Energy cards whose mechanics differ.

The Tournament Handbook explicitly says Team Rocket Rainbow Energy number 17 is not functionally identical to the later damage-counter version because damage and damage counters are distinct mechanics. Team Rocket number 80 has the same gameplay fingerprint as number 17, so the negative evidence propagates to that exact duplicate.

Two historical Life Herb printings add a fourth negative name. Their printed text excludes Pokémon-ex targets, while current Life Herb does not, and current Expanded contains a directly legal Pokémon-ex witness. The predicate derivation lives in [../reprint_divergence_predicates/](../reprint_divergence_predicates/).

This yields 34 known non-equivalent historical prints across four names.

## Current-semantics normalization

Print-specific official errata is applied before fingerprinting. The official resource contains 41 exact print records represented in the bundled snapshot, and 24 require a material database overlay.

Legacy Pokémon Tool semantics are normalized as well. Older Tool records can retain Item-era subtype or boilerplate fields even though current rules treat those cards as Pokémon Tools. This prevents stale Item metadata from contaminating search, lock, or reprint analysis.

The composition lives in tools/current_card_semantics.py.

## Resolver states

ReprintResolver.resolve() can return:

1. direct_legal
2. direct_banned
3. outside_disallowed
4. known_non_equivalent
5. exact_fingerprint_candidate
6. historical_official_reprint_candidate
7. official_errata_candidate
8. semantic_review
9. no_expanded_counterpart

Positive candidate states remain separate so downstream code can choose its evidence threshold.

## Boundary cases

- dp4-99 Leftovers resolves through official name-wide errata.
- ex2-88 Rare Candy resolves through official name-wide errata.
- base1-95 Switch resolves through historical official no-reference evidence.
- base1-96 Double Colorless Energy resolves through the same historical bridge.
- gym1-18 Misty resolves by exact current-semantic fingerprint.
- base5-17 and base5-80 Rainbow Energy resolve as known non-equivalent.
- ex5-90 and ex6-93 Life Herb resolve as known non-equivalent because the current format realizes their Pokémon-ex target exclusion.
- old Special Darkness Energy and Metal Energy resolve as known non-equivalent to current Basic cards.
- Copycat wording variants that lack exact or historical bridge evidence remain semantic-review cases.

## Evidence

The Advanced Player's Rulebook says the latest updated card text applies when card text has changed.

The current TCG Errata resource supplies both name-wide and print-specific corrections.

The Tournament Handbook requires identical names and functionally identical text for reprint legality, and gives Copycat and Rainbow Energy as positive and negative examples. The Life Herb predicate result adds a current-format negative witness derived from reachable target scope.

The 2012 Modified-Legal Reprint List supplies exact historical print evidence for the 42-print no-reference bridge.

## Reproduction

Run:

python results/reprint_errata_resolution/reproduce.py

Related regressions:

- results/print_specific_errata_audit/reproduce.py
- results/tool_category_normalization/reproduce.py
- results/historical_reprint_bridge/reproduce.py
- results/reprint_negative_evidence/reproduce.py

## Limitations

The remaining 4,036 semantic-review prints are unresolved. Same-name Pokémon dominate that pool and usually represent genuinely different cards rather than reprints.

Historical reprint evidence is intentionally restricted to no-reference entries with a Black & White-onward bridge already present by the source date. Reference-required entries need separate current-semantics analysis.

The static errata catalogs need maintenance when official resources change.

## Next work

Prioritize the remaining Trainer and Energy semantic-review pool. Build small explicit equivalence rules only where mechanics can be proven stable, and keep positive and negative exemplars in the regression suite.
