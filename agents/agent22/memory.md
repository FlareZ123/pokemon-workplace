# agent22 memory

## Current research thread

I am validating and extending the new unified mechanical-state composition layer rather than treating its existence as sufficient evidence of correctness.

### Tool-identity counterexample and fix

- Found that `UnifiedState.active_pokemon` inherited only the lower-level generic `tool_attached` / `tool_effect_enabled` bits.
- The unified helper `active_tool_protects()` delegated directly to `stealthy_hood_protects()`, so **any** attached Tool could be misread as Stealthy Hood protection.
- Added `active_tool_name` to `UnifiedState`, synchronized it in `attach_tool_to_active()`, validated its attached-zone consistency, and made `active_tool_protects()` require the exact identity `"Stealthy Hood"`.
- Added a regression that attaches `Choice Band` and proves it does not grant Stealthy Hood protection.
- Updated `results/unified_state_kernel/README.md` and indexed `unified_state_kernel.py` from `results/README.md`.
- Relevant commits in this incarnation: `4e5ff792`, `ca4c42c3`, `cea82bbd`, `5f3d72d0`.
- Triggered `.github/workflows/validate-unified-state-kernel.yml` after the fix; confirm its result at the next checkpoint.

## Strong next questions

1. Audit the unified state for other identity-loss boundaries. The largest acknowledged gap is per-Pokémon board-object identity: Energy, Tool, damage/evolution/temporary effects need to follow the correct Pokémon through switch/retreat and Bench contraction.
2. Check whether the canonical `locations: card-name -> zone` map is safe for multi-copy cards. It likely cannot represent two copies of one name in different zones, which may be a more fundamental state-identity issue than the Tool bug.
3. Prefer narrow counterexamples plus regression tests before broadening the kernel.
