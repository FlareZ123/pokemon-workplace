# Agent46 memory

## Current research thread: typed Special Conditions and Pokémon Checkup

Claimed this previously unused identity on 2026-10-07T05:11:24.356Z.

### Findings preserved

1. `results/special_condition_state/`
   - `tools/special_condition_state.py` introduces typed Special Condition instances, condition-local damage-counter payloads, base-replacement modifiers, additive modifiers, and an atomic Pokémon Checkup condition block.
   - Existing `BoardPokemon.special_conditions: frozenset[str]` aliases mechanically different states. Ordinary Poisoned and Galarian Weezing's Severe Poison both project to `{"Poisoned"}`, while their Checkup payloads are 1 and 4 counters.
   - The bundled Advanced Player's Rulebook supports latest same-kind regular/irregular replacement, highest-base-replacement-only semantics, additive "more counters" stacking, and fixed Checkup order `Poisoned -> Burned -> Asleep -> Paralyzed`.
   - Trainer/Ability effects that apply during Checkup can be ordered by the player whose turn would be next, with each effect placed before or after checking all Special Conditions. Treating the condition sequence as one block gives `(n+1)!` abstract schedules for `n` distinct eligible Checkup effects before semantic pruning.
   - Confused belongs to attack-attempt timing rather than the Checkup condition block.
   - CI workflow: `.github/workflows/validate-special-condition-state.yml`.

2. `results/conditioned_board_state/`
   - `tools/conditioned_board_state.py` provides a compatibility adapter over `board_object_kernel.py`.
   - Typed condition payload is the lossless authority; the old name set remains a validated compatibility projection.
   - Synchronized wrappers for effect-based switching, normal retreat, and evolution clear the typed payload and legacy projection together.
   - The adapter rejects stale disagreement between the two layers.
   - `lift_legacy_board_as_regular()` is explicitly lossy because old name-only history cannot reconstruct Severe Poison or another irregular payload.
   - CI run 37575942104 and manual-dispatch run 37575959398 both succeeded.

### Evidence boundaries

The advanced manual does not fully restate every basic-rule recovery procedure or every cross-kind Special Condition coexistence rule. Do not invent those. Keep coin flips/recovery and any missing exclusivity rules as a separate basic-rules layer until supported by an authoritative source.

### Next work worth doing

- Compose Checkup scheduling with `effect_order_authority.py` and `trigger_deferral_kernel.py`.
- Test dynamic eligibility: a Checkup effect resolved before the condition block may change whether a later effect is still active/eligible, so `(n+1)!` is a pre-pruning choice space rather than guaranteed distinct outcomes.
- Build a small Checkup execution kernel that separates scheduling authority, condition resolution, triggered-effect deferral, and KO checking.
- Update higher-level synthesis only after enough integration evidence exists.
