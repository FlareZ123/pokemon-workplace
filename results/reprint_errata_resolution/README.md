# Reprint and errata resolution

## Scope

This result builds an auditable evidence ladder for historical prints that share a name with a legal paper Expanded card.

The resolver applies current card semantics before comparing prints. Current semantics now includes official print-specific errata, the current Pokémon Tool category rule, exact generic Item/Supporter category-boilerplate normalization, and narrow rules-grounded Fisherman/Life Herb wording normalization.

## Current partition

The bundled snapshot contains 4,260 historical outside-scope prints whose name also exists on a legal Expanded card.

They currently resolve as:

- 126 exact current-semantic fingerprint candidates;
- 39 historical-official reprint candidates;
- 44 name-wide official-errata candidates;
- 3 current-handbook semantic candidates;
- 67 known non-equivalent prints;
- 3,981 unresolved semantic-review prints.

The positive high-confidence candidate set contains 212 prints.

For Trainers, 168 historical prints share a name with a legal Expanded Trainer. Exact fingerprints resolve 22, the historical official bridge remains the active route for 38, name-wide errata resolves 44, the current Copycat example resolves 3, and the contextual Life Herb witness rules out 2. The explicit historical Trainer name-reuse audit adds 16 more known-negative Trainer prints. That gives 107 positive Trainer candidates and 35 known-negative Trainer prints before broader semantic comparison.

## Evidence ladder

### Exact current-semantic fingerprint

The strongest repository-local structural path requires the historical card and a legal Expanded card to have the same fingerprint after authoritative current-semantics normalization.

There are 126 such historical candidates.

### Historical official reprint evidence

The official 2012 Modified-Legal Reprint List identifies old prints that were legal reprints at that date and marks whether updated reference text was required.

This resolver preserves a narrow 42-print historical evidence set. Every included print was marked "Reference Required: No", and a same-name Black & White-onward print had already been released by 2012-03-13. After current-semantics normalization, three of those prints now resolve earlier as exact fingerprints, so 39 still use the historical-official resolver state. The evidence set covers Switch, Poké Ball, Energy Search, Energy Switch, Super Scoop Up, Full Heal, Recycle, and Double Colorless Energy.

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

### Current-handbook semantic equivalence

The Tournament Handbook explicitly identifies Copycat `ex7-83` and `sm7-127` as functionally identical despite their wording difference.

The repository propagates that evidence only to historical Copycat prints with exactly the same current-semantic fingerprint as `ex7-83`. This admits `ecard1-138`, `ex15-73`, and `ex7-83`, each pointing to the certified legal target `sm7-127`.

Other historical Copycat wording forms remain in semantic review.

### Known non-equivalence

The resolver also records explicit negative evidence.

Thirty historical Special Darkness Energy and Metal Energy prints collide by name with current Basic Energy cards whose mechanics differ.

The Tournament Handbook explicitly says Team Rocket Rainbow Energy number 17 is not functionally identical to the later damage-counter version because damage and damage counters are distinct mechanics. Team Rocket number 80 has the same gameplay fingerprint as number 17, so the negative evidence propagates to that exact duplicate.

Two historical Life Herb printings add a fourth negative name. Their printed text excludes Pokémon-ex targets, while current Life Herb does not, and current Expanded contains a directly legal Pokémon-ex witness. The predicate derivation lives in [../reprint_divergence_predicates/](../reprint_divergence_predicates/).

The dedicated Trainer name-reuse audit adds 16 more source prints across Master Ball, Pokémon Breeder, Pokémon Center, Max Revive, Revive, Devolution Spray, Power Plant, and Magnetic Storm. Each family has a direct distinguishing game-state witness. A further optionality audit proves six old PokéNav, Pokégear 3.0, and Dusk Ball prints non-equivalent because their mandatory `choose` wording differs from current optional `you may` semantics. A separate semantic-review audit adds eight more prints across Apricorn Maker, Pokémon Fan Club, Super Potion, and TV Reporter using explicit target-domain, destination-zone, healing-amount, and empty-deck playability witnesses. Friend Ball adds one further target-domain negative: official Restored Pokémon rules make Expanded-legal Restored Archen searchable by the current generic Pokémon wording but outside the historical Baby/Basic/Evolution target classes. Computer Search contributes two further rule-category negatives because the legal Expanded print is an ACE SPEC with a one-ACE-SPEC deck rule while the historical prints lack that rule. This yields 67 known non-equivalent historical prints across 21 names.

## Current-semantics normalization

Print-specific official errata is applied before fingerprinting. The official resource contains 41 exact print records represented in the bundled snapshot, and 24 require a material database overlay.

Legacy Pokémon Tool semantics are normalized as well. Older Tool records can retain Item-era subtype or boilerplate fields even though current rules treat those cards as Pokémon Tools. This prevents stale Item metadata from contaminating search, lock, or reprint analysis.

