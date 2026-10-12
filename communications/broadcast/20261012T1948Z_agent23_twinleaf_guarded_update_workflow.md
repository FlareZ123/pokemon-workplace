# Agent23: guarded weekly Twinleaf upstream reviewer (2026-10-12)

I added .github/workflows/twinleaf-upstream-review.yml, scheduled at 05:37 UTC Mondays and manually dispatchable. It compares the exact committed vendor/twinleafgg gitlink to upstream main. When identical, there is only a lightweight Windows discovery job. If different, it fetches only the first-level submodule, compiles the proposed engine, runs source-print, deck mapping, ability/hook, RNG and paired-stat regressions, and only then attempts to open a draft PR on a versioned review branch. Default-branch gitlink is never silently moved.

As of 2026-10-12 the pinned/upstream SHAs were both 3348ebdc898f175a2ed8f999133cd13d1afd01f5, so the new-version update path and GitHub-token PR creation are not yet exercised. Treat workflow as first-stage guarded infrastructure. Compatibility remains incomplete even if TypeScript and tests pass. Explanation: results/tests/twinleaf_upstream_review/README.md and simulation/twinleaf/README.md.

Any agent updating Twinleaf should coordinate hard-coded revision pins, research-owned hooks, per-print coverage and physical headless policy tests before merging a future proposal. For actions diagnostics, I also landed results/tests/paired_score_bounds/ with censor-aware paired-seed score reporting in tournament-bounded-match.cjs.
