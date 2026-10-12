# Agent31: coordinating results curation after owner directive

The repository owner replaced the old oversized results/README.md with an explicit request for a concise human-usable deck index, `results/decks/` and `results/tests/`, and no future 900-item root test dump. At 18:33 UTC multiple agents independently created near-duplicate deck directories (e.g. `regidrago-aichi-2026` and `regidrago-vstar`; `vileplume-control-aichi-2026` and `vileplume-control`).

I will replace `results/README.md` with a curated 5-deck tournament baseline index and a clearly experimental Mew VIP4 candidate, retaining the maintainer note in a footnote. Please stop appending atomic test paragraphs to the index. Preserve tests in their current paths until a dependency-aware staged migration can rewrite relative imports, CI paths, and links. Existing `results/competitive_deck_baselines/` remains validated provenance.

Future agents can merge duplicate deck directories after comparing print IDs, link consistency, and external backlinks. Avoid deleting other agents' files on discovery alone.
