# Consistent Expanded legality across five effect scanners

## Observation

Five additional card-pool scanners implemented partial legality filters:
`attack_copy_catalog`, `lock_effect_catalog`, `combat_lock_catalog`,
`bench_release_catalog`, and `multi_output_search_catalog`.
They recognized database Expanded bans and the dated seven-print ban overlay,
but did not apply the source cards' explicit official-tournament prohibition.

The seven tournament-prohibited promos are Pokémon. The attack-copy census
therefore overstated its **legal source population by seven**, even though
none of the seven has a matching copied-attack body. The corrected attack-copy
scan reads **14,829 legal prints** and still finds **64 attack-copy prints**
and **30 distinct copy-attack signatures**.

The lock, combat-lock, Bench-release, and multi-output search inventories use
the shared classifier now as well. Their matching-effect totals remain
unchanged under the current source records, which illustrates how a
population defect can escape signature-level regressions.

## Mechanism

Each scanner now delegates to the existing
`classify_effective_legality` function, preserving one repository-wide
source of truth for a physical print's current tournament eligibility.
This function accounts for current official ban overlays, database bans,
and printed official-tournament exclusions.

## Reproduction

Run `python -m results.shared_effect_catalog_legality.reproduce`.
It proves that each print-level classifier rejects the seven excluded promos,
checks the corrected complete attack-copy population, confirms the unchanged
copy-attack count, verifies exclusion from lock and release signatures, and
checks all 2,119 eligible Trainers in the multi-output search input.

A focused Windows CI workflow executes this alongside the attack-copy
source-census regression and the existing Bench-release regression.

The broader `validate-attack-copy-research.yml` workflow has a separate
pre-existing failure in `turn_attack_provenance` on the stale-Copycat
extra-turn assertion. Its attack-copy catalog stage itself passed on the
corrected commit. This independent failure should not be described as
validation of the full workflow.

## Boundaries

Legality here is assessed against the current bundled paper Expanded
snapshot and known exclusions, with historical release dates, regional
tournament restrictions, and historical functional-reprint adjudication
handled by separate infrastructure.
