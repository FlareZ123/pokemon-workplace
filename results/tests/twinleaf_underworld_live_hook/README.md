# Underworld Door guard in the **live** headless matchup runner

## Finding

The pinned Twinleaf revision `3348ebdc898f175a2ed8f999133cd13d1afd01f5` has a verified Underworld Door target-eligibility bug. The source passes bench indices in the source-energy `blocked` field, and tests `PokemonCardList` objects with `instanceof PokemonCard`. In the actual pinned engine this permits attaching Energy to an ineligible Benched Pokémon.

The repository previously had a tested research-side remedy at `simulation/twinleaf/hooks/shadow-rider-underworld-door.cjs`, with a source-grounded regression at `test-underworld-door-targets.cjs`. However, the standard manual matchup path `simulation/twinleaf/tournament-bounded-match.cjs` never installed this hook, so prior matchup diagnostics were **not protected by that fix**. This gap persisted even though the hook's independent SFT was run by a different CI job step.

## Integration change

The live `runOne` entry point now installs the hook before constructing or dispatching any game. It uses the existing idempotent installer, leaving the upstream Git submodule unchanged. Every returned trace includes `engine_hooks: ["shadow_rider_underworld_door_guard_v1"]`, and the aggregate report records the same hook label.

The new standalone regression `simulation/twinleaf/test-tournament-engine-hooks.cjs` begins in a fresh Node process, registers a small real-engine 60-card Regidrago/Energy fixture, drives two live engine actions through `runOne`, and verifies that the guard was installed and reported. It also confirms that repeated explicit hook setup preserves the identical hook set. Both bounded-match manual GitHub Actions workflows now execute this SFT before their headless-match step.

The existing `test-underworld-door-targets.cjs` is a complementary semantics test: it demonstrates the pinned engine accepting an invalid Dragon destination before the hook, then the hook rejecting it while retaining the legal Psychic destination. Together these tests cover semantic correctness and the runner's installation path.

## Evidence boundary

Any earlier Shadow Rider match diagnostic run through the unguarded runner lacks a verified ability-target restriction. This does **not** prove that every trace actually selected an illegal target. It does mean the old traces and the new guarded traces differ in their game-engine semantics and must not be pooled as matched-replicate evidence.

A valid hook label is evidence that the patch was installed, not that Twinleaf has complete Expanded rules parity. The policy remains `SimpleTacticsAi`, which has documented inability to exercise key matchup mechanics. No match-win-rate inference follows from installing this guard.

## Reproduction

- Source pin and card-level diagnostic: [Underworld Door defect and guard](../../twinleaf_shadow_rider_underworld_door/).
- Runner: [tournament-bounded-match.cjs](../../../simulation/twinleaf/tournament-bounded-match.cjs).
- Live-path SFT: [test-tournament-engine-hooks.cjs](../../../simulation/twinleaf/test-tournament-engine-hooks.cjs).
- Paired workflow: [twinleaf-manual-matchup.yml](../../../.github/workflows/twinleaf-manual-matchup.yml).
- Independent exact-print paper Shadow Rider list: [decks/shadow-rider-calyrex](../../decks/shadow-rider-calyrex/).

Research classification: executable engine integration correction, with a bounded real-action regression. This result describes simulation validity; the highest-confidence competitive evidence remains the 2026 Aichi tournament placement and the independently checked 60-card list.
