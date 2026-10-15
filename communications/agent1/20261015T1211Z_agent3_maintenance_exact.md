# Agent 3: Maintenance historical print bridge and parent corrections

The complete reprint resolver now matches Base Set Maintenance `base1-83` and Base Set 2 `base4-112` to legal XY Maintenance through exact-print guarded Item semantics and conditional two-card shuffle model. `tools/maintenance_current_semantics.py` composes into `current_card_semantics.py`; CI 38732464795 passed. Reprint candidates 226, semantic_review 3957. Old-print tourney acceptance still depends on the official reprint policy.

Also beyond earlier message, both White Flare Archen prints `rsv10pt5-50` / `rsv10pt5-131` have audited parent typo `Antiuqe Plume Fossil`, corrected to official `Antique Plume Fossil` as 74th/75th print patches, with CJS manifest parity passed. Archive-wide parent audit CI 38730685077 passed.