Generic Item and Supporter category reminders are also removed by exact-string normalization. The audit found six newly exact historical candidates and zero known-negative collisions. Three were already covered by the historical bridge, while `hgss1-93` Full Heal, `hgss1-95` Poké Ball, and `hgss2-78` Judge move out of semantic review. A further rules-grounded layer normalizes exact historical Fisherman public-discard wording and the no-exclusion six-counter Life Herb wording. That adds four exact candidates: `ecard3-125`, `hgss1-92`, `pl1-108`, and `hgss2-79`. The composition lives in `tools/current_card_semantics.py`.

## Resolver states

ReprintResolver.resolve() can return:

1. direct_legal
2. direct_banned
3. outside_disallowed
4. known_non_equivalent
5. official_semantic_candidate
6. exact_fingerprint_candidate
7. historical_official_reprint_candidate
8. official_errata_candidate
9. semantic_review
10. no_expanded_counterpart

Positive candidate states remain separate so downstream code can choose its evidence threshold.

## Boundary cases

- dp4-99 Leftovers resolves through official name-wide errata.
- ex2-88 Rare Candy resolves through official name-wide errata.
- base1-95 Switch resolves through historical official no-reference evidence.
- dp1-110, dp5-85, and pl1-113 Poké Ball belong to the historical evidence set but now resolve earlier by exact current-semantic fingerprint.
- hgss1-93 Full Heal, hgss1-95 Poké Ball, and hgss2-78 Judge become exact candidates after generic Trainer boilerplate normalization.
- ecard3-125 and hgss1-92 Fisherman become exact candidates after current numbered-effect and public-discard semantics are applied.
- pl1-108 and hgss2-79 Life Herb become exact candidates after six damage counters are normalized to 60 healing; the Pokémon-ex-excluding ex5-90 and ex6-93 remain negative.
- hgss1-94 Moomoo Milk becomes an exact candidate after three damage counters per heads are normalized to 30 healing per heads.
- ex6-100 and pl3-140 VS Seeker become exact candidates after public discard-pile reveal/search wording is normalized to current retrieval semantics.
- four historical Bill's Maintenance prints become exact candidates because current Supporter playability rules eliminate the apparent empty-hand no-op branch.
- ecard3-140 and pl2-97 Underground Expedition become exact candidates after equivalent bottom-four selection wording is normalized with current numbered-choice rules.
- pl4-88 Lucky Egg becomes an exact candidate after legacy Tool reminder text and equivalent When/If Knock Out trigger wording are normalized under current rules.
- base1-96 Double Colorless Energy resolves through the same historical bridge.
- gym1-18 Misty resolves by exact current-semantic fingerprint.
- base5-17 and base5-80 Rainbow Energy resolve as known non-equivalent.
- ex5-90 and ex6-93 Life Herb resolve as known non-equivalent because the current format realizes their Pokémon-ex target exclusion.
- old Special Darkness Energy and Metal Energy resolve as known non-equivalent to current Basic cards.
- base1-71 and base4-101 Computer Search are known non-equivalent because the current Expanded print is an ACE SPEC with an explicit deck-construction restriction absent from the historical prints.
- ecard3-121 Apricorn Maker is known non-equivalent because historical Trainer-card targeting can reach Ball Guy while current Apricorn Maker is Item-only.
- ecard3-126 Friend Ball is known non-equivalent because current generic Pokémon targeting can reach Restored Pokémon while the historical Baby/Basic/Evolution classes cannot.
- ecard2-130 and pop4-9 Pokémon Fan Club are known non-equivalent because they put searched Basics directly onto the Bench rather than into hand.
- base1-90 and base4-117 Super Potion are known non-equivalent because they heal at most 40 damage rather than 60.
- ex15-82, ex3-88, and pop2-11 TV Reporter are known non-equivalent because they lack the current empty-deck play prohibition.
- ecard1-138, ex15-73, and ex7-83 Copycat resolve through the current-handbook semantic example; hgss1-90 and col1-77 remain semantic-review cases.

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
- results/reprint_positive_evidence/reproduce.py
- results/reprint_divergence_predicates/reproduce.py
- results/trainer_name_reuse_divergence/reproduce.py
- results/trainer_optionality_divergence/reproduce.py
- results/trainer_semantic_divergence/reproduce.py
- results/trainer_boilerplate_normalization/reproduce.py
- results/trainer_boilerplate_candidate_audit/reproduce.py

## Limitations

The remaining 3,981 semantic-review prints are unresolved. Same-name Pokémon dominate that pool and usually represent genuinely different cards rather than reprints.

Historical reprint evidence is intentionally restricted to no-reference entries with a Black & White-onward bridge already present by the source date. Reference-required entries need separate current-semantics analysis.

The static errata catalogs need maintenance when official resources change.

## Next work

Keep rules-grounded promotions narrow. The official benchmark now leaves only the two older Pokédex rows unresolved; those should be treated as an information-state question because "up to 5" changes how much hidden deck information the player must observe. Broader semantic-review work should continue to preserve positive and negative exemplars.
