# Copied attack body to real hand-lock turn window

## Research question

When an attack-copy effect executes the text of an attack that imposes an Item, Supporter, Stadium, Energy, or card-from-hand restriction, how can the resulting lock enter the correct opponent-turn lifetime while preserving the copy attack's actual source identity and refusing incomplete attack semantics?

## Model and bridge

`tools/copied_attack_lock_window_bridge.py` combines four existing source-backed layers:

1. The copy kernel's executed leaf trace and exact `body:<card_id>:attack:<index>` event.
2. The new whole-text lock audit, which records every secondary effect handler.
3. `materialize_attack_restriction`, which uses actual coin or exclusive-branch outcomes to produce an actionable source-scoped restriction.
4. `create_attack_restriction_window`, which schedules opponent-next-turn or longer source-turn effects.

A copied body is eligible for this narrow bridge only when its additional handler set contains **at most a coin gate or player-selected exclusive branch**. Therefore 58 of the 77 printings fit this lock-only-or-self-contained-gate contract: 53 have no additional handlers, four require a coin result, and one requires a player-selected dimension. The other 19 remain deliberately rejected; the caller cannot use the lock-window bridge to assert that Beheeyem self-shuffled, Galvantula discarded Energy, or GX effects and attack-history requirements were completed.

An executed source event is necessary. Merely selecting an attack in the copy engine, or possessing an attack ID in a search graph, is insufficient. The bridge requires exactly one matching event and an executed leaf trace. A coin tails result yields no pending lock; a valid heads result yields a concrete pending lock. A chosen Item or Supporter branch blocks only its chosen card class.

## Real-card reproduction

The single runnable test `results/copied_attack_lock_window_bridge/reproduce.py` uses the Haughty Order copy route to select original printings:

- Budew `me2pt5-16` Itchy Pollen creates a next-opponent-turn Item-from-hand prohibition while leaving Prize-origin Item actions and hand Supporters unrestricted.
- Psyduck `sm9-26` Headache requires a coin; tails creates no window.
- Crobat `sv4-112` Echoing Madness preserves the Item-or-Supporter exclusive choice.
- Vileplume `swsh11-3` Allergy Storm sends heads to Supporter lock and tails to Item lock.
- Vanilluxe `xy8-45` Frigid Breath applies a simultaneous lock on both players until the original attacker's next turn ends.
- Copied-body execution prevented by a copy gate and opaque residual clauses are rejected.
- Six representative compound attacks are rejected until their other semantic handlers are executed.

The regression also checks that an extra turn by the attacker does not prematurely activate a pending opponent-next-turn hand lock.

## Boundaries

The bridge owns the **creation** of one legally characterized lock window after a verified copied-body event. It does not execute the copied attack's damage, check the attack's Energy cost, decide whether the attack reached its effects step, adjudicate attack-effect immunity, or advance an entire completed turn. Callers must supply those results and pass the new window to the existing turn scheduler. Its source event verifies copy-kernel execution, not complete physical combat execution.

Coverage is a reusable paper Expanded mechanics result. It is neither a full Twinleaf game nor a competitive deck win-rate measurement.
