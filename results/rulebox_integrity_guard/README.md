# Pokémon Rule Box integrity across six card classes

## Scope

Strong Expanded deck simulation requires the correct number of Prizes on Knock Out, Tera Bench protection, and construction-restricted Pokémon identities. An undetected source-data defect can propagate through thousands of game states or cause two identical artwork prints to appear functionally different.

This audit scans **every Pokémon in the supplied English card pool** and checks six current Rule Box families against simple physical-card invariants:

| Printed class | Current dataset count after repair | Checked invariant |
| --- | ---: | --- |
| Mega Evolution ex | 114 | Exactly one Mega three-Prize rule; no extra ordinary two-Prize rule |
| Tera ex | 147 | Exactly one Tera protection-from-Bench-attack-damage statement |
| VMAX | 210 | A VMAX three-Prize rule |
| VSTAR | 95 | A VSTAR two-Prize rule |
| TAG TEAM | 120 | A TAG TEAM three-Prize rule |
| Radiant | 16 | A Radiant Pokémon singleton deck rule |

Before applying the separate verified metadata corrections, the archive has **70 Rule Box violations**: 45 extra generic Mega-ex rules, one missing Mega rule on `me5-115`, and 24 duplicate Tera damage-prevention statements. The missing Tera trait on `sv8pt5-92` means that print is **not counted at all** in the Tera category until repaired. The corrected shared loader yields 147 Tera ex records and **zero violations** in the checked families.

## Reproduction

The scanner is `tools/rulebox_integrity_audit.py`, and the independent exact-count oracle is `results/rulebox_integrity_guard/reproduce.py`. Run:

`python -m results.rulebox_integrity_guard.reproduce`

This test compares the complete exact original 70-issue set with the corrected zero-issue set and verifies all six category populations. Windows CI runs it on snapshot changes through `.github/workflows/validate-rulebox-integrity.yml`.

## Evidence and limitations

The class rules are grounded in the bundled Advanced Player's Rulebook (D-18) and printed card text. The 45 Mega, 24 Tera and one missing Stage/rule repairs are separately documented with representative physical-print photo evidence and print-local mutation guards in [the shared metadata boundary](../verified_card_metadata_boundary/).

An invariant check cannot detect a missing subtype when that subtype is the predicate determining whether the check should run. It also does not audit all possible Rule Box formats, event semantics or engine Prize processing. Same-set print variant checks [complement this limitation](../same_set_print_anomaly_guard/). Passing these structural checks is an input-data confidence improvement, rather than a claim of proven tournament-level simulation fidelity.
