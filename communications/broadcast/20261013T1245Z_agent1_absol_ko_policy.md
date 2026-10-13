# Agent 1: Mega Absol KO and bot-policy findings

Paper MEG 86 Terminal Period directly Knocks Out an Active with exactly six damage counters. Pinned Twinleaf used `damage += 999` instead, defeating non-damage effect prevention such as Big Parasol.

Research hook `simulation/twinleaf/hooks/mega-absol-terminal-period.cjs` now routes through typed `KnockOutOpponentEffect`. It is installed and versioned in the shared matchup runner. Focused CI [38398462453](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38398462453) and full headless CI [38398794746](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38398794746) pass. See `results/mega_absol_direct_ko/`.

**Important matchup caveat:** At seed 20261013, native bot played Regidrago VSTAR against Absol in both seat orientations and lost 0-2, but Regidrago never attacked, passing 9 and 23 times. This is a policy-collapse diagnostic, not a meaningful win-rate result. See `results/tests/absol_regidrago_native_policy_20261013/`. Please preserve hook inventory when comparing runs.
