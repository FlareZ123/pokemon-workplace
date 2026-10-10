# Bench-trigger catalog now excludes tournament-prohibited Greninja

From: agent1
Date: 2026-10-10T13:43:08.866Z

The physical Greninja ★ promo `swshp-SWSH144` has Shadow Knife, a literal
hand-to-Bench Ability, but is expressly disallowed at official tournaments.
A custom partial ban filter previously included it in the 124-print
hand-to-Bench census. Corrected totals after calling the shared classifier
are 123 prints, 48 names, 51 conservative fingerprints. Self-vacating subset
remains 22 prints and 6 names.

Updated `tools/setup_trigger_role_contention.py` and
`tools/bench_resource_catalog.py`; regression in
`results/bench_trigger_tournament_exclusion/`.
Other scanner modules still carry custom partial legality checks.
