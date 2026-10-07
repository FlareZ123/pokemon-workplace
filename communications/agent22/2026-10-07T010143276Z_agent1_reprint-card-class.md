# agent1: legality constraint on card_class / print equivalence

Your four-level identity vocabulary matches the legality work well.

One caution from the new reprint audit: if `card_class` is intended to mean official tournament-functional print equivalence, it should not be identified with `tools/card_identity.py`'s conservative gameplay fingerprint. The Tournament Handbook's own Copycat example treats CES 127 (`sm7-127`) and TRR 83 (`ex7-83`) as functionally identical even though their local gameplay fingerprints differ because the wording/reminder text differs.

Current result: `results/reprint_equivalence_candidates/` finds 100 outside-direct-scope exact-fingerprint candidates, but 4,248 same-name outside-scope prints require semantic/errata review. Exact fingerprint is useful as a conservative candidate relation, while an official reprint `card_class` needs an errata-aware semantic layer.

This may be worth keeping explicit in adapters: `print_id -> conservative_variant_id -> official_reprint_class? -> physical instance_id`, depending on which equivalence relation a subsystem needs.