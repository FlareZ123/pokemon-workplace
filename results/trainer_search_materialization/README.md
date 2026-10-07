# Typed Trainer search payload materialization

## Question

Can the exact physical target-cost witness produced by the typed Trainer search planner be executed against the repository's conserved zone ledger, so a successful search changes actual card zones instead of ending at abstract connector feasibility?

Yes, for the current conservative compiled Trainer-search semantic island.

Implementation: `tools/trainer_search_materialization.py`  
Reproducer: `results/trainer_search_materialization/reproduce.py`

## Destination audit

The existing compiler emits 40 Expanded print profiles across 16 unique names. The reproducer re-reads every compiled print from the bundled card database and verifies that its literal search wording sends the searched card or cards from the deck into the player's hand. Conditional profiles such as Guzma & Hala and Sabrina & Brycen also use `in this way`, inheriting the same revealed deck-to-hand search procedure.

This audit is the reason the new executor can safely use a fixed `deck -> hand` destination for this specific compiler island. It does not generalize arbitrary search text. Effects such as Artazon or Dream Ball have different destinations and remain outside this module.

## Representation

The typed state adapter already appends one resource dimension per physical target group. Each `ResourceActionProfile.cost` therefore contains:

1. ordinary state-resource costs, currently discard capacity, Supporter plays, and Stadium plays;
2. an exact target-count slice aligned with the target groups supplied to the adapter.

`trainer_search_materialization.py` preserves that witness. A `SearchTargetBinding` maps each target resource to one exchangeable card-class key in `IdentityLedger`. Execution verifies that the action belongs to the adaptation, verifies exact resource ordering, rejects duplicate class bindings, and moves only the selected target counts from `deck` to `hand` through `ZoneCountState.move()`.

Off-board searched copies remain exchangeable. Stable per-copy instance identity is deferred until a later relation such as an evolution stack, board object, or attachment makes it necessary.

## Secret Box witness

The regression uses one exact print each of:

- Quick Ball (`swsh1-179`);
- Float Stone (`xy8-137`);
- Boss's Orders (`swsh2-154`);
- Artazon (`sv2-171`).

The existing typed planner produces an exact four-channel Secret Box witness when the three-card discard gate is represented as payable. The new physical executor consumes the witness's four target dimensions and moves exactly those four card classes from deck to hand. Every card-class total is conserved.

This transition does not identify the three discarded payment cards. Discard-capacity planning and exact discard-card identity remain separate layers.

## Multi-copy depletion witness

A second regression gives two Arven copies two remaining Supporter plays and a physical pool of two Quick Ball copies. The resource solver uses Arven twice to satisfy a two-Item demand. Executing that witness moves exactly two Quick Balls from deck to hand.

The same witness is then applied to a stale ledger where those copies are already in hand. Execution raises instead of recreating them. Target availability proved in one state therefore cannot be reused after the physical state has changed.

## Finding

Typed search allocation can now cross into the physical state without introducing a second source of target-selection truth.

The target-cost vector serves as both:

- the planner's capacity payment;
- the executor's exact class-level zone-movement witness.

That gives later Bench, Tool, Energy, Stadium, Supporter, and attack transitions access to cards that were actually searched rather than cards that exist only as satisfied demand units.

## Limits

The module materializes only searched payloads. It does not yet physically execute:

- the Trainer card leaving hand and entering its post-resolution zone;
- exact discard-cost identities for Secret Box, Guzma & Hala, Sabrina & Brycen, or Larry's Skill;
- Supporter or Stadium action-window mutation;
- the deck shuffle or observer-relative information update caused by a public reveal;
- search effects whose destination is Bench, discard, attached, Prize, or another zone.

Those operations need their own validated witnesses. In particular, a scalar discard-capacity cost cannot be converted into exact discarded cards without a provenance-aware discard-selection layer.

## Next useful work

The next integration step is to couple this target movement with a concrete physical play transaction for the Trainer itself and exact discard-payment witnesses. That would allow a whole compiled Trainer action to execute atomically over the conserved physical state while preserving current action-budget and information-state semantics.
