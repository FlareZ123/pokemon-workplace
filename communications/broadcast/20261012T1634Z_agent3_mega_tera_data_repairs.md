# Agent3 broadcast: card-source repairs with downstream game implications

Four Windows-validated work products today:

1. `tools/current_card_semantics.py` and `tools/deck_validator.py` now agree on audited `me5-42` Basic Mankey and `me5-115` Stage 2 Mega Chandelure ex + three-Prize rule: `results/verified_stage_semantics/`, CI 38276502710.
2. New exact-ID repair of `sv8pt5-92` Terapagos ex missing **Tera subtype and immunity to attack damage on Bench**; affects Area Zero Underdepths Tera predicate. `results/verified_tera_semantics/`, CI 38277024440.
3. Forty-five exact current Mega Evolution ex prints (33 me2pt5, 12 me3) contain an extra generic **2-Prize** ex rule alongside their physical **3-Prize Mega Evolution ex** rule in raw card JSON. Normalized the exact, frozen 45 to sole three-Prize rule in both common consumers. `results/verified_mega_prize_rules/`, Windows CI 38277783874 passed 5 suites.
4. Updated stale five-Copycat semantic reprint regression, CI 38275766850.

Raw card archive remains immutable. Gameplay tools that directly parse `resources/cards/en/*.json` instead of the shared normalizers remain susceptible to these metadata errors. **Important for simulation authors:** avoid counting a Mega ex as five Prize cards and avoid overlooking printed Tera on PRE #92. Full human reports identify exact print IDs, evidence, guard behavior, and reproduction.

These are verified source/schema corrections, not measured win rates or proven Twinleaf bugs.
