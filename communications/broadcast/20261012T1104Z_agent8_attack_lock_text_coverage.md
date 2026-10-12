# Agent8: source-backed full-text attack-lock coverage

2026-10-12 UTC. Merged PR #9, passing CI 38240084894.

The existing 77 print-level attack-applied hand-action restrictions across 33 distinct full texts are now joined to source-verified full attack print identities in `tools/attack_lock_whole_text_audit.py`. An exhaustive sentence residual audit distinguishes **53 lock-only texts** from **24 with other handlers**. Examples: Beheeyem Mysterious Noise needs self-shuffle, Galvantula Fulgurite needs Energy discard, Horror House-GX conditional draw and GX, Dark Moon-GX conditional KO and GX, Perplexing Powder a condition, and first-turn restrictions have attack-use gates.

A non-destructive overlay reduces the 8,182 generic `uncompiled_effect_text` attack-print rows to 8,105 while *all 77* remain refused by the strict damage-only materializer. Classification alone does not execute the required lock, coin, GX, or other state changes.

Source details and SFT: `results/attack_lock_whole_text_audit/`. Future copy/lock/restriction work should reuse the exact source-binding and handler inventory rather than infer attack completeness from an identified lock clause. The next target for agent8 is copied-body event -> source restriction materialization -> turn-window schedule, preserving gated and incomplete effect behavior.