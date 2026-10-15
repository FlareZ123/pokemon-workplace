# Agent 3: source-data audit and historical Maintenance / VS Seeker evidence

Verified three current-source evolution parents against official Pokémon card text:
- `me55-96` Zoroark missing parent `Zorua`
- `rsv10pt5-50`, `rsv10pt5-131` Archen typo `Antiuqe Plume Fossil` corrected to `Antique Plume Fossil`.

The Python guarded source normalizer and `results/verified_card_metadata_boundary/overrides.json` Node CJS manifest now contain **75** exact-print patches. `results/evolution_parent_integrity/` independently scans 20,635 source cards and leaves the single Japanese text Exeggutor parent unresolved. Windows CI 38730685077, 38729974763 passed.

Separately, `results/maintenance_shuffle_equivalence/` proved Base Maintenance 2-card shuffle/playability against XY using exact conditional outcomes. Official Pokémon BW introduction explicitly calls old plain Trainers Items. `tools/maintenance_current_semantics.py` now narrowly normalizes `base1-83` and `base4-112`, promoting both to `exact_fingerprint_candidate`. Full resolver CI 38732464795 passed; **226** candidate prints, **3,957** semantic-review. This is a candidate classification, not explicit official print-acceptance certification.

`results/vs_seeker_public_discard_equivalence/` independently validates two older VS Seeker print texts against XY, but those were already exact fingerprints and candidate counts did not change.

Consult source audit READMEs before consuming corrected card properties; no raw archive or upstream Twinleaf source modified.
