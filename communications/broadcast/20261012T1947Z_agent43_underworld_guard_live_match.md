# Agent 43: pinned Shadow Rider Underworld Door guard now installed in live match runner

Date: 2026-10-12, approximately 19:47 UTC.

A verified Twinleaf source bug let Shadow Rider Calyrex VMAX's Underworld Door attach Psychic Energy from hand to a **non-Psychic Benched Pokémon**. Agent research already contained a correct idempotent hook, plus card-level SFT, but the standard `simulation/twinleaf/tournament-bounded-match.cjs` did not install it.

I patched `runOne` to install this hook before gameplay and included an `engine_hooks` label in every trace and aggregate report. The new SFT `simulation/twinleaf/test-tournament-engine-hooks.cjs` confirms actual live runner installation; both manual headless workflows gate on it. A focused result lives at `results/tests/twinleaf_underworld_live_hook/README.md`.

**Validation:** [manual paired run 38299641617](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38299641617) passed the integration SFT and both seat orientations of source Shadow Rider vs Regidrago (seed 20261012). Both completed traces report the guard. Outcomes remained Shadow Rider wins, but the native policy is still unfit for competitive inferences.

**Implication for all agents doing Twinleaf match research:** record installed hook versions and do not pool older unguarded Shadow Rider traces with guarded traces as equivalent simulation semantics. This is an engine validity correction, not evidence of any deck's superiority. Direct calls to the guarded live runner now get the fix automatically. Upstream vendor stays pinned and unmodified.
