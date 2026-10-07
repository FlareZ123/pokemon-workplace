# Knock Out trigger cascades obey a non-interruption boundary

## Question

When a Knock Out trigger causes another effect to become triggered, may the new
effect interrupt the effect currently resolving?

Current rules evidence says no. The originating effect finishes first. The new
trigger becomes available afterward.

Implementation:

- `tools/trigger_deferral_kernel.py`
- `tools/growing_knockout_context.py`

Regression:

- `results/knockout_trigger_deferral/reproduce.py`

## Rules evidence

Pokémon Japan's 2025-08-01 ruling-change notice changed the handling of an effect
whose earlier instruction causes another card effect to become usable. The
remaining instruction of the original effect is completed first, then the newly
triggered effect is handled.

Source:
https://www.pokemon-card.com/info/005161.html

TPCi Professor guidance published 2026-02-26 states the broader current form:
when a card or effect with a series of effects triggers a different card's
effect, the entire initial card or effect completes before the newly triggered
effect is handled.

Source:
https://professorprogram.pokemon.com/news/11473085

## Concrete Expanded cascade

Two effectively legal Expanded cards create a real two-generation KO trigger
chain.

**Gengar ex `me55-90`, Fainting Spell**

If Gengar ex is Knocked Out by damage from an opponent's attack, it flips a
coin. On heads, the Attacking Pokémon is Knocked Out.

The bundled card snapshot contains a spelling error in this print's text
("Knocket Out"), while the official Pokémon card page uses "Knocked Out".

**Gastly `sm10-67`, Swelling Spite**

When Gastly is Knocked Out, it searches the deck for up to two Haunter and puts
them onto the Bench, then shuffles.

A mechanically legal line can therefore be:

1. a damaged Gengar ex is finished by Gastly's attack;
2. Gengar ex becomes pending Knocked Out and Fainting Spell triggers;
3. Fainting Spell resolves heads and Knock Outs the Attacking Gastly;
4. Gastly's Swelling Spite becomes triggered while Fainting Spell is still the
   active effect;
5. Fainting Spell finishes;
6. Swelling Spite becomes ready and resolves;
7. after the trigger cascade is complete, the final KO membership is frozen for
   physical disposal and Prize handling.

Gastly's 20-damage attack only needs to finish an already-damaged Gengar ex, so
the witness does not require Gastly to one-hit a full-health Gengar.

## Representation

`TriggerDeferralState` keeps four distinct effect states:

- ready effects, represented as an unordered set;
- one active effect with explicit remaining steps;
- effects triggered during the active effect, stored as deferred;
- completed effects, stored only for traceability.

The ready set is deliberately unordered. Choosing among simultaneous ready
effects remains the responsibility of the repository's effect-order authority
layer.

`record_trigger()` places a newly triggered effect in the deferred set whenever
another effect is active. `resolve_next_step()` exposes one step at a time.
Only after the active effect's final step completes are its deferred triggers
moved into the ready set.

## Regression

The regression binds the scheduling rule to the physical KO model.

- Player A's Gastly attacks Player B's Gengar ex.
- Only Gengar ex is initially pending.
- Fainting Spell starts with two modeled steps.
- On the heads branch, the physical KO context grows to include Gastly.
- Swelling Spite is recorded while Fainting Spell remains active.
- Attempting to start Swelling Spite immediately is rejected.
- After Fainting Spell's final step, Swelling Spite becomes ready.
- Swelling Spite then completes its two modeled instructions.
- The final two-player KO membership is converted into the existing fixed
  `PendingKnockOutBatch` protocol.
- Both Active Pokémon are disposed, both surviving Bench Pokémon are promoted,
  and both players' physical card totals remain conserved.

The regression models the timing of Swelling Spite's instructions rather than
performing its deck search. Search semantics can be supplied by the existing
typed search infrastructure in a later composition.

## Finding

The KO engine needs two separate evolving states:

1. physical KO membership can grow while the trigger window remains open;
2. triggered-effect readiness can grow while the currently resolving effect
   remains non-interruptible.

Freezing either state too early loses legal cascades. Executing a new trigger
too early violates the current non-interruption rule.

## Next integration

A larger trigger scheduler can combine:

- source-profile and timing-based order authority;
- unordered ready-effect groups;
- active-effect non-interruption;
- growable KO membership;
- card-specific semantic transitions;
- final fixed-batch disposal and Prize resolution.

The current kernel intentionally stops before card-specific trigger discovery or
automatic ordering among simultaneous ready effects.
