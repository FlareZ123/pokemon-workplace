# Mega Absol ex direct-KO semantics

2026-05-10 Aichi eighth-place Mega Absol/Garbodor uses print `me1-86`. Pinned Twinleaf revision: `3348ebdc898f175a2ed8f999133cd13d1afd01f5`.

Printed **Terminal Period** knocks out the opposing Active if it has **exactly six damage counters**. The Advanced Player's Rulebook C-17 establishes that attack effects can be prevented separately from damage.

The pinned `mega-absol-ex.ts` instead increases opposing Active damage by 999. This bypasses normal non-damage effect protection and creates extraneous damage. It is especially relevant to the eighth-place tournament list.

Research correction: `simulation/twinleaf/hooks/mega-absol-terminal-period.cjs` sends the conditional Knock Out through Twinleaf's `KnockOutOpponentEffect` and leaves other attacks unchanged. The shared headless runner installs the idempotent hook with version label `mega_absol_terminal_period_direct_ko_v1`.

Reproduction: `simulation/twinleaf/test-mega-absol-terminal-period.cjs` contrasts native 1059 counters against one typed Knock Out at exactly six counters. `test-mega-absol-parasol.cjs` verifies the actual pinned Big Parasol reducer prevents the typed effect. [Original CI pass](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38398116272) and [Big Parasol CI pass](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38398462453).

**Limit:** The focused tests use a StoreLike double for effect routing. Full Store knockout/Prize interactions and competitive match strength are not established. The 2026 deck remains a tournament-supported reference, with no validated diverse-field head-to-head win rate.
