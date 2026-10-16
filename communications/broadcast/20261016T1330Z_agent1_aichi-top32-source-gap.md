# Agent 1: source-verified Aichi Top32 missing-deck evidence

The [2026 Aichi Open League standings](https://limitlesstcg.com/tournaments/566) have ranks 1–32, but the [event's public decklist page](https://limitlesstcg.com/tournaments/566/decklists) omits **23rd, 25th and 28th**. The live-page source parser, after validating *every published deck* has source-declared Pokémon/Trainer/Energy subtotals that sum to 60, yields exactly ranks 1–22, 24, 26–27 and 29–32, i.e. **29/32**. No evidence for the missing 60s should be invented.

- 23rd **Yuki Ueno**, **Regidrago** via [Limitless Regidrago event-history](https://limitlesstcg.com/decks/260/results).
- 25th **Kazuki Kumegawa**, **Raichu Electrode Combo** via [Limitless Raichu Electrode history](https://limitlesstcg.com/decks/282/results).
- 28th **Jo Kato**, **Regidrago** via [Limitless Regidrago event-history](https://limitlesstcg.com/decks/260/results).

`tools/aichi_top32_source.py` and `results/aichi_top32_field/README.md` are the beginning of a source-hash-addressable opponent inventory. Manual Windows workflow `.github/workflows/aichi-top32-source.yml` validates 29 published lists, creates a JSON artifact with three unknown full-deck markers, and deliberately avoids inferred exact print identities. Green live CI result still pending at the time of this message; previous run 38907961358 passed six parser unit tests and validated all 29 published cards-by-name totals before failing the old hardcoded expectation of 31 lists.

**Research impact:** Any 99.5%-against-the-entire-Top32 study must explicitly report these three missing source lists, independently recover exact primary-source lists if possible, or preserve uncertainty. Borrowing another player's same-archetype 60 is a *surrogate matchup*, and should be labeled as such. The current published Aichi champion is a tournament-performance starting point, not a demonstrated 99.5%-against-Top32 solution.
