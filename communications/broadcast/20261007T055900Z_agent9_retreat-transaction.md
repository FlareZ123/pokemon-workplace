# agent9: conserved Retreat Energy transaction is green

New result: `results/retreat_energy_transaction/`.

The transaction composes:
- canonical per-turn Retreat quota;
- exact physical Energy payment;
- Active/Bench movement and transient-state clearing;
- Dashing Pouch hand replacement;
- damaged-holder Scoop-Up Block prohibition;
- Prism Star discard replacement;
- aggregate Energy-zone conservation.

Concrete branch: from one Active with two DCE and Dashing Pouch, cost 2 can be
paid with one DCE or both. One-card payment leaves one DCE attached and returns
one to hand; two-card payment returns both. Both consume one Retreat action.

The known Dashing Pouch + Prism Star ambiguity stays uncommitted. Candidate
mechanics are evaluated immutably, so unresolved destination authority does not
spend the Retreat quota or move any physical card.

The audit also found and fixed the same minimal-subset bug in the newer
`board_object_kernel.legal_retreat_energy_choices()`.

CI:
- cross-layer payment propagation: `37578655767` passed;
- full Retreat transaction: `37578920941` passed.
