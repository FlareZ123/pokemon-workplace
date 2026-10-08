# Canonical destination signatures for terminal Knock Out states

## Research question

After a fixed Knock Out batch has been prepared and a fixed survivor promotion chosen, can a program predict when two different destination vectors will produce the same complete conserved terminal state **without executing each disposal**?

For this narrow destination-only model, yes. The relevant invariant is the multiset of `(card_class, resolved_zone)` for all knocked-out Pokémon stack cards and their attachments, with omitted routes defaulting to discard.

The reusable function `tools/ko_order_zone_signature.py::terminal_zone_signature` builds the sparse sorted histogram of those pairs from materialized instance IDs. Card classes come directly from the existing `IdentityLedger`, preserving the repository's chosen print/functional-equivalence resolution.

## Why it works

The fixed pending state includes one complete materialized representation of every removed card. KO disposal converts each removed instance into the exchangeable count of its card class in its chosen destination. Every surviving materialized instance, existing non-board exchangeable count, promotion choice, and surviving Pokémon remains the same across compared routes.

Therefore, if two valid destination mappings have the same histogram, their complete terminal `StackBoardMaterialState` instances are equal. Conversely, a difference in the histogram produces a difference in final exchangeable counts, so their complete terminal states cannot be equal. This is a conditional equivalence theorem for the existing `discard_pending_with_zone_routes` kernel.

## Witness and validation

Two attached Basic Water Energy copies provide a minimal example. The route pairs
`water-1 -> hand, water-2 -> discard` and
`water-1 -> discard, water-2 -> hand`
differ by physical instance ID. They have the same histogram: one `basic-water` in hand, one in discard. Their full conserved terminal states are identical.

By contrast, the existing Aegislash-return and Lost City-like destination programs have different histograms and different terminal states.

The reproducer runs 220 deterministic random destination assignments for the existing Honedge/Doublade/Aegislash plus attached Energy and Tool board. It independently disposes each assignment using the prior physical conservation kernel, checks class totals, and asserts an exact correspondence between histogram equality and complete terminal-state equality. It also rejects routes outside the pending KO batch or into board-bound zones.

## Scope

The theorem requires a **fixed pending KO batch**, the **same promotion**, the **same original ledger**, and route-only effects with no additional board changes, triggered effects, observation, or persistent copy-specific consequences. It does not decide which effects actually activate or who may choose the order.

This provides a possible optimization for `ko_order_terminal_projection.py`: coalesce route classes by cheap signatures, then execute one full physical disposal per distinct signature. The reduction is sound within the assumptions above.
