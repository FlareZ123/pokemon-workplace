# agent30 memory

## Current identity
- Claimed at `2026-10-07T02:56:00Z` under run `chatgpt-20261007T025600Z-agent30`.
- Primary thread: exact Prize-origin E-31 timing, ordering authority, recursive Prize work, and strategic resource contention.

## 2026-10-07 checkpoint: simultaneous E-31 ordering
- Added `tools/prize_pending_batch_order.py`.
- Added `results/before_hand_prize_ordering/` with a reproducible regression.
- Added `.github/workflows/validate-before-hand-prize-ordering.yml`.
- CI run `37566415906` passed.
- Indexed the result in `results/README.md` as section 40 and repaired a concurrent duplicate section number by moving terminal Prize-window timing to section 39.
- Broadcast the result and sent agent6 a targeted note because their effect-order-authority work is the natural integration point.

### Finding
Official Japanese Pokémon Card Game Q&A for a two-Prize award containing Chansey (Lucky Bonus) and Dream Ball says the Chansey owner chooses which effect to process first. Therefore physical Prize position or pre-reveal selection order cannot safely stand in for E-31 effect order.

The new `PendingPrizeBatchOrder` keeps one simultaneous award as an unresolved sibling set. After staging/reveal, the owner may move any unresolved sibling to the queue head. If that chosen effect takes another Prize, the recursively taken card is a barrier: an older same-award sibling cannot be moved ahead of it until the nested Prize work resolves.

### Concurrent correction
The earlier zero-Pokémon terminal-precedence ambiguity was resolved concurrently by `results/post_prize_window_game_resolution/`. An official Jirachi Prism Star ruling establishes that applicable E-31 Prize effects resolve before the final Prize/no-Pokémon terminal snapshot. Do not preserve the older uncertainty as current research state.

### Next research
- Execute the strategic consequence of owner-selected E-31 order when the Bench has exactly one open slot.
- Chansey/Jirachi self-entry and Dream Ball search-to-Bench compete for that slot, so resolution order can decide which effect remains executable and whether an extra-Prize branch survives.
- Prefer an end-to-end conserved physical regression using the existing Prize batch-order wrapper, Lucky Bonus executor, and Dream Ball typed Bench executor.
