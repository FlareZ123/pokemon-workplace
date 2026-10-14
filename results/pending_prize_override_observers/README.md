# Rule-backed per-card Prize destination choice preserves hidden-state evidence

## Why the bridge exists

A two-Prize Knock Out can trigger both Barbaracle Lost Block and Billowing Smoke. Official Japanese Pokémon TCG Q&A explicitly permits the Prize-taking player to see the taken Prize cards and select, for each individual card, whether the applicable replacement sends it to the Lost Zone or the discard pile. The choices can differ within one award.

The existing `tools/prize_destination_overrides.py` models this per-card decision correctly, and `tools/physical_pending_prize_batch_bridge.py` models the physical identity and observer information state correctly. `tools/pending_prize_override_observer_bridge.py` composes the two without requiring a caller to hand-translate the decision into a destination move.

## Mechanics

`resolve_pending_override_with_observers(state, overrides, actor_id, group_by_card_class, chosen_effect_id=...)` first resolves replacement applicability and the chosen effect.

- When all applicable effects agree on a destination, it advances exactly one queued Prize card.
- When effects conflict and the caller has supplied no legal choice, it returns a pending `PrizeDestinationDecision` while leaving the card in the same physical `prize_pending` queue and preserving the observer beliefs.
- When a legal effect is chosen, it moves exactly that queued physical instance into hand, discard, or Lost Zone and conditions each observer using the actual destination visibility. Every subsequent card can receive a separate choice.

The caller remains responsible for ensuring chooser authority. The specific Lost Block + Billowing Smoke case is grounded in a Japanese official card Q&A. A generic rule granting the same choice for unrelated replacement conflicts is deliberately not asserted.

## Exact regression

The [reproducer](reproduce.py) uses a two-world correlated top/Prize belief, with two Prize identities B and X in the actual state. It verifies:

1. A missing choice under a conflict changes neither physical state nor beliefs.
2. One Prize goes to private hand and leaves the opponent at P(top=A)=1/2; the next card is publicly sent to Lost Zone and the opponent updates to P(top=A)=1.
3. The same two-Prize award can send B to discard and X to Lost Zone, or reverse those destinations, without losing exact card instances.
4. Unknown effects, unavailable observer IDs, and an empty queue are rejected.

The result closes an integration gap in the Prize-state research. Its outcomes are exact constrained belief transitions, with no estimates of live-game frequency or match-winning value.

## Sources and reproducibility

- [Earlier official-ruling-backed replacement study](../prize_destination_override_conflicts/) includes Japanese Q&A references.
- [Batch latent identity model](../pending_prize_batch_correlation/) explains why immediate marginalization is invalid.
- [E-31 public/hidden destination study](../pending_prize_before_hand_visibility/) checks the before-hand boundary.
- Run the deterministic test via `python results/pending_prize_override_observers/reproduce.py`. CI workflow: `.github/workflows/validate-pending-prize-override-observers.yml`.
