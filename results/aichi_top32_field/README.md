# 2026 Aichi Top 32 source field

The [10 May 2026 CL Aichi Open League decklist page](https://limitlesstcg.com/tournaments/566/decklists) publishes ranked player names, archetypes, and card counts. This is the fixed opponent-field benchmark specified in the research objective.

`tools/aichi_top32_source.py` fetches that public page on demand, extracts each source deck's card-name rows **without merging same-name variants**, asserts individual Pokémon/Trainer/Energy subtotals and 60 cards, and fails if 32 valid ranked lists cannot be recovered. Its JSON output records the raw source HTML SHA-256 and the source URL. The workflow `.github/workflows/aichi-top32-source.yml` is **manual-only** and uploads the verified JSON as an artifact. Unit tests use synthetic HTML and exercise failure cases; this is not yet a validated full-page source capture until a manual run passes.

## Provenance and validity boundaries

- The name and count of each card are taken from the source page. No English print IDs are inferred.
- Japanese-only cards (for example, Palace Book, Palace Belt, or Player's Ceremony) may appear; source fidelity does not imply paper Expanded availability in the project's English snapshot.
- Different Pokémon having the same displayed name can have different attacks or Abilities. Their separate rows must be resolved to exact prints before any simulator materialization.
- Parsing and counting only establish structural transcription accuracy. Each candidate still requires mapping to playable English prints, up-to-date legality, engine card support, and a realistically informed decision policy.
- Ranking positions are placements in this tournament, rather than independent samples of performance against a proposed universal deck.

## Next steps

Run the manual workflow, inspect all 32 cards-by-name arrays, and commit the reviewed snapshot or a pinned digest manifest. Build a per-opponent audit identifying unresolved print variants, Japanese-only cards, source total, validated English 60, Twinleaf coverage, and actual match evidence. Use this ledger to choose a fixed candidate and evaluate all 32 opponents on a common engine/research/policy revision with seat-paired trials and explicit error bounds. The existing `simulation/twinleaf/matchup-evidence-ledger.cjs` can then reject incompatible report pooling.

This source inventory improves field completeness; **it does not demonstrate a game win rate**.
