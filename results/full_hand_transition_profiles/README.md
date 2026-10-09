# Unified typed full-hand transition profiles

## Objective

Earlier results represented 15 canonical literal full-hand discard-and-draw families, and a later [return-destination catalog](../hand_destination_reset_geometry/README.md) identified 65 shuffle-back or bottom-deck text variants. This compiler unifies their card-text transitions while preserving materially different timing, targeting and action budgets.

Implementation: `tools/compile_full_hand_transition_profiles.py`. Regression: `results/full_hand_transition_profiles/reproduce.py`.

## Snapshot results

Current local English card snapshot and the repository's print-level Expanded legality gate produce:

| Hand disposition | Typed variants | Candidate print records |
| --- | ---: | ---: |
| Discard entire old hand | 15 | 80 |
| Shuffle entire old hand into deck | 59 | 128 |
| Shuffle entire old hand to deck bottom | 6 | 19 |
| **Combined** | **80** | **227** |

There are no repeated print IDs between the two source catalogs in the current snapshot. The return catalog deliberately retains text variants as separate entries; the discard catalog uses its prior canonical family grouping.

Across 80 typed variants:

- **34 Supporters, 33 attacks, 11 Abilities, 1 Stadium effect, 1 Item**.
- **40 fixed-count redraw profiles**, while **40 retain card-text-dependent draw semantics** pending a richer effect compiler.
- **37 turn-ending transitions**, including every attack and specific non-attack effects.
- **34 Supporter-budget consumers**, **3 GX-attack users**, and **1 VSTAR Power user**.

The fixed-count classifier is intentionally conservative. Text with conditional draw amounts, multiple draw quantities, coin results, opponent-relative counts, or ambiguous clauses remains uncompiled, with complete local effect text attached to the profile.

## Representative typed distinctions

| Source | Hand destination | Important additional constraint |
| --- | --- | --- |
| Dedenne-GX, Dedechange | discard_all | Pokémon played from hand to Bench, requiring space |
| Ingo & Emmet | discard_all | draw five from top or bottom; Supporter window |
| Cynthia | shuffle_into_deck | fixed six-card redraw; Supporter window |
| Judge | shuffle_into_deck | effects on both players, four-card draw |
| N | shuffle_into_deck | both players; remaining-Prize-dependent draw |
| Iono | bottom_deck | both players; remaining-Prize-dependent draw |
| Marnie | bottom_deck | both players; asymmetric draws |
| Kingdra | bottom_deck | in-play Ability, selected player |
| Thievul | bottom_deck | when-played-to-evolve Ability trigger |
| Jubilife Village | shuffle_into_deck | Stadium effect active during a player's turn; that turn ends |
| Venomoth-GX | shuffle_into_deck | GX attack resource and turn-ending attack |

An intermediate audit caught an important source-catalog bug: Jubilife Village says **their turn ends**, which was missed by a detector checking only **your turn ends**. The upstream catalog and its regression were corrected before this integration.

## Interface and interpretation

Each typed entry retains: source name and effect name, source gate and kind, target scope, hand destination, draw mode/count, draw position, Supporter use, GX/VSTAR resource, first-turn text conditions, turn termination, print count and source-text evidence.

For the original 15 discard families the source-text marker links back to the earlier catalog instead of duplicating entire effect texts. For 65 return variants, the normalized complete matching effect text is retained directly.

A simulator must still check attack Energy cost, first-turn Supporter restrictions, Ability suppression, Tool/Bench availability, once-per-game limits, actual draw-count conditions and other text-specific legality. This is a **typed candidate transition catalog**, not a complete action generator or a claim that all 227 prints produce identical strategy.

## Validation

The standalone regression asserts all 80 variant and 227 print counts, destination/category splits, fixed-versus-text-dependent draw policies, 37 turn-ending variants, and 34 Supporter consumers. Named fixtures guard the source gates, target scopes, Ingo & Emmet positional choice, Jubilife Village's turn-ending effect, and Venomoth-GX's once-per-game resource.

The next useful step is to attach zone-conservation and information-belief transition kernels to these profiles so that full-hand material replacement can be simulated without flattening source costs or card-specific conditional draws.
