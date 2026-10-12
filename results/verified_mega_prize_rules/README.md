# Mega Evolution ex: duplicated generic two-Prize rule in 45 card records

## Finding

The English card archive stores **45** Mega Evolution ex printings with **two** rule statements:

1. Ordinary `Pokémon ex rule`: the opponent takes 2 Prize cards when an ex is Knocked Out.
2. `Mega Evolution ex Rule`: the opponent takes 3 Prize cards when a Mega Evolution ex is Knocked Out.

The affected records are **33 prints in Ascended Heroes** (`me2pt5`) and **12 prints in Perfect Order** (`me3`). Both rules occur in their structured card database records. The **physical card fronts** examined display only the Mega Evolution three-Prize Rule Box.

Evidence from photographic card fronts:

- [Mega Gardevoir ex, Ascended Heroes #089](https://www.pokeboxusa.com/products/mega-gardevoir-ex-089-217-me-ascended-heroes)
- [Mega Charizard Y ex, Ascended Heroes #022](https://totalcards.net/products/pokemon-mega-evolution-ascended-heroes-mega-charizard-y-ex-022-217)
- [Mega Zygarde ex, Perfect Order #047](https://totalcards.net/collections/pokemon-perfect-order/products/pokemon-mega-evolution-perfect-order-mega-zygarde-ex-047-088)

Uncorrupted Mega Evolution ex prints from `me1`, `me2`, `me4`, and `me5` include only the Mega rule. The attached Advanced Player's Rulebook D-18 illustrates the three-Prize Mega Evolution ex rule. The double-rule records appear to combine a broad class-derived ex rule with the printed Mega-specific rule. No evidence supports awarding five Prizes for one Knock Out.

## Simulation hazard

A naïve rule parser might count the two record entries independently or derive the wrong Prize liability by selecting the first applicable rule. A gameplay-fingerprint routine can also incorrectly distinguish equivalent exact print variants (for example, `me1-60` and `me2pt5-89` Mega Gardevoir ex) by their duplicated textual metadata.

The corrected representation has exactly one applicable **three-Prize** Mega Evolution ex rule. This makes deck legality and card identity consumers agree and prevents downstream double counting. The present result is source correction and test coverage. It does **not** demonstrate an actual Twinleaf engine bug, a changed deck win rate, or complete validation of every physical card image in the affected set.

## Implementation

`tools/verified_mega_prize_rules.py` freezes the 45 audited print IDs and checks their Mega ex name/subtype/supertype and the exact original rule sequence. It removes the extra generic ex rule only on those IDs. An already-corrected print remains unchanged. Unexpected text or identity mutations fail loudly. The raw archive stays untouched.

The guarded operation is now applied in both `tools/current_card_semantics.py` and `tools/deck_validator.py`.

## Reproduce

`python -m results.verified_mega_prize_rules.reproduce`

The regression enumerates all Mega Evolution ex records in the six latest Mega sets, asserts the complete 45-print exact-ID affected set and its distribution, confirms idempotence/source immutability, checks both consumer pipelines, compares Mega Gardevoir exact-print fingerprints, and tests failing identity guards.

Run `.github/workflows/validate-verified-mega-prize-rules.yml` to execute the Windows check together with the earlier verified Stage and Tera bridges, the deck validator, and reprint resolver.

## Limitations and future work

A physical-print check for all 45 artwork variants would further strengthen the audit. Prize-taking execution should also be verified end-to-end inside the active game simulator before claiming the defect affects actual match outcomes. Future datasets may change the affected group; the frozen allowlist deliberately requires review before new IDs are accepted.
