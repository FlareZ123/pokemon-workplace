# Agent 2: Repo maintainer requested deck-first results structure (2026-10-12)

On 2026-10-12 at 18:30 UTC a repository-owner commit replaced results/README.md with a new directive: preserve a maintainer footnote, curate a concise deck-focused results index, and progressively move test-like directories into results/tests/ while organizing proven decklists under results/decks/. Old results/README.md had grown to ~435 kB and was overwritten deliberately.

I am preparing a new concise deck-first results README and initial curated results/decks/ entries. Please preserve the owner's directive, avoid restoring the enormous prior index, and place new atomic tests under results/tests/ when feasible. Existing ~964 result directories have many cross-links and imports; do not mass-move without checking breakage and migration strategy. For new research, include a deck-local synthesis if it materially affects deck choice. Communicate any conflicting README/index work before editing.

The source owner commit can be inspected in results/README.md Git history (b8047b40df, 'Update README.md'). There is no match-win-rate evidence establishing a single currently strongest Expanded deck; initial index will rank tournament-backed candidates as provisional, with verified 60s linked.
