# Board-derived Scoop-Up Block for Retreat

## Question

The conserved Retreat transaction previously accepted an upstream boolean saying
whether the opponent's Scoop-Up Block was active. Can that destination
prohibition be derived from the opponent's represented board instead?

## Result

Yes, for the exact current paper Expanded source represented by the card pool.

The current card database contains one Ability named `Scoop-Up Block`:
Mr. Mime `sm9-66`. Its effect prevents an opponent's damaged Pokemon, and
cards attached to those Pokemon, from being put into that opponent's hand.

`tools/retreat_board_effects.py` now keeps an explicit exact-print registry and
derives active source object IDs from the opponent's `BoardState`. A source
counts only when:

- the physical board object is Mr. Mime `sm9-66`;
- it is in play, either Active or Benched;
- its represented `abilities_enabled` state is true.

The Ability text is not position-gated, so Bench residency remains active. The
existing destination analyzer still applies the holder condition separately:
Scoop-Up Block only removes Dashing Pouch's hand route when the Retreating
Pokemon has damage counters.

## Conserved transaction witness

The regression starts with a damaged Active Pokemon holding Dashing Pouch and
one Double Colorless Energy. Retreat Cost 2 is paid by that physical DCE card.

With an enabled Mr. Mime `sm9-66` on the opponent's Bench:

- the exact source is derived from the board;
- Dashing Pouch's hand destination is prohibited;
- the DCE enters discard;
- the Retreat transaction commits normally.

The same source works from the opponent's Active Spot.

If that Mr. Mime has `abilities_enabled=False`, the source disappears and the
DCE returns to hand through Dashing Pouch. A different Mr. Mime print ID is not
silently treated as Scoop-Up Block. With an undamaged holder, the exact source
is still active but does not prohibit the hand route.

## Architectural implication

The low-level destination analyzer still accepts a boolean because it is useful
as a mechanical primitive. Higher-level execution no longer needs to invent
that boolean for this effect: it can preserve source identity and derive the
prohibition from board state.

This is a useful pattern for continuous effects. A simulator should prefer:

`physical source -> applicability/suppression -> derived effect -> transaction`

over storing free-floating booleans that can outlive the source that created
them.

## Limits

This bridge is deliberately source-authorized rather than name-heuristic. If a
future legal reprint gains the same Ability, its exact print must be added to
the registry.

`abilities_enabled` is already-resolved board state. Deriving global Ability
suppression, owner scope, and source-specific suppression from the wider lock
matrix remains upstream.
