# Source-verified full-text attack-lock coverage

## Problem

The direct hand-action restriction compiler identifies 77 effectively legal paper Expanded attack printings with player-scoped restrictions. Its output establishes that a lock clause has typed semantics. It does not establish that the attack has no other consequences. The conservative whole-text coverage inventory previously left these rows inside `uncompiled_effect_text`.

## Method

`tools/attack_lock_whole_text_audit.py` joins the current legality-filtered attack index to `source_scoped_restriction_activation` using the exact card ID, attack name, and complete normalized text. A source matches precisely one physical attack-print row; mismatches, duplicate bindings, and unsupported printed damage fail closed.

Each sentence is accounted for. The existing source compiler owns the hand-action restriction. The audit identifies secondary sentences only when their *whole text* matches a known pattern. A new sentence remains opaque. The application-gate compiler is cross-checked so coin-, choice-, and prerequisite-gated restrictions cannot lose their respective handlers.

The overlay labels the restriction component `source_scoped_lock_only` or `source_scoped_lock_with_other_handlers`. This is a coverage classification, never a claim that the complete attack can be executed without a further live-state or timing implementation. The existing strict `materialize_damage_only_verified()` is left unchanged and must still reject all 77 attacks.

## Corpus-level finding

The bundled legal snapshot has **77 print rows** with **33 distinct complete lock-attack texts**. Among the 77 rows, **53** have only the lock consequence; **24** require at least one additional handler.

| Other handler profile | Print rows |
| --- | ---: |
| None | 53 |
| Stadium discard prerequisite | 1 |
| Attacker self-shuffle | 1 |
| Conditional Knock Out plus GX budget | 2 |
| Previous-turn attack-history gate | 1 |
| GX budget | 3 |
| Going-second first-turn gate | 3 |
| Coin result | 4 |
| Conditional draw-to-seven plus GX budget | 4 |
| Special Condition | 1 |
| Choice of restricted card class | 1 |
| Attacker Energy discard | 3 |
| **Total** | **77** |

The 24 compound/gated examples include Beheeyem Mysterious Noise (self-shuffle); Umbreon & Darkrai-GX Dark Moon-GX (conditional Knock Out); Gengar & Mimikyu-GX Horror House-GX (conditional draw); Galvantula ex Fulgurite (Energy discard); Venomoth Perplexing Powder (Confused); Walrein Cold Snap (repeat-attack gate); Chi-Yu Scorching Earth (Stadium discard); and GX or coin/choice restrictions.

The non-destructive coverage overlay reduces the generic *uncompiled-effect-text* bin from **8,182 to 8,105** and adds two explicit categories totaling 77. The original broad bin is not a measure of executable attack completeness. Every recognized lock still needs a turn-window restriction handler. Compound texts need their listed additional handlers, while source/action/board legality is checked separately.

## Independent safeguards and interpretation

- Source matching binds complete attack text, not an attack name alone.
- An introduced `Draw a card.` clause is left opaque and does not acquire a recognized handler.
- Removing a coin instruction from a source whose activation profile requires one fails.
- All 77 attacks remain rejected by the strict damage-only materializer.
- The corpus comparison measures semantics covered by existing typed tools. It is not a Twinleaf simulation, an estimated matchup win percentage, or proof of a deck's competitive strength.

## Reproduce

Run `python results/attack_lock_whole_text_audit/reproduce.py` from the repository root. The regression checks exact source bindings, the complete category distribution, 13 representative prints, unknown-clause behavior, missing gate instructions, all 77 damage-only rejection gates, and conservation of the 19,992-row coverage census.

The CI workflow is `.github/workflows/validate-attack-lock-whole-text.yml`. Current source snapshot and current legality logic are dependencies: corpus updates should cause a failed assertion and a new audit rather than silently claim unchanged coverage.

## Remaining work

Connect the already-existing restriction materialization and turn-window lifetime to the executed copied-body trace. In a genuine game step, the lock must be created after its gate succeeds; any other effects of the same attack must execute in correct phase order. In particular, a Beheeyem self-shuffle or a Fulgurite Energy discard cannot be ignored merely because the lock clause was recognized.
