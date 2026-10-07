# Official print-specific errata audit

## Question

How much of the official Pokémon TCG print-specific errata is already reflected in the bundled card database, and where would raw database fields misrepresent card semantics in paper Expanded research?

## Result

The current official TCG Errata resource lists **41 exact English print records** under its print-specific correction section. Every one of those print IDs exists in the bundled snapshot.

A targeted semantic audit finds **24 records whose gameplay fingerprint still changes when the official correction is applied**:

- **12 historical pre-Black & White prints**, relevant when evaluating reprint equivalence;
- **12 prints already inside the Expanded set universe**, relevant to direct card execution and state modeling.

The remaining 17 records are already semantically reflected by the database for the corrected point, or the official correction is metadata-only for the fields used here.

Applying the 24 material overlays does **not** change the current count of exact historical reprint candidates. The raw and normalized scans both produce **106** exact-fingerprint candidates. The main value of this layer is semantic correctness of exact prints, including legal Expanded prints, rather than immediate expansion of the reprint candidate set.

## Expanded prints that require a material overlay

The 12 in-scope records are:

- Fighting Stadium, xy3-90
- Jamming Net Team Flare Hyper Gear, xy4-98
- Shield Energy, xy5-143
- Galvantula, xy11-42
- Electrode, xy12-40
- Venusaur & Snivy-GX, sm12-1
- Venusaur & Snivy-GX, sm12-210
- Venusaur & Snivy-GX, sm12-249
- Venusaur & Snivy-GX, smp-SM229
- Cinderace, swsh1-36
- Minior, sv4-99
- Minior, sv4-201

Several differences are mechanically important. Shield Energy's official correction changes both attachment scope and damage-reduction timing. Galvantula's Double Thread is restricted to Benched targets. Electrode's Buzzap Thunder can attach to any Pokémon. Shining Vine and Far-Flying Meteor are repeatable triggers instead of once-per-turn effects. Cinderace has a one-Energy Retreat Cost.

## Historical prints that require a material overlay

The 12 pre-Black & White records are:

- Alakazam, dp2-2
- Glalie, dp2-25
- Blastoise, dp3-2
- Wormadam Sandy Cloak, dp3-42
- Gengar, dp7-18
- Roserade, dp7-23
- Skuntank, dp7-26
- Staraptor, dp7-27
- Shaymin LV.X, pl1-126
- Lucky Egg, pl4-88
- Defender, hgss3-72
- Unown, hgss4-51

These corrections matter whenever an older print is compared with a legal Black & White-onward counterpart. For example, Gengar's Fainting Spell must Knock Out the Attacking Pokémon, while the raw database text says the Defending Pokémon. Blastoise's Waterlog may attach Basic Energy generally, while the raw database restricts it to Basic Water Energy.

## Tooling

tools/official_print_errata.py provides:

- a 41-print catalog tied to the official errata resource;
- exact print identity checks against the bundled database;
- a pure normalize_print_specific_errata() function;
- a reproducible summary that separates raw and normalized gameplay fingerprints;
- a reprint-candidate comparison before and after normalization.

The normalizer only changes fields for the 24 material cases identified above. It leaves the other 17 entries unchanged because the database already captures the relevant semantics or because the correction is outside the gameplay fields represented by the current fingerprint.

## Evidence classes

**Official rule fact.** The Advanced Player's Rulebook states that when card text has been updated, the latest version of the effect must be applied.

**Official errata evidence.** The Play! Pokémon TCG Errata resource, last updated November 7, 2024, lists the exact print-specific corrections used by this audit.

**Computational result.** The bundled snapshot contains all 41 referenced prints. Twenty-four produce a changed gameplay fingerprint under the targeted official overlay, split 12 historical and 12 Expanded-scope records.

**Computational result.** Legal Expanded distinct gameplay fingerprints remain 10,416 before and after this print-specific normalization. Historical exact reprint candidates remain 106 before and after normalization.

**Methodological judgment.** Official errata should be applied before raw card text is used as simulator semantics or as input to semantic reprint comparison.

## Reproduction

Run:

python results/print_specific_errata_audit/reproduce.py

The regression checks the 41-print catalog, all identity mappings, the 24 material overlays, the 12/12 scope split, several high-risk corrected fields, and the unchanged 106 exact-candidate count.

## Source

- Official TCG Errata: https://play.pokemon.com/en-us/resources/documents/tcg-errata/
- Repository rule reference: resources/advanced-players-rulebook.md, section II-A, About Card Text

## Limitations

This is a targeted official-overlay layer, not a free-form semantic parser. A no-overlay entry means the database already captures the corrected gameplay point closely enough for the current fingerprint model, or the official correction is metadata-only. It does not imply byte-for-byte text identity with the official wording.

The global Pokémon Tool category change is broader than a print-specific correction and remains a separate normalization problem. Some old Tool records still contain legacy Item boilerplate in their raw rules fields even though current rules treat those cards as Pokémon Tools.

## Next work

The strongest continuation is to normalize the global historical Pokémon Tool category rule before semantic reprint comparison. That should remove legacy Item boilerplate from gameplay identity where current rules supersede it, while preserving genuine Tool-specific effects.
