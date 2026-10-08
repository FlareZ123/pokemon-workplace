# Ordered event journal for committed plays and Ability-lock precedence

## Research question

Can the existing play-event bridge and the continuous Ability-lock precedence owner share a replayable ordered history without conflating the two sources of state?

## Contribution

`tools/causal_event_journal.py` adds an immutable event-boundary journal. Each validated transition supplies both physical boards, the Stadium in play, an event identity, and optionally a `CommittedPlayEvent` from the existing Trainer producer.

Each boundary advances the existing `AbilityLockCausalState`, records its result and accumulates only *committed* physical Trainer plays. A failed Item/Supporter attempt, a copied Supporter attack effect, or a Stadium moved into play via Teleport Room must supply no committed-play event. Recording a board boundary and recording that a card was **played** are distinct operations.

The journal has a monotonic revision check and unique event IDs, permitting callers to reject stale submissions and duplicate event records. Replaying reconstructs every intermediate continuous-lock state rather than consulting the final board alone. The journal stores board snapshots for auditability; this research implementation is not a compact production event store.

## Exact counterexample

Two sequences end with the *same physical boards*:

1. Empoleon V and Wobbuffet both begin Active; verified setup precedence selects Empoleon V. A later endpoint still has both Active.
2. The same initial board is followed by Wobbuffet leaving Active while another Pokémon becomes Active. The source graph becomes acyclic. Wobbuffet later returns Active, reintroducing the mutual suppression cycle.

The first sequence retains the verified setup precedence under the existing causal owner's continuity condition. The second returns *unresolved* after the interrupted source graph is reintroduced, since no official midgame reentry precedence ruling is encoded.

Both sequences have **identical committed Trainer-play histories**, including the same normal and forced Supporters. Thus even the combination of the final physical board and a complete Trainer-play log is insufficient to determine the supported effective-lock state. The event **order and intermediate source geometry** are necessary data. The journal makes this assumption explicit and replay-testable.

A second real-card family checks undamaged Tool-attached Garbodor suppressing Ting-Lu ex, then damage activating the reverse edge, then healing. The existing verified-established precedence and later return to a snapshot state remain stable under journal replay.

## Validation

`python results/causal_event_journal/reproduce.py`

The regression covers both official-case lock families, two distinct committed-play channels constructed through their actual producer kernels, copied-effect non-events, identical-endpoint/identical-play-history/different-lock states, stale revision and duplicate ID rejection, and corruption detection on replay.

## Scope and cautions

The journal **does not** generate mechanical actions, prove that events were not skipped, certify card legality, infer unknown precedence rulings, or grant a right to play Trainers. Callers must submit every lock-relevant event after legality and physical state changes have been validated. The existing lock-state owner continues to report unsupported cycles as unresolved. The existing Trainer-play producers determine which actions count as committed plays.

Dependencies: [ability_lock_causal_state](../ability_lock_causal_state/), [committed_play_event](../committed_play_event/). Key original rules evidence is in the supplied Advanced Player's Rulebook and the verified-case documentation in those dependencies.
