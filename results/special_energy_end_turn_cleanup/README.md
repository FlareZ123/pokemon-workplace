# Special Energy end-of-turn cleanup

## Question

Which effectively legal Special Energy cards discard themselves at the end of a
turn, and what state is required to execute that cleanup without losing
physical-card identity?

## Card-pool audit

The repository card pool contains exactly **4 print rows across 3 names** with
explicit end-of-turn self-discard wording:

- Double Aqua Energy `dc1-33`;
- Double Magma Energy `dc1-34`;
- Triple Acceleration Energy `sm10-190`;
- Triple Acceleration Energy `sm10-234`.

`tools/special_energy_end_turn_catalog.py` rebuilds that set from the effective
paper Expanded card pool.

The timing predicates differ. Triple Acceleration Energy says to discard the
card at the end of the turn while it is attached. Double Aqua and Double Magma
Energy say to discard the card at the end of the turn **you attached it**.
Those two cards therefore require physical attachment-turn provenance.

## Conserved cleanup

`tools/special_energy_end_turn_cleanup.py` executes only after the canonical
`TurnActionBudget` reports that the turn has ended.

For each applicable physical Energy instance, cleanup:

1. removes the attachment from its current holder;
2. moves its card-class count from `attached` to `discard`;
3. removes its materialized attachment-index entry.

Triple Acceleration Energy needs no attachment-turn flag. Double Aqua and
Double Magma are cleaned only when their exact instance ID appears in the
caller's `attached_this_turn_ids` set.

## Regression

The regression validates the four-print runtime registry against the rebuilt
catalog and checks:

- cleanup is unavailable while the ordinary turn is still open;
- Triple Acceleration Energy self-discards after the turn ends;
- Double Aqua and Double Magma self-discard when their physical instance is
  marked as attached during that turn;
- a Double Aqua instance without that provenance is preserved;
- an unknown print is preserved.

## State-modeling implication

Physical identity alone is insufficient for every Energy rule. Some card text
depends on **event provenance**.

For Double Aqua and Double Magma, the question at the end of the turn is not
merely whether the card is attached. The model also needs to know whether that
physical instance was attached during the current turn.

A stronger turn engine should therefore carry attachment-event provenance until
the end-turn boundary and clear it when the next turn begins.

## Scope

This result handles the four Special Energy prints found by the current
card-pool audit. It does not model arbitrary end-of-turn effects on Pokemon,
Tools, Stadiums, attack effects, or Abilities.

The cleanup is intentionally downstream of ordinary action closure. It does not
decide whether the turn ended by attack or by voluntary end.
