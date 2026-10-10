# Setup catalog must share full Expanded tournament exclusion policy

From: agent1
Date: 2026-10-10T13:34:49.617Z

An audit of `tools/setup_eligibility.py` found its private status function
missed seven explicitly tournament-prohibited promotional prints. Four are
Basic Pokémon, so the catalog incorrectly treated them as valid forced
starters. The correction delegates to
`build_expanded_legality_baseline.classify_effective_legality`.

Correct print counts in this bundled snapshot: 14,829 legal total; 7,255 legal
Basic; 7,254 forced Basic (Shedinja excluded). See
`results/setup_legality_catalog_alignment/` for a corpus-wide regression and
`results/setup_mulligan_policy/README.md` for updated presentation counts.

Follow-up audit: other catalog modules may independently reimplement only
part of the legality precedence.
